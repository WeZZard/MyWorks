---
name: cover-image
description: Create a cover image for a target surface (X Article, 微信公众号头条/图片消息, 小红书, or a generic ratio). An idea-extractor reads the article and outputs idea + rhetoric + orientation; palette-planner and layout-planner develop palette and layout directions in parallel and recommend artists; artist-works downloads works; features are extracted and combined into a pure-text generation prompt — no image is sent to the generator.
---

# Cover Image

Create a cover image for a target **surface**. The flow splits into:
- **Concept** (from the article): idea → rhetoric → orientation — all in one clean context.
- **Palette** (parallel): palette-planner develops a palette direction + recommends palette artists.
- **Layout** (parallel): layout-planner develops a layout direction + recommends layout artists.
- **Download**: artist-works finds and downloads works for all recommended artists.
- **Extract + Generate**: palette features from palette works + layout features from layout works → pure-text generation prompt (no image sent).

References under `references/`:
- `surfaces.md` — the **surface registry**: one row per surface with `aspectRatio`, `safeArea`, `bleed`, `text`, `cropBehavior`, `filename`, and a `detail` path. Read this first to offer the surface choice and to load each surface's config.
- `surfaces/<id>.md` — per-surface detail: composition rules, crop behavior, element list (the `detail` each registry row points at).
- `poster-principles.md` — the five tests a cover must pass; read by `idea-extractor` before it extracts anything.
- `visual-rhetoric.md` — catalog of visual rhetorical devices (read by idea-extractor).
- `titling.md` — how the article's single title is typeset on a banner, including when to split into kicker + main (read by layout-planner on text-carrying surfaces).
- `final-checks.md` — criteria for the visual subagents.

Subagents:
- `idea-extractor` — reads the article in a clean context; extracts idea (3 words) + creates rhetoric (1 device + target) + orientation (color/tone).
- `palette-planner` — given idea + rhetoric + orientation, develops a palette direction + recommends 2–3 palette artists.
- `layout-planner` — given idea + rhetoric + orientation + surface constraint, develops a layout direction + recommends 2–3 layout artists.
- `artist-works` — agentically searches the web for all recommended artists' works; records work + reason + source URL.
- `artwork-feature-extractor` — views downloaded works and extracts visual key features as text (one per image).
- `layout-generator` — views downloaded works + surface constraint, extracts spatial tendencies, writes layout rules.
- `prompt-composer` — takes all intermediate products (rhetoric, palette direction + features, layout direction + features, surface constraints) and composes the final generation prompt as markdown text. Kimi K3.

Tools: `.pi/scripts/seed-library/` — `fetch.py` (download with Wikimedia verification + GAP fallback), `palette.py` (exact palette), `recall.py` (gallery + provenance).

## Working directory

```
.pi/cover-image-work/<post-dir-basename>--<YYYYMMDDTHHMMSS>/
  meta.json                     # post-dir, surface, timestamp
  01-idea-extractor.json    # idea (3 words) + rhetoric (device + target) + orientation
  02-palette-planner.json       # palette direction + palette artists
  03-layout-planner.json        # layout direction + layout artists
  04-artist-works.json          # all works (palette + layout) + reason + URL
  05-downloads/                 # downloaded artworks (all)
  06-palette-features.json      # palette features extracted from palette artists' works
  07-layout-features.json       # layout features extracted from layout artists' works
  08-prompt.md                  # the composed generation prompt (from prompt-composer)
  09-candidates/                # generated candidate PNGs (2-3 from the same prompt)
  10-provenance.json            # per candidate: palette source + layout source + rhetoric + features
  11-final.png                  # the user's pick
```

Every step writes its output to the fixed filename before the next step runs. Nothing is held only in conversation. Gitignore `.pi/cover-image-work/`.

## Input

- `surface` — a surface `id` from `references/surfaces.md` (e.g. `x-article`, `wechat-headline`, `wechat-image-message`, `xiaohongshu`, `square`, `4x3`, `9x16`, `16x9`).
- `post-dir` — the `YYYY-MM-DD-slug/` directory.

If the surface is missing, ask once which surface, listing the `label` column from the registry; cache the answer in the session (it stays in the transcript). If the post-dir is missing, ask once for it. Do not guess either.

## Workflow

