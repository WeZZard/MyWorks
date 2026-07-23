---
name: preflight
description: Run pre-publish checks on a blog post — frontmatter, content, feed-page exposure, and cover image checks per platform. Use before publishing a post under YYYY-MM-DD-slug/.
---

# Preflight

Run pre-publish checks on a post. The skill is a thin orchestrator around a deterministic stage and a VLM verification stage. It owns no checking logic itself. Cover expectations come from the platform specs in `.pi/skills/cover-image/references/` (`platform-*.md`).

## What it checks

1. **Content and metadata** (deterministic, `.pi/bin/preflight`): frontmatter fields, non-empty body, no `TODO`, local image refs resolve, cover files exist with the right aspect ratios (X 5:2, WeChat 头条 2.35:1).
2. **Feed-page exposure** (deterministic, same script): title length, subtitle presence, and an approximate 300-character excerpt sanity check that mirrors the gatsby feed/`PostExcerpt` query.
3. **Cover checks** (SAM 2 + VLM), per platform spec:
   - **WeChat 头条** (`cover-image-wmp.png`): the center 1:1 square is the share card (third-party and in-app share both crop to it). SAM finds candidate squares; the VLM confirms the **center** square is a complete, self-contained visual (metaphor fully inside, uncropped, no text bleeding in). The center square is the deciding candidate.
   - **X article** (`cover-image-x-article.png`): full-bleed, no center-square rule. The VLM confirms it is a coherent full-bleed banner with readable title + subtitle + metaphor. (Run only when the user asks.)

## Responsibilities

- Resolve the target post directory.
- Run `.pi/bin/preflight <post-dir>` and read the deterministic report. If it fails, present failures and stop.
- Run the cover checks above via the SAM script (`.pi/scripts/cover-crop/cover-crop-safety-check.py`) and the `cover-crop-safety-verifier` subagent.
- Present a single consolidated report.

## Limits

**MUST NOT:**

- Duplicate the deterministic checks or the SAM logic here. Keep them in `.pi/bin/preflight` and `.pi/scripts/cover-crop/cover-crop-safety-check.py`.
- Run the VLM verification in the main agent. It belongs in the `cover-crop-safety-verifier` subagent for context hygiene.
- Skip the deterministic stage before the cover stage.
- Edit the post unless the user explicitly asks.

## Workflow

1. Resolve the target post directory.
2. Run the deterministic stage:

   ```bash
   python3 .pi/bin/preflight <post-dir>
   ```

   Exit code 1 means a hard failure. Present failures and stop unless the user says to continue.

3. **WeChat 头条 center-crop check.** Run the SAM candidate script:

   ```bash
   .pi/scripts/cover-crop/.venv/bin/python .pi/scripts/cover-crop/cover-crop-safety-check.py <post-dir>/cover-image-wmp.png --json
   ```

   If the venv is missing, tell the user to run `zsh .pi/scripts/cover-crop/setup.zsh` and stop.

4. Spawn the `cover-crop-safety-verifier` subagent with the candidates. In the spawning prompt, state that the **center** square is the deciding candidate (third-party platforms crop to it) and must pass; left/right are optional in-app share exports. Ask for `PASS center` or `NONE` with one short clause naming what is cut or missing.

5. **X article cover check (when the user asks).** Spawn the `cover-crop-safety-verifier` subagent with `cover-image-x-article.png` and ask whether it is a coherent full-bleed banner with readable title + subtitle + metaphor. Do not apply the center-square rule to X.

6. Present a consolidated report: the deterministic result, the center-crop verdict for the 头条, and (if run) the X verdict. When the 头条 center verdict is `NONE`, say the cover has no complete center crop and suggest regenerating via the `cover-image` skill (WeChat platform spec: centered-visual banner, share = center crop).

## Response Handling

**MUST:**

- Present the deterministic failures and the VLM verdicts in plain language.
- Name the post directory and each cover file checked.
- When the 头条 center verdict is `NONE`, name the regeneration step: regenerate with the `cover-image` skill.

**MUST NOT:**

- Paste the raw SAM JSON unless the user asks.
- Re-attach the cropped images to the main conversation.
- Re-run the VLM judgment in the main agent.