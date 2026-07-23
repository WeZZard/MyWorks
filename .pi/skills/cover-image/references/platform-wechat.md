# Platform: WeChat Public Account

WeChat shows the cover on three surfaces, all served by one file. The design centers the visual so every surface crops to a complete image.

## Artifact (one)

- File: `cover-image-wmp.png`
- Aspect ratio: 2.35:1 (e.g., 900×383)
- Design: **centered visual, NO text.** The visual rhetoric figure sits at the visual center.

## Surfaces (all from this one file)

1. **Message-list 头条** — the full 2.35:1 banner.
2. **Third-party share** (sharing the article URL off WeChat) — the **center 1:1 square** crop.
3. **WeChat in-app share** (forwarding to friends / 朋友圈) — the **center 1:1 square** crop.

The center 1:1 square is the share card. It must be a complete, self-contained visual: the rhetoric fully inside, uncropped. Put the rhetoric at the center so the center crop captures it whole. WeChat renders the article title as text in the UI, so no title text is needed on the image.

## Why no separate share file

The share card is the center of the 头条, not a separate upload. One file covers all three surfaces. Do not create a `cover-image-wmp-share.png`.

## Elements

- Rhetoric only (centered), no text.

## Generation

- One image: a 2.35:1 centered-visual banner — style **visual language** only, rhetoric centered, no text. The center 1:1 square must be a complete visual.
- Save as `cover-image-wmp.png` in the post directory.

## Preflight

- Check the center 1:1 square is a complete visual (SAM + VLM). This single check covers the share card.