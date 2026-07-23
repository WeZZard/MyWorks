#!/usr/bin/env python3
"""Cover safe-crop candidate generation (Part 1, deterministic, SAM 2).

For a wide cover image, find candidate 1:1 square crops that are most likely
to contain a complete visual semantic, and crop each to a file for the VLM
verifier (Part 2) to judge.

Pipeline:
  1. SAM 2 automatic mask generation -> significant region masks + bboxes.
  2. Enumerate candidate squares (left / center / right / free) of side = H.
  3. Score each by the fraction of significant-region area it contains.
  4. Crop each candidate to .crops/ and emit JSON ordered best-first.

Usage:
    .pi/scripts/cover-crop/.venv/bin/python .pi/scripts/cover-crop/cover-crop-safety-check.py <cover.png> [--top N] [--side H] [--out-dir DIR]

Environment:
    Requires the SAM 2 venv from setup.zsh. Run via:
      .pi/scripts/cover-crop/.venv/bin/python .pi/scripts/cover-crop/cover-crop-safety-check.py <cover>
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
DEFAULT_CKPT = HERE / "checkpoints" / "sam2_hiera_large.pt"
# SAM 2 config name shipped inside the sam2 package.
DEFAULT_CFG = "configs/sam2/sam2_hiera_l.yaml"
MIN_AREA_FRAC = 0.001  # drop masks smaller than 0.1% of the image area
MIN_KEEP = 8          # always keep the top-N masks by area, even below the floor


def pick_device():
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def load_predictor(cfg, ckpt):
    from sam2.build_sam import build_sam2
    device = pick_device()
    try:
        return build_sam2(cfg, str(ckpt), device=device), device
    except Exception as e:
        print(f">> MPS build failed ({e}); retrying on CPU", file=sys.stderr)
        return build_sam2(cfg, str(ckpt), device="cpu"), "cpu"


def significant_masks(masks, img_area):
    scored = []
    for m in masks:
        area = int(m["area"])
        x, y, w, h = m["bbox"]
        scored.append({"bbox": (int(x), int(y), int(w), int(h)), "area": area,
                       "cx": int(x) + int(w) / 2, "cy": int(y) + int(h) / 2})
    scored.sort(key=lambda m: m["area"], reverse=True)
    above_floor = [m for m in scored if m["area"] >= MIN_AREA_FRAC * img_area]
    if len(above_floor) >= 3:
        return above_floor
    # minimalist line-art covers: no large filled blob, so keep the top-N instead
    return scored[:MIN_KEEP]


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def contained_area(square, masks_xyxy, area_per_mask):
    """Sum of mask area whose bbox is fully inside the square; partial if split."""
    sx, sy, side = square
    total = 0
    for (x1, y1, x2, y2), a in zip(masks_xyxy, area_per_mask):
        ix1 = max(x1, sx); iy1 = max(y1, sy)
        ix2 = min(x2, sx + side); iy2 = min(y2, sy + side)
        if ix2 <= ix1 or iy2 <= iy1:
            continue
        # approximate contained fraction by bbox intersection over bbox area
        inter = (ix2 - ix1) * (iy2 - iy1)
        bbox_area = max(1, (x2 - x1) * (y2 - y1))
        total += a * (inter / bbox_area)
    return total


def candidates(W, H, masks):
    side = min(W, H)          # 1:1 share crop
    side = int(side)
    x_max = W - side
    masks_xyxy = [(x, y, x + w, y + h) for (x, y, w, h) in (m["bbox"] for m in masks)]
    areas = [m["area"] for m in masks]
    total_area = sum(areas) or 1

    def square(x):
        return (clamp(int(x), 0, x_max), 0, side)

    cands = {}
    cands["left"] = square(0)
    cands["center"] = square(x_max / 2)
    cands["right"] = square(x_max)

    if masks:
        # free: center on the union bbox of all significant regions
        xs1 = min(m["bbox"][0] for m in masks)
        ys1 = min(m["bbox"][1] for m in masks)
        xs2 = max(m["bbox"][0] + m["bbox"][2] for m in masks)
        ys2 = max(m["bbox"][1] + m["bbox"][3] for m in masks)
        ucx = (xs1 + xs2) / 2
        cands["free-union"] = square(ucx - side / 2)
        # free: center on the single largest region
        big = max(masks, key=lambda m: m["area"])
        cands["free-largest"] = square(big["cx"] - side / 2)
        # free: best window by contained area (coarse scan)
        best_x, best_score = 0, -1.0
        for x in range(0, x_max + 1, max(1, x_max // 40)):
            s = contained_area((x, 0, side), masks_xyxy, areas)
            if s > best_score:
                best_score, best_x = s, x
        cands["free-best"] = square(best_x)

    scored = []
    for name, sq in cands.items():
        score = contained_area(sq, masks_xyxy, areas) / total_area
        scored.append({"id": name, "square": sq, "score": round(float(score), 4)})
    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored, side


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cover", type=Path)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--side", type=int, default=None, help="override square side")
    ap.add_argument("--out-dir", type=Path, default=HERE / ".crops")
    ap.add_argument("--ckpt", type=Path, default=DEFAULT_CKPT)
    ap.add_argument("--cfg", type=str, default=DEFAULT_CFG)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not args.ckpt.exists():
        print(f"checkpoint not found: {args.ckpt}\nrun: zsh scripts/cover-crop/setup.zsh", file=sys.stderr)
        sys.exit(2)

    img = np.array(Image.open(args.cover).convert("RGB"))
    H, W = img.shape[:2]

    print(f">> loading SAM 2 ({os.path.basename(args.cfg)}) on {pick_device()}", file=sys.stderr)
    sam2, device = load_predictor(args.cfg, args.ckpt)

    from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
    mg = SAM2AutomaticMaskGenerator(sam2)
    print(">> generating masks…", file=sys.stderr)
    raw = mg.generate(img)
    print(f">> {len(raw)} raw masks", file=sys.stderr)

    masks = significant_masks(raw, W * H)
    print(f">> {len(masks)} significant masks", file=sys.stderr)
    for m in masks:
        print(f"   bbox={m['bbox']} area={m['area']}", file=sys.stderr)

    scored, side = candidates(W, H, masks)
    if args.side:
        side = args.side
    top = scored[:args.top]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    base = args.cover.stem
    out = []
    for c in top:
        x, y, s = c["square"]
        crop_path = args.out_dir / f"{base}-{c['id']}.png"
        Image.open(args.cover).convert("RGB").crop((x, y, x + s, y + s)).save(crop_path)
        out.append({"id": c["id"], "coords": c["square"], "score": c["score"],
                    "crop": str(crop_path)})

    payload = {"original": str(args.cover), "device": device,
               "image_size": [W, H], "square_side": side,
               "significant_masks": len(masks), "candidates": out}
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else
          json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()