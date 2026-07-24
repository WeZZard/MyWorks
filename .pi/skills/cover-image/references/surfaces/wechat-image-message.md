# Surface: 微信公众号图片消息(小绿书)

WeChat's image-message format — the 小红书-style vertical card. Defaults below; refine on first real use.

## Config

- `aspectRatio`: 3:4 (e.g. 1080×1440)
- `safeArea`: full — the feed shows the full 3:4. (Refine: confirm whether a center 1:1 share crop applies, and switch `safeArea` to `center-square` if it does.)
- `bleed`: full — the image fills the card to all edges.
- `text`: none — WeChat renders the title as text in its UI.
- `cropBehavior`: feed shows the full 3:4.
- `filename`: cover-image-wmp-image-message.png

## Elements

- Rhetoric only, no text.

## Generation

- One 3:4 vertical image: style **visual language** + rhetoric, full-bleed. Keep the rhetoric readable at card size.
- Save as `cover-image-wmp-image-message.png` in the output directory.