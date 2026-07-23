#!/usr/bin/env python3
"""Deterministic palette extraction from an image — the color "interpolated value".

Outputs the dominant colors and their ratios as JSON: [{"hex": "#rrggbb", "ratio": 0.xx}, ...]
sorted by ratio. This is the exact color distribution of the artwork, used as the
generation color seed (no vision model needed for color ratios).

Usage:
    python3 palette.py <image> [n]      # n = number of palette colors (default 6)
"""
import json
import sys
from collections import Counter

from PIL import Image


def palette(path, n=6):
    im = Image.open(path).convert("RGB")
    # downscale so dominant colors are stable and fast
    im = im.resize((160, 160), Image.LANCZOS)
    q = im.quantize(colors=n, method=Image.Quantize.MEDIANCUT).convert("RGB")
    cnt = Counter(q.getdata())
    total = sum(cnt.values())
    out = []
    for (r, g, b), c in cnt.most_common(n):
        out.append({"hex": f"#{r:02x}{g:02x}{b:02x}", "ratio": round(c / total, 3)})
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: palette.py <image> [n]", file=sys.stderr)
        sys.exit(2)
    p = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    print(json.dumps(palette(p, n), ensure_ascii=False, indent=2))