#!/usr/bin/env python3
"""Fetch artwork images with robustness: global cache, multi-source fallback chain, concurrent batch, rate limiting, retry, large-image handling.

Sources (fallback order):
  1. Global cache (~/.pi/artwork-cache/) — instant, no network
  2. Wikimedia Commons — search + artist/work verification
  3. Google Art Project — dezoomify-rs (limited to 1024px width)
  4. Metropolitan Museum of Art — public API, CC0, no key needed
  5. Art Institute of Chicago — public API, no key needed
  6. Rijksmuseum — API, needs RIJKSMUSEUM_API_KEY env var
  7. Smithsonian — API, needs SMITHSONIAN_API_KEY env var

Single mode:
    fetch.py <out.jpg> --artist "Name" --work "Title" [--wm-query Q] [--gap-url URL]

Batch mode (concurrent, rate-limited):
    fetch.py --batch <batch.json>

Config (optional env vars):
    RIJKSMUSEUM_API_KEY  — free key from https://data.rijksmuseum.nl/
    SMITHSONIAN_API_KEY   — free key from https://api.si.edu/
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.parse
import random
import shutil
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
DZ = os.path.join(HERE, "dezoomify-rs")

CACHE_DIR = os.path.expanduser("~/.pi/artwork-cache")

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Mac; Intel Mac OS X 10_15_7; rv:121.0) Gecko/20100101 Firefox/121.0",
]

_last_request_time = {}
MIN_DELAY = 0.5
MAX_RETRIES = 3
GAP_TIMEOUT = 300
MAX_CONCURRENT_GAP = 2


def _ua():
    return random.choice(USER_AGENTS)


def _normalize(s):
    """ASCII-normalize for fuzzy matching (ø→o, é→e, etc.)"""
    import unicodedata
    # Manual replacements for chars that NFKD doesn't decompose (ø, ß, ð, þ, etc.)
    replacements = {"ø": "o", "Ø": "o", "ß": "ss", "ð": "d", "þ": "th", "œ": "oe", "æ": "ae"}
    for k, v in replacements.items():
        s = s.replace(k, v)
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


def _get(url, retry=True):
    from urllib.parse import urlparse
    host = urlparse(url).netloc
    now = time.time()
    if host in _last_request_time:
        elapsed = now - _last_request_time[host]
        if elapsed < MIN_DELAY:
            time.sleep(MIN_DELAY - elapsed)
    _last_request_time[host] = time.time()

    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _ua()})
            return urllib.request.urlopen(req, timeout=60)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wait = (2 ** attempt) + random.uniform(0, 0.5)
                print(f"  rate limited ({e.code}), retrying in {wait:.1f}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            if retry and attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
                continue
            raise
        except Exception as e:
            if retry and attempt < MAX_RETRIES - 1:
                print(f"  network error ({e}), retry {attempt+1}/{MAX_RETRIES}...", file=sys.stderr)
                time.sleep(2 ** attempt)
                continue
            raise
    raise Exception(f"failed after {MAX_RETRIES} retries: {url}")


def _get_json(url):
    return json.load(_get(url))


def _edit_ratio(a, b):
    return SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


def _contains_fuzzy(haystack, needle):
    h = _normalize(haystack)
    n = _normalize(needle)
    if n in h:
        return True
    n_words = set(n.split())
    h_words = set(h.split())
    if len(n_words) >= 2 and len(n_words & h_words) >= len(n_words) * 0.6:
        return True
    return False


# === Cache ===

def _cache_key(artist, work):
    return _normalize(artist).replace(" ", "-") + "_" + _normalize(work).replace(" ", "-")[:60]


def _cache_check(artist, work):
    """Check global cache. Returns cached file path or None."""
    key = _cache_key(artist, work)
    cached = os.path.join(CACHE_DIR, key + ".jpg")
    if os.path.exists(cached) and os.path.getsize(cached) > 1000:
        return cached
    return None


def _cache_store(src, artist, work, source, url):
    """Copy file to global cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = _cache_key(artist, work)
    dst = os.path.join(CACHE_DIR, key + ".jpg")
    shutil.copy2(src, dst)
    meta = {"artist": artist, "work": work, "source": source, "url": url, "cached_at": time.time()}
    with open(os.path.join(CACHE_DIR, key + ".meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    return dst


# === Wikimedia ===

def _commons_search(query, limit=5):
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "list": "search", "srsearch": query, "srnamespace": 6, "srlimit": str(limit), "format": "json"})
    hits = _get_json(api)["query"]["search"]
    return [h["title"] for h in hits if h["title"].lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff"))]


def _commons_file_info(file_title):
    ii = _get_json("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "titles": file_title, "prop": "imageinfo", "iiprop": "url", "format": "json"}))
    info = list(ii["query"]["pages"].values())[0].get("imageinfo")
    if not info:
        return None, ""
    img_url = info[0]["url"]
    try:
        pi = _get_json("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
            {"action": "query", "titles": file_title, "prop": "categories|extracts",
             "exlimit": "1", "explaintext": "1", "cllimit": "50", "format": "json"}))
        page = list(pi["query"]["pages"].values())[0]
        extract = page.get("extract", "") or ""
        cats = " ".join(c.get("title", "") for c in page.get("categories", []))
        text = extract + " " + cats
    except Exception:
        text = ""
    return img_url, text


def _verify(file_title, page_text, artist, work, threshold=0.6):
    artist_ok = _contains_fuzzy(page_text, artist) or _contains_fuzzy(file_title, artist)
    file_base = file_title.replace("File:", "").rsplit(".", 1)[0]
    work_ratio = _edit_ratio(work, file_base)
    # work match: edit distance OR fuzzy text OR key-word overlap with file title
    work_ok = work_ratio >= threshold or _contains_fuzzy(page_text, work) or _normalize(work) in _normalize(file_base)
    if not work_ok:
        # Last resort: check if significant words from work appear in file title
        work_words = [w for w in _normalize(work).split() if len(w) > 3]
        file_words = set(_normalize(file_base).split())
        if work_words and sum(1 for w in work_words if w in file_words) >= len(work_words) * 0.6:
            work_ok = True
    return artist_ok and work_ok


def _try_wikimedia(artist, work, wm_query, out):
    if not wm_query:
        return None
    try:
        titles = _commons_search(wm_query, limit=5)
        for t in titles:
            img_url, page_text = _commons_file_info(t)
            if not img_url:
                continue
            ok = _verify(t, page_text, artist, work)
            print(f"  wm candidate: {t} -> verify={ok}", file=sys.stderr)
            if ok:
                if dl_url(img_url, out):
                    _cache_store(out, artist, work, "wikimedia", img_url)
                    return "wikimedia"
        print(f"  all Wikimedia candidates failed", file=sys.stderr)
    except Exception as e:
        print(f"  Wikimedia error: {e}", file=sys.stderr)
    return None


# === Google Art Project ===

def _downscale(dst, max_edge=512):
    if os.path.exists("/usr/bin/sips"):
        try:
            subprocess.run(["sips", "-Z", str(max_edge), dst], capture_output=True, timeout=30, check=True)
            return True
        except Exception:
            pass
    for magick in ["/opt/homebrew/bin/magick", "/usr/local/bin/magick"]:
        if os.path.exists(magick):
            try:
                subprocess.run([magick, "convert", dst, "-resize", f"{max_edge}x{max_edge}>", dst],
                               capture_output=True, timeout=60, check=True)
                return True
            except Exception:
                pass
    try:
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        im = Image.open(dst).convert("RGB")
        w, h = im.size
        m = max(w, h)
        if m > max_edge:
            im = im.resize((int(w * max_edge / m), int(h * max_edge / m)), Image.LANCZOS)
        im.save(dst)
        return True
    except Exception:
        return False


def dl_url(url, dst):
    try:
        data = _get(url).read()
    except Exception as e:
        print(f"  download error: {e}", file=sys.stderr)
        return False
    if len(data) < 1000:
        print(f"  downloaded file too small ({len(data)} bytes)", file=sys.stderr)
        return False
    with open(dst, "wb") as f:
        f.write(data)
    if os.path.getsize(dst) > 1_000_000:
        print(f"  large file ({os.path.getsize(dst)//1024}KB), downscaling...", file=sys.stderr)
        _downscale(dst)
    return True


def _try_gap(gap_url, out):
    if not gap_url or not os.path.exists(DZ):
        return None
    try:
        png_tmp = out + ".gap.png"
        if os.path.exists(png_tmp):
            os.remove(png_tmp)
        print(f"  trying GAP (-w 1024, PNG): {gap_url[:60]}...", file=sys.stderr)
        r = subprocess.run([DZ, "-w", "1024", gap_url, png_tmp], capture_output=True, text=True, timeout=GAP_TIMEOUT)
        if r.returncode == 0 and os.path.exists(png_tmp) and os.path.getsize(png_tmp) > 1000:
            if out.lower().endswith((".jpg", ".jpeg")):
                subprocess.run(["sips", "-s", "format", "jpeg", png_tmp, "--out", out], capture_output=True, timeout=30)
                os.remove(png_tmp)
            else:
                os.rename(png_tmp, out)
            if os.path.exists(out) and os.path.getsize(out) > 1000:
                return "google-art-project"
            if os.path.exists(png_tmp):
                os.remove(png_tmp)
        else:
            err = (r.stderr or r.stdout or "").strip()[-120:]
            print(f"  GAP failed: {err}", file=sys.stderr)
            if os.path.exists(png_tmp):
                os.remove(png_tmp)
    except subprocess.TimeoutExpired:
        print(f"  GAP timed out ({GAP_TIMEOUT}s)", file=sys.stderr)
        if os.path.exists(png_tmp):
            os.remove(png_tmp)
    except Exception as e:
        print(f"  GAP error: {e}", file=sys.stderr)
        if os.path.exists(png_tmp):
            os.remove(png_tmp)
    return None


# === Metropolitan Museum of Art ===

def _try_met(artist, work, out):
    """Search Met Museum public API. CC0, no key needed."""
    try:
        print(f"  trying Met Museum...", file=sys.stderr)
        # Search by artist + title keyword
        query = urllib.parse.quote(f"{artist} {work}")
        search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?artistOrCulture=true&q={urllib.parse.quote(artist)}&title=true&hasImages=true"
        data = _get_json(search_url)
        if data.get("total", 0) == 0:
            print(f"  Met: no results for artist '{artist}'", file=sys.stderr)
            return None
        object_ids = data.get("objectIDs", [])[:5]
        for oid in object_ids:
            obj_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}"
            obj = _get_json(obj_url)
            # Verify artist
            obj_artist = obj.get("artistDisplayName", "")
            obj_title = obj.get("title", "")
            if not _contains_fuzzy(obj_artist, artist) and not _contains_fuzzy(artist, obj_artist):
                continue
            if not _contains_fuzzy(obj_title, work) and not _contains_fuzzy(work, obj_title):
                continue
            # Get primary image
            img_url = obj.get("primaryImage", "") or obj.get("primaryImageSmall", "")
            if not img_url:
                continue
            if dl_url(img_url, out):
                _cache_store(out, artist, work, "met-museum", obj_url)
                return "met-museum"
        print(f"  Met: no matching works found", file=sys.stderr)
    except Exception as e:
        print(f"  Met error: {e}", file=sys.stderr)
    return None


