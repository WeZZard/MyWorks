#!/usr/bin/env python3
"""seed-library recall tool.

Given a visual-style name, recall (download if needed, then print) the local
paths of that style's seed images, with per-image provenance (artist, work,
year, source).

Source policy: try Wikimedia Commons first (a diffusion seed does not need high
resolution, and Commons is stable and direct); on fetch failure, fall back to
Google Art Project (via dezoomify-rs, which has a more complete collection).
The `source` field in the output records which source each image came from.

Usage:
    python3 recall.py <style>                # print one cached path per line
    python3 recall.py <style> --json          # JSON: [{path,id,artist,work,year,source}]
    python3 recall.py <style> --refresh       # re-download even if cached

The cover-image skill calls this to get referencedImagePaths for a style and to
record which artwork each candidate referenced.
"""
import json
import os
import subprocess
import sys
import urllib.request
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "manifest.json")
DZ = os.path.join(HERE, "dezoomify-rs")
CACHE = os.path.join(HERE, "cache")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def _get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40)


def _commons_first_image(query):
    """Search Wikimedia Commons; return the image URL of the first image File: hit, or None."""
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "list": "search", "srsearch": query, "srnamespace": 6, "srlimit": 8, "format": "json"}
    )
    hits = json.load(_get(api))["query"]["search"]
    for h in hits:
        t = h["title"]
        if t.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
            ii = json.load(_get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
                {"action": "query", "titles": t, "prop": "imageinfo", "iiprop": "url", "format": "json"})))
            info = list(ii["query"]["pages"].values())[0].get("imageinfo")
            if info:
                return info[0]["url"]
    return None


def _recall_google_art(url, dst):
    r = subprocess.run([DZ, "-l", url, dst], capture_output=True, text=True)
    return r.returncode == 0 and os.path.exists(dst)


def _recall_wikimedia(query, dst):
    imgurl = _commons_first_image(query)
    if not imgurl:
        return False
    ext = imgurl.rsplit(".", 1)[-1].split("?")[0].lower()
    if ext not in ("jpg", "jpeg", "png"):
        ext = "jpg"
    realdst = dst[:-4] + "." + ext if not dst.lower().endswith(ext) else dst
    with _get(imgurl) as r, open(realdst, "wb") as f:
        f.write(r.read())
    if realdst != dst and os.path.exists(realdst):
        os.replace(realdst, dst) if ext == "jpg" else None
    return os.path.exists(dst)


def main():
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in flags
    refresh = "--refresh" in flags
    if not args:
        print("usage: recall.py <style> [--json] [--refresh]", file=sys.stderr)
        sys.exit(2)
    style = args[0]
    manifest = json.load(open(MANIFEST))
    if style not in manifest:
        print(f"no seeds for style '{style}' in manifest", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(DZ):
        print(f"dezoomify-rs missing at {DZ}; Wikimedia fallback still works (run setup.zsh for the Google Art Project fallback)", file=sys.stderr)
    styledir = os.path.join(CACHE, style)
    os.makedirs(styledir, exist_ok=True)
    out = []
    for entry in manifest[style]:
        dst = os.path.join(styledir, f"{entry['id']}.jpg")
        source = None
        if refresh or not os.path.exists(dst):
            print(f"recalling {entry['id']} ({entry['artist']} — {entry['work']})…", file=sys.stderr)
            if entry.get("wikimedia_query"):
                if _recall_wikimedia(entry["wikimedia_query"], dst):
                    source = "wikimedia"
                else:
                    print(f"  wikimedia failed; falling back to google-art-project", file=sys.stderr)
            if source is None and os.path.exists(DZ) and entry.get("google_art_url"):
                if _recall_google_art(entry["google_art_url"], dst):
                    source = "google-art-project"
        elif os.path.exists(dst):
            source = "cached"
            meta = dst + ".meta.json"
            if os.path.exists(meta):
                try:
                    source = json.load(open(meta)).get("source", "cached")
                except Exception:
                    pass
        if os.path.exists(dst):
            out.append({"path": dst, "id": entry["id"], "artist": entry["artist"],
                        "work": entry["work"], "year": entry.get("year"), "source": source,
                        "view_online": entry.get("google_art_url")})
            if source and source != "cached":
                try:
                    json.dump({"source": source}, open(dst + ".meta.json", "w"))
                except Exception:
                    pass
        else:
            print("  " + entry["id"] + ": both sources failed", file=sys.stderr)
    if "--gallery" in flags:
        rows = "".join(
            f'<figure style="display:inline-block;margin:12px;text-align:center;vertical-align:top">'
            f'<img src="file://{o["path"]}" style="max-height:360px;border:1px solid #333">'
            f'<figcaption><b>{o["artist"]}</b> — {o["work"]} ({o.get("year")}) '
            f'<br><small>[{o["source"]}] '
            f'<a href="{o["view_online"]}">view online</a></small></figcaption></figure>'
            for o in out
        )
        html = f"<!doctype html><meta charset=utf-8><title>seed library: {style}</title>"                f"<body style=background:#111;color:#eee;font-family:sans-serif>"                f"<h2>seed library — {style}</h2>{rows}</body>"
        gp = os.path.join(styledir, "gallery.html")
        open(gp, "w").write(html)
        try:
            subprocess.run(["open", gp])
        except Exception:
            pass
        print(gp)
    elif as_json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for o in out:
            print(o["path"])


if __name__ == "__main__":
    main()