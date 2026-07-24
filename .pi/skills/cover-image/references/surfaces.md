# Surface Registry

A **surface** is a target use for a cover image. Each surface fixes the canvas config — aspect ratio, safe area, bleed, text rules, crop behavior, and filename — so the pipeline can run without knowing anything about "platforms" beyond this table. The skill reads this registry to offer the surface choice and to load each surface's detail file.

## Schema

Every surface has:

- `id` — stable key.
- `label` — the string shown to the user in the surface choice.
- `aspectRatio` — canvas ratio (e.g. `5:2`, `2.35:1`, `3:4`, `1:1`).
- `safeArea` — the region critical content must survive in, so the surface's crop never eats it:
  - `shape`: `full` (the whole canvas) | `center-square` (a centered 1:1).
- `bleed` — whether the composition extends to the canvas trim:
  - `full` — content runs to all four edges (no margin frame).
  - `none` — content stays inside the safe area; margins around it.
- `text` — `required` | `optional` | `none`.
- `cropBehavior` — what crop the surface applies on feed/share.
- `filename` — output filename.
- `detail` — path to the per-surface detail file (composition rules for the generation prompt and the final checks).

## Registry

| id | label | aspectRatio | safeArea | bleed | text | cropBehavior | filename | detail |
|---|---|---|---|---|---|---|---|---|
| x-article | X Article Cover | 5:2 | full | full | required | feed center-crops 5:2 | cover-image-x-article.png | surfaces/x-article.md |
| wechat-headline | 微信公众号头条 | 2.35:1 | center-square | none | none | center 1:1 share crop | cover-image-wmp.png | surfaces/wechat-headline.md |
| wechat-image-message | 微信公众号图片消息(小绿书) | 3:4 | full | full | none | feed 3:4 | cover-image-wmp-image-message.png | surfaces/wechat-image-message.md |
| xiaohongshu | 小红书 | 3:4 | full | full | optional | feed 3:4 | cover-image-xhs.png | surfaces/xiaohongshu.md |
| square | 1:1 | 1:1 | full | full | optional | none | cover-image-1x1.png | surfaces/square.md |
| 4x3 | 4:3 | 4:3 | full | full | optional | none | cover-image-4x3.png | surfaces/4x3.md |
| 9x16 | 9:16 | 9:16 | full | full | optional | none | cover-image-9x16.png | surfaces/9x16.md |
| 16x9 | 16:9 | 16:9 | full | full | optional | none | cover-image-16x9.png | surfaces/16x9.md |

## How the skill uses this

1. If the user did not name a surface, ask once which surface, listing the `label` column. Cache the choice in the session (it stays in the transcript as a user message; no file needed).
2. Look up the row by `id`. Read `detail` for the composition rules.
3. Pass a **surface constraint** — `aspectRatio` + `safeArea` + `bleed` + `text` + `cropBehavior` — into the layout-planner, layout-generator, and prompt-composer.
4. After generation, the final-checks-verifier reads the detail file.

## Notes on the six generic / new surfaces

`wechat-image-message`, `xiaohongshu`, `square`, `4x3`, `9x16`, `16x9` ship with default rules (full-bleed, `safeArea: full`, text optional/none, no platform crop). Refine each one's detail file when it is first used for real output.