# === Art Institute of Chicago ===

def _try_aic(artist, work, out):
    """Search Art Institute of Chicago API. No key needed."""
    try:
        print(f"  trying Art Institute of Chicago...", file=sys.stderr)
        query = urllib.parse.quote(f"{artist} {work}")
        search_url = f"https://api.artic.edu/api/v1/artworks/search?q={query}&fields=id,title,artist_title,image_id,is_public_domain&limit=5"
        data = _get_json(search_url)
        for art in data.get("data", []):
            obj_artist = art.get("artist_title", "") or ""
            obj_title = art.get("title", "") or ""
            if not _contains_fuzzy(obj_artist, artist) and not _contains_fuzzy(artist, obj_artist):
                continue
            if not _contains_fuzzy(obj_title, work) and not _contains_fuzzy(work, obj_title):
                continue
            image_id = art.get("image_id")
            if not image_id:
                continue
            img_url = f"https://www.artic.edu/iiif/2/{image_id}/full/1024,/0/default.jpg"
            if dl_url(img_url, out):
                _cache_store(out, artist, work, "aic", f"https://api.artic.edu/api/v1/artworks/{art.get('id')}")
                return "aic"
        print(f"  AIC: no matching works found", file=sys.stderr)
    except Exception as e:
        print(f"  AIC error: {e}", file=sys.stderr)
    return None