1. Resolve the surface and the post-dir. Read `references/surfaces.md`, look up the surface row, and read its `detail` file (`references/surfaces/<id>.md`). Build the **surface constraint** from the row: `aspectRatio` + `safeArea` + `bleed` + `text` + `cropBehavior`. Create the run dir with subdirs `05-downloads/`, `09-candidates/`. Write `meta.json` (include `surface`).
2. **Idea + rhetoric + orientation + article title.** Invoke `idea-extractor` with the article path AND `references/poster-principles.md` AND `references/visual-rhetoric.md`. It reviews the poster principles, surveys the article, develops THREE idea+rhetoric candidates, scores them on the five poster tests, and outputs the highest-scoring one (with per-test breakdown and the two runners-up). It also carries the article's frontmatter `title` **verbatim** as `article_title` — it does NOT split or rephrase it; splitting is a layout decision. **Write** the full output to `01-idea-extractor.json`. Downstream uses the chosen idea, rhetoric, orientation, and `article_title` verbatim.
3. **[Parallel] Palette direction.** Invoke `palette-planner` with the idea, rhetoric, and orientation. It develops a palette direction + recommends 2–3 palette artists. **Write** to `02-palette-planner.json`.
4. **[Parallel] Layout direction.** Invoke `layout-planner` with the idea, rhetoric, orientation, the surface constraint, AND the article's real title (from `01-idea-extractor.json`) AND `references/titling.md`. It develops a layout direction — including how the title is typeset on the banner (`title`: `article_title` + `kicker` + `main` + placement + relative size, both strings verbatim substrings of the real title) — and recommends 2–3 layout artists. **Write** to `03-layout-planner.json`.
5. **Find works.** Invoke `artist-works` with all artists from both planners + the rhetoric target. **Write** to `04-artist-works.json`.
6. **Download works.** For each found work, download with `fetch.py` into `05-downloads/`.
7. **Extract palette features.** Invoke `artwork-feature-extractor` on each palette artist's downloaded work. **Write** to `06-palette-features.json`.
8. **Extract layout features.** Invoke `artwork-feature-extractor` on each layout artist's downloaded work. **Write** to `07-layout-features.json`.
9. **Generate.** `prompt-composer` composes the generation prompt with FOUR sections: **Content** (rhetoric target), **Layout** (layout direction from step 4 + layout features from step 8), **Palette** (palette direction from step 3 + palette features from step 7), **Constraints** (the surface constraint: aspect ratio, safe area, bleed, text rules, crop behavior). **Write the full prompt for each candidate to `08-generation-prompts/candidate-<n>.md` BEFORE calling the generator.** Then read each file and pass its content **verbatim** to `codex_generate_image` — do not rewrite, expand, paraphrase, or compose inline. Do NOT send any image via `referencedImagePaths` — pure text only. Generate into `08-candidates/`. The content sent to the generator MUST be byte-identical to what is written in the candidate file; if it is not, the step is invalid.
10. **Record provenance.** Write `09-provenance.json` mapping each candidate to its palette source + layout source + rhetoric + features.
11. **Record provenance.** Write `<run-dir>/10-provenance.json` mapping each candidate to its palette source + layout source + rhetoric + features. with their palette source, layout source, and rhetoric.
12. **Ship + check.** Copy the user's pick to `10-final.png`, then to the post dir with the surface's `filename`. Run `cover-crop-safety-verifier` + `final-checks-verifier`, then `preflight`.

## Stacking rules

**MUST:**

- Let `idea-extractor` read the article in a clean context; it creates idea + rhetoric + orientation — do not hardcode any of them.
- Run `palette-planner` and `layout-planner` in parallel — they are independent.
- Let `artist-works` find works for ALL artists from BOTH planners.
- Extract palette features from palette artists' works and layout features from layout artists' works — they may be different artworks.
- Do NOT send any artwork image to `codex_generate_image` — the generator works from text only.
- Let `prompt-composer` compose the generation prompt from all intermediate products — do not compose it yourself.
- Render the title **verbatim** from `layout-planner`'s `title` block (`article_title` / `kicker` / `main`) — the article's real title, typeset per the titling reference. Do not invent, rephrase, or re-split the title; the main agent never authors cover text.
- **Write each candidate's full prompt to `08-generation-prompts/candidate-<n>.md` before calling the generator, and pass that file's content verbatim to `codex_generate_image`.** The prompt sent to the tool must equal the file's content — no inline rewriting, expanding, or paraphrasing.
- Generate 2–3 candidates in parallel from the same composed prompt.

**MUST NOT:**

- Send artwork images to the generator.
- Send a prompt to `codex_generate_image` that differs from what is written in `08-generation-prompts/candidate-<n>.md`, or call the generator before the candidate file is written.
- Invent or rephrase the cover title — it comes from `idea-extractor`'s `article_title` and is typeset by `layout-planner`; the main agent never authors or splits it.
- Mix palette and layout sources — keep them separate until the generation prompt.
- Skip provenance or the final visual checks.
- Put text on the WeChat 头条 banner.

## Limits

- You **MUST NOT** edit the post's `index.md` unless the user explicitly asks.
- You **MUST NOT** overwrite an existing cover asset unless the user explicitly asks.