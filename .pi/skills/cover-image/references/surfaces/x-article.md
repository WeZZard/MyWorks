# Surface: X Article Cover

## Config

- `aspectRatio`: 5:2 (e.g. 2000×800)
- `safeArea`: full — the whole canvas is safe; X shows the full 5:2 cover in the article.
- `bleed`: full — the composition extends to all four edges (top, bottom, left, right). No empty margin frame.
- `text`: required — title + subtitle + rhetoric all sit on the banner.
- `cropBehavior`: the feed preview center-crops the 5:2; accepted for X.
- `filename`: cover-image-x-article.png

## Elements (all three on the one banner)

- title — the main title
- subtitle — the kicker / eyebrow
- rhetoric — the visual rhetoric / analogue figure

## Composition

- One full-bleed editorial banner. The style reference's **visual language** (container + rhetoric + breaking line + palette + tone) and **typography** (subtitle + main title + thin bar) both apply, composed together into a single 5:2 banner that bleeds to every edge.
- No safe-square constraint. Do not apply the WeChat center-square rule here.

## Generation

- Generate one 5:2 image: the style's visual language + title + subtitle + rhetoric, full-bleed on all four edges.
- Save as `cover-image-x-article.png` in the output directory.