# === Rijksmuseum ===

def _try_rijks(artist, work, out):
    """Search Rijksmuseum API. Needs RIJKSMUSEUM_API_KEY."""
    key = os.environ.get("RIJKSMUSEUM_API_KEY")
    if not key:
        return None
    try:
        print(f"  trying Rijksmuseum...", file=sys.stderr)
        query = urllib.parse.quote(f"{artist} {work}")
        search_url = f"https://www.rijksmuseum.nl/api/en/collection?key={key}&q={query}&imgonly=true&ps=5&format=json"
        data = _get_json(search_url)
        for item in data.get("artObjects", []):
            obj_artist = item.get("principalOrFirstMaker", "") or ""
            obj_title = item.get("title", "") or ""
            if not _contains_fuzzy(obj_artist, artist) and not _contains_fuzzy(artist, obj_artist):
                continue
            if not _contains_fuzzy(obj_title, work) and not _contains_fuzzy(work, obj_title):
                continue
            img_url = item.get("webImage", {}).get("url")
            if not img_url:
                continue
            if dl_url(img_url, out):
                _cache_store(out, artist, work, "rijksmuseum", item.get("links", {}).get("self", ""))
                return "rijksmuseum"
        print(f"  Rijksmuseum: no matching works found", file=sys.stderr)
    except Exception as e:
        print(f"  Rijksmuseum error: {e}", file=sys.stderr)
    return None


