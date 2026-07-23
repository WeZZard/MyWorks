# Seed Library

Tools for downloading artwork images to use as seeds in the cover-image skill.

## Tools

### `fetch.py`

Downloads one artwork image through a multi-source fallback chain:

1. **Global cache** (`~/.pi/artwork-cache/`) — instant, no network
2. **Wikimedia Commons** — search + artist/work verification (edit distance + ASCII-normalized fuzzy match)
3. **Google Art Project** — `dezoomify-rs` tile stitching (limited to 1024px width, PNG output → sips conversion)
4. **Metropolitan Museum of Art** — public API, CC0, no key needed
5. **Art Institute of Chicago** — public API, no key needed
6. **Rijksmuseum** — API, requires `RIJKSMUSEUM_API_KEY`
7. **Smithsonian Open Access** — API, requires `SMITHSONIAN_API_KEY`

Each source verifies the artist name and work title against the result before downloading. Large images (>1MB) are auto-downscaled to 512px via `sips` (macOS) or ImageMagick.

#### Single mode

```bash
python3 fetch.py <out.jpg> \
  --artist "Bridget Riley" \
  --work "Movement in Squares" \
  [--wm-query "Bridget Riley Movement in Squares"] \
  [--gap-url "https://artsandculture.google.com/asset/..."]
```

#### Batch mode (concurrent, rate-limited)

```bash
python3 fetch.py --batch <batch.json>
```

`batch.json` format:

```json
[
  {
    "out": "/path/to/output.jpg",
    "artist": "Artist Name",
    "work": "Work Title",
    "wm_query": "Artist Work (optional, defaults to 'Artist Work')",
    "gap_url": "https://artsandculture.google.com/asset/... (optional)"
  }
]
```

### `palette.py`

Extracts the dominant color palette from an image as JSON `[{hex, ratio}]`.

```bash
python3 palette.py <image.jpg> [n_colors]
```

### `recall.py`

Recalls cached seed images by style, opens a gallery, or outputs provenance JSON.

```bash
python3 recall.py <style> [--json] [--gallery] [--refresh]
```

### `setup.zsh`

Downloads the `dezoomify-rs` binary for Google Art Project support.

```bash
zsh setup.zsh
```

## Optional API Keys

Some fallback sources require a free API key. Set them as environment variables to activate those sources. Without a key, the source is silently skipped.

### Rijksmuseum

1. Register at <https://data.rijksmuseum.nl/>
2. Get your API key from the registration page
3. Set the environment variable:

```bash
export RIJKSMUSEUM_API_KEY="your-key-here"
```

Or add to `~/.config/zsh/secrets.zsh` (sourced from `~/.zshrc`):

```zsh
export RIJKSMUSEUM_API_KEY="your-key-here"
```

### Smithsonian Open Access

1. Register at <https://api.si.edu/>
2. Get your API key
3. Set the environment variable:

```bash
export SMITHSONIAN_API_KEY="your-key-here"
```

Or add to `~/.config/zsh/secrets.zsh`.

### Verifying keys are active

```bash
# With key set — Rijksmuseum source will be tried
RIJKSMUSEUM_API_KEY="test" python3 fetch.py /tmp/test.jpg --artist "Rembrandt" --work "Night Watch"

# Without key — Rijksmuseum source is silently skipped
python3 fetch.py /tmp/test.jpg --artist "Rembrandt" --work "Night Watch"
```

## Global Cache

Downloaded artworks are cached at `~/.pi/artwork-cache/`:

```
~/.pi/artwork-cache/
  <artist>-<work>.jpg          # downscaled image (≤512px)
  <artist>-<work>.meta.json    # source, URL, cache time
```

Cache key is `normalized-artist_normalized-work` (ASCII-lowercased, spaces→dashes). Second request for the same artwork returns instantly from cache.

To clear the cache:

```bash
rm -rf ~/.pi/artwork-cache/
```

## Sources Reference

| Source | URL | Auth | License | Notes |
|--------|-----|------|---------|-------|
| Global cache | `~/.pi/artwork-cache/` | None | — | First priority, instant |
| Wikimedia Commons | `commons.wikimedia.org` | None | Varies per file | Search + verification |
| Google Art Project | `artsandculture.google.com` | None | Varies | `dezoomify-rs` tile stitching |
| Met Museum | `collectionapi.metmuseum.org` | None | CC0 | Large public-domain collection |
| Art Institute of Chicago | `api.artic.edu` | None | Public domain | IIIF image delivery |
| Rijksmuseum | `data.rijksmuseum.nl` | API key | Public domain | High-quality images |
| Smithsonian | `api.si.edu` | API key | CC0 | Multiple museums aggregated |