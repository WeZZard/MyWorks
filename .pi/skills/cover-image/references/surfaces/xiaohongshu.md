# Surface: 小红书

小红书 note cover. Defaults below; refine on first real use.

## Config

- `aspectRatio`: 3:4 (e.g. 1080×1440) — the feed's primary ratio; largest screen share.
- `safeArea`: full — the feed shows the full 3:4. (Refine: add a top/bottom safe band if 小红书 overlays UI elements over the cover.)
- `bleed`: full — the image fills to all edges.
- `text`: optional — overlay titles are common on 小红书; add a title only when the article's title reads as a cover line.
- `cropBehavior`: feed shows the full 3:4; the first image is the cover.
- `filename`: cover-image-xhs.png

## Elements

- Rhetoric, centered or full-bleed per the style.
- Title optional; if used, keep it to the title's 2–6 words and keep it readable at thumbnail size.

## Generation

- One 3:4 vertical image: style **visual language** + rhetoric, full-bleed. Add a title overlay only when the surface choice explicitly asks for text.
- Save as `cover-image-xhs.png` in the output directory.