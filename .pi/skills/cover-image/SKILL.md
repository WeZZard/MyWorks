---
name: cover-image
description: Create a cover image for a target platform (X, WeChat). An idea-extractor reads the article and outputs idea + rhetoric + orientation; palette-planner and layout-planner develop palette and layout directions in parallel and recommend artists; artist-works downloads works; features are extracted and combined into a pure-text generation prompt — no image is sent to the generator.
---

# Cover Image

Create a cover image for a target platform. The flow splits into:
- **Concept** (from the article): idea → rhetoric → orientation — all in one clean context.
- **Palette** (parallel): palette-planner develops a palette direction + recommends palette artists.
- **Layout** (parallel): layout-planner develops a layout direction + recommends layout artists.
- **Download**: artist-works finds and downloads works for all recommended artists.
- **Extract + Generate**: palette features from palette works + layout features from layout works → pure-text generation prompt (no image sent).

References under `references/`:
- `platform-<platform>.md` — surfaces, aspect ratios, crop behavior, filenames, element list.
- `visual-rhetoric.md` — catalog of visual rhetorical devices (read by idea-extractor).
- `titling.md` — distilling title/subtitle (X covers only).
- `final-checks.md` — criteria for the visual subagents.

Subagents:
- `idea-extractor` — reads the article in a clean context; extracts idea (3 words) + creates rhetoric (1 device + target) + orientation (color/tone).
- `palette-planner` — given idea + rhetoric + orientation, develops a palette direction + recommends 2–3 palette artists.
- `layout-planner` — given idea + rhetoric + orientation + platform constraint, develops a layout direction + recommends 2–3 layout artists.
- `artist-works` — agentically searches the web for all recommended artists' works; records work + reason + source URL.
- `artwork-feature-extractor` — views downloaded works and extracts visual key features as text (one per image).
- `layout-generator` — views downloaded works + platform constraint, extracts spatial tendencies, writes layout rules.
- `prompt-composer` — takes all intermediate products (rhetoric, palette direction + features, layout direction + features, platform constraints) and composes the final generation prompt as markdown text. Kimi K3.

Tools: `.pi/scripts/seed-library/` — `fetch.py` (download with Wikimedia verification + GAP fallback), `palette.py` (exact palette), `recall.py` (gallery + provenance).

## Working directory

```
.pi/cover-image-work/<post-dir-basename>--<YYYYMMDDTHHMMSS>/
  meta.json                     # post-dir, platform, timestamp
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

- `platform` — `x` or `wechat`.
- `post-dir` — the `YYYY-MM-DD-slug/` directory.

If the post or platform is missing, ask once for it; do not guess.

## Workflow

1. Resolve the platform and the post-dir. Read the platform spec. Create the run dir with subdirs `05-downloads/`, `09-candidates/`. Write `meta.json`.
2. **Idea + rhetoric + orientation.** Invoke `idea-extractor` with the article path AND `references/visual-rhetoric.md`. It reads the article in a clean context, extracts idea (3 words), creates rhetoric (1 device + target), and extracts orientation (color/tone). **Write** to `01-idea-extractor.json`.
3. **[Parallel] Palette direction.** Invoke `palette-planner` with the idea, rhetoric, and orientation. It develops a palette direction + recommends 2–3 palette artists. **Write** to `02-palette-planner.json`.
4. **[Parallel] Layout direction.** Invoke `layout-planner` with the idea, rhetoric, orientation, and platform constraint. It develops a layout direction + recommends 2–3 layout artists. **Write** to `03-layout-planner.json`.
5. **Find works.** Invoke `artist-works` with all artists from both planners + the rhetoric target. **Write** to `04-artist-works.json`.
6. **Download works.** For each found work, download with `fetch.py` into `05-downloads/`.
7. **Extract palette features.** Invoke `artwork-feature-extractor` on each palette artist's downloaded work. **Write** to `06-palette-features.json`.
8. **Extract layout features.** Invoke `artwork-feature-extractor` on each layout artist's downloaded work. **Write** to `07-layout-features.json`.
9. **Generate.** Build the generation prompt with FOUR sections: **Content** (rhetoric target), **Layout** (layout direction from step 4 + layout features from step 8), **Palette** (palette direction from step 3 + palette features from step 7), **Constraints**. Do NOT send any image via `referencedImagePaths` — pure text only. Generate with `codex_generate_image` into `08-candidates/`. **Write the full prompt** to `08-generation-prompts/` (one .md per candidate).
10. **Record provenance.** Write `09-provenance.json` mapping each candidate to its palette source + layout source + rhetoric + features.
11. **Record provenance.** Write `<run-dir>/10-provenance.json` mapping each candidate to its palette source + layout source + rhetoric + features. with their palette source, layout source, and rhetoric.
12. **Ship + check.** Copy the user's pick to `10-final.png`, then to the post dir with the platform filename. Run `cover-crop-safety-verifier` + `final-checks-verifier`, then `preflight`.

## Stacking rules

**MUST:**

- Let `idea-extractor` read the article in a clean context; it creates idea + rhetoric + orientation — do not hardcode any of them.
- Run `palette-planner` and `layout-planner` in parallel — they are independent.
- Let `artist-works` find works for ALL artists from BOTH planners.
- Extract palette features from palette artists' works and layout features from layout artists' works — they may be different artworks.
- Do NOT send any artwork image to `codex_generate_image` — the generator works from text only.
- Let `prompt-composer` compose the generation prompt from all intermediate products — do not compose it yourself.
- Generate 2–3 candidates in parallel from the same composed prompt.

**MUST NOT:**

- Send artwork images to the generator.
- Mix palette and layout sources — keep them separate until the generation prompt.
- Skip provenance or the final visual checks.
- Put text on the WeChat 头条 banner.

## Limits

- You **MUST NOT** edit the post's `index.md` unless the user explicitly asks.
- You **MUST NOT** overwrite an existing cover asset unless the user explicitly asks.