# === Smithsonian ===

def _try_smithsonian(artist, work, out):
    """Search Smithsonian Open Access API. Needs SMITHSONIAN_API_KEY."""
    key = os.environ.get("SMITHSONIAN_API_KEY")
    if not key:
        return None
    try:
        print(f"  trying Smithsonian...", file=sys.stderr)
        query = urllib.parse.quote(f"{artist} {work}")
        search_url = f"https://api.si.edu/openaccess/api/v1.0/content/search?q={query}&api_key={key}&rows=5"
        data = _get_json(search_url)
        for row in data.get("response", {}).get("rows", []):
            content = row.get("content", {}).get("freetext", {})
            obj_artist = " ".join(n.get("content") for n in content.get("name", []))
            obj_title = (content.get("title", [{}])[0].get("content", "") if content.get("title") else "")
            if not _contains_fuzzy(obj_artist, artist) and not _contains_fuzzy(artist, obj_artist):
                continue
            if not _contains_fuzzy(obj_title, work) and not _contains_fuzzy(work, obj_title):
                continue
            # Find image URL in content
            ds = row.get("content", {}).get("descriptiveNonRepeating", {})
            online = ds.get("online_media", {}).get("media", [])
            for media in online:
                for thumb in media.get("thumbnail", []):
                    img_url = thumb.get("content")
                    if img_url and dl_url(img_url, out):
                        _cache_store(out, artist, work, "smithsonian", img_url)
                        return "smithsonian"
        print(f"  Smithsonian: no matching works found", file=sys.stderr)
    except Exception as e:
        print(f"  Smithsonian error: {e}", file=sys.stderr)
    return None


