---
name: cover-image-platforms
description: wpw entry point for cover images. Generate cover image(s) for a post on one or more surfaces (X Article, 微信公众号头条/图片消息, 小红书, generic ratios), then run preflight. Delegates generation to the `cover-image` skill from the pi-cover-image package; this shim only maps the post directory to the plugin's inputs, loops over surfaces, and chains preflight.
---

# Cover Image Platforms

The wpw-specific glue over the generic `cover-image` plugin. The plugin takes `article-path` + `surface` + `output-dir` and writes a cover PNG. This shim knows the wpw convention — a post lives in `YYYY-MM-DD-slug/` with `index.md`, covers land in that directory with the surface's filename, and preflight runs after.

## Input

- `post-dir` — the `YYYY-MM-DD-slug/` directory.
- `surfaces` — one or more surface ids from the plugin's `references/surfaces.md` (e.g. `x-article`, `wechat-headline`, `wechat-image-message`, `xiaohongshu`, `square`, `4x3`, `9x16`, `16x9`).

If `post-dir` is missing, ask once. If `surfaces` is missing, ask once which surfaces (list the labels); cache the choice in the session (it stays in the transcript). Do not guess.

## Run directory

Create the cover-image skill's work dir at `.pi/cover-image-work/<post-dir-basename>--<YYYYMMDDTHHMMSS>/`, where the timestamp is **UTC** (`date -u +%Y%m%dT%H%M%S`) with no timezone marker. The post-dir basename already starts with the date, so runs sort chronologically under the post. `.pi/cover-image-work/` is gitignored. Do NOT prefix the run dir with the surface name — the post-dir basename is the prefix; if a post has multiple surfaces, each gets its own run dir (the timestamp differs).

## Workflow

1. Resolve `post-dir`. Set `article-path = <post-dir>/index.md` and `output-dir = <post-dir>`. Create the run dir per the naming rule above.
2. **For each requested surface**, invoke the `cover-image` skill (from `pi-cover-image`) with `surface`, `article-path`, and `output-dir`, using a run dir under `.pi/cover-image-work/<post-dir-basename>--<UTC ts>/`. The plugin runs the full pipeline (idea → rhetoric → palette/layout → artworks → features → prompt → generation via `image-gen` → final-checks) and writes the cover to `<post-dir>/<filename>` (e.g. `cover-image-x-article.png`, `cover-image-wmp.png`). Run the surfaces sequentially (they share the same article read and the same session-cached generation backend).
3. After every surface has produced its cover, invoke the `preflight` skill on `post-dir` to run the pre-publish checks (deterministic + SAM/VLM cover-safety).

## MUST

- Map `post-dir` to `article-path` + `output-dir` exactly — do not pass `post-dir` to the plugin; it works in article-path + output-dir.
- Let the `cover-image` skill own the whole pipeline — do not reimplement any stage here.
- Chain `preflight` after all surfaces are done.

## MUST NOT

- Invent or rephrase the cover title — the plugin handles that (idea-extractor carries it, layout-planner typesets it).
- Skip preflight.
- Edit `<post-dir>/index.md` unless the user explicitly asks.