# === Main fetch logic ===

def fetch_one(out, artist, work, wm_query=None, gap_url=None):
    """Download one artwork through the full fallback chain. Returns source name or None."""
    # 1. Check global cache
    cached = _cache_check(artist, work)
    if cached:
        print(f"  cache hit: {cached}", file=sys.stderr)
        shutil.copy2(cached, out)
        # Also copy meta
        key = _cache_key(artist, work)
        return "cache"

    # 2. Wikimedia
    source = _try_wikimedia(artist, work, wm_query, out)
    if source:
        return source

    # 3. Google Art Project
    source = _try_gap(gap_url, out)
    if source:
        _cache_store(out, artist, work, source, gap_url or "")
        return source

    # 4. Met Museum
    source = _try_met(artist, work, out)
    if source:
        return source

    # 5. Art Institute of Chicago
    source = _try_aic(artist, work, out)
    if source:
        return source

    # 6. Rijksmuseum (optional, needs key)
    source = _try_rijks(artist, work, out)
    if source:
        return source

    # 7. Smithsonian (optional, needs key)
    source = _try_smithsonian(artist, work, out)
    if source:
        return source

    return None


def main():
    args = sys.argv[1:]

    # Batch mode
    if "--batch" in args:
        batch_idx = args.index("--batch")
        if batch_idx + 1 >= len(args):
            print("usage: fetch.py --batch <batch.json>", file=sys.stderr)
            sys.exit(2)
        batch_file = args[batch_idx + 1]
        items = json.load(open(batch_file))
        print(f"Batch: {len(items)} artworks", file=sys.stderr)

        results = {}
        with ThreadPoolExecutor(max_workers=max(len(items), 4)) as pool:
            futures = {}
            for item in items:
                fut = pool.submit(fetch_one, item["out"], item["artist"], item["work"],
                                  item.get("wm_query"), item.get("gap_url"))
                futures[fut] = item
            for fut in as_completed(futures):
                item = futures[fut]
                try:
                    source = fut.result()
                    results[os.path.basename(item["out"])] = source
                    print(f"  {os.path.basename(item['out'])}: {source or 'FAILED'}", file=sys.stderr)
                except Exception as e:
                    results[os.path.basename(item["out"])] = None
                    print(f"  {os.path.basename(item['out'])}: ERROR ({e})", file=sys.stderr)

        print(json.dumps(results, indent=2))
        failed = [k for k, v in results.items() if not v]
        if failed:
            print(f"\n{len(failed)} failed: {failed}", file=sys.stderr)
            sys.exit(1)
        return

    # Single mode
    if len(args) < 1:
        print("usage: fetch.py <out.jpg> --artist NAME --work TITLE [--wm-query Q] [--gap-url URL]", file=sys.stderr)
        print("       fetch.py --batch <batch.json>", file=sys.stderr)
        print("env:   RIJKSMUSEUM_API_KEY, SMITHSONIAN_API_KEY (optional)", file=sys.stderr)
        sys.exit(2)
    out = args[0]
    artist = work = wm = gap = None
    for i, a in enumerate(args):
        if a == "--artist" and i + 1 < len(args): artist = args[i + 1]
        if a == "--work" and i + 1 < len(args): work = args[i + 1]
        if a == "--wm-query" and i + 1 < len(args): wm = args[i + 1]
        if a == "--gap-url" and i + 1 < len(args): gap = args[i + 1]
    if not artist or not work:
        print("fetch.py: --artist and --work are required", file=sys.stderr)
        sys.exit(2)
    source = fetch_one(out, artist, work, wm, gap)
    if source:
        print(source)
    else:
        print("failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()