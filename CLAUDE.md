# AGENTS.md

Guidelines for any AI agent (Codex, Claude Code, etc.) writing or editing **English prose** in this repository — primarily blog posts under `YYYY-MM-DD-slug/index.md`. Apply them when drafting and when revising. They do not govern the Chinese pieces, which follow their own conventions.

## The Elements of Style (Strunk & White)

Follow these principles when writing and revising.

### Principles of composition

- **Omit needless words.** Make every word tell. Cut "the fact that," "in order to," "there is," and throat-clearing.
- **Use the active voice.** "X did Y," not "Y was done by X."
- **Put statements in positive form.** Assert what *is*, not what isn't.
- **Use definite, specific, concrete language.** Prefer the particular to the abstract, the concrete to the vague.
- **Express coordinate ideas in parallel form.**
- **Keep related words together.** Keep subject and verb close; keep modifiers next to what they modify.
- **Place the emphatic words of a sentence at its end.**
- **Make the paragraph the unit of composition** — one idea per paragraph.
- **Choose a design and hold to it.** Decide the shape of the piece, then keep to it.
- **Avoid a succession of loose sentences** — don't string clause onto clause with "and," "but," "which," "so."

### Reminders on style

- **Place yourself in the background.** Let the writing draw attention, not the writer.
- **Write with nouns and verbs**, not with adjectives and adverbs.
- **Revise and rewrite.**
- **Do not overwrite.**
- **Do not overstate.** One overstatement and the reader distrusts the rest.
- **Avoid qualifiers** — "very," "rather," "pretty," "quite," "somewhat" — they dilute.
- **Do not affect a breezy manner.**
- **Use figures of speech sparingly.** A metaphor must illuminate, not decorate — and never mix two in the same breath.
- **Do not explain too much.** Trust the reader.
- **Prefer the standard to the offbeat.**
- **Be clear.** Never sacrifice clarity for cleverness.

### Usage (the few that most affect prose)

- Use the serial (Oxford) comma: "a, b, and c."
- Do not join two independent clauses with only a comma (no comma splices) — use a period, a semicolon, or a conjunction.
- Enclose a parenthetic expression between commas — matched pairs, both or neither.
- A participial phrase at the start of a sentence must refer to the grammatical subject (no dangling modifiers).
- Avoid the words and expressions commonly misused (Strunk & White, Ch. IV): e.g., "which" vs "that," "less" vs "fewer," "comprise," "literally."

## Additional Guidelines

**Price formatting:**

- For recurring monthly prices in English prose, use `$N USD/month` so the currency is explicit for international readers, e.g., `$60 USD/month`, `$5 USD/month for the first month, then $10 USD/month`.
- Avoid nonstandard forms such as `$60 USD/mon`, `USD 60/month`, and `$60/month` unless quoting a source verbatim.

**MUST:**

- You **MUST** use commonly used idioms — established expressions a native reader recognizes as real (e.g., "in the driver's seat," "calling the shots," "at the helm").

**MUST NOT:**

- You **MUST NOT** use near-idioms — phrases that carry the cadence of a saying but are not one, usually a blend of two or more real idioms or a reworded one (e.g., "locked the controls in the human's cockpit," which welds "at the controls" + "in the pilot's seat" + "under lock and key"). Before committing to any vivid phrase, apply both tests; if it fails either, replace it with one real idiom or plain words:
  1. Is this an actual established expression, or does it only *sound* like one?
   2. Does its metaphor still hold one sentence later, without clashing with an adjacent image?

## Cover Image Skill

The cover-image pipeline ships as a public pi package, **`pi-cover-image`** (repo at `../pi-cover-image`), depended on by this project. It provides the `cover-image` skill, 8 subagents, the seed-library scripts, and the `references/` (surfaces, poster-principles, visual-rhetoric, titling, final-checks). Generation backends come from its bundled **`pi-image-gen`** package (Codex / Antigravity / Grok).

This project's entry point is the **`cover-image-platforms`** shim skill (`.pi/skills/cover-image-platforms/`). It maps a post directory to the plugin's inputs (`article-path = <post-dir>/index.md`, `output-dir = <post-dir>`), loops over the requested surfaces, and chains `preflight`. It owns no pipeline logic — the `cover-image` skill does it all.

There is no fixed style-transfer step: the aesthetic comes from real artworks matched to the article's orientation, and the layout is read from those artworks by a vision model. The flow: idea + rhetoric + orientation (from article) → [parallel: palette direction + layout direction] → download works → extract features → generate from pure text.

- The `cover-image` skill resolves the surface, invokes the subagents, downloads and filters seeds, generates candidates, and on the user's pick runs a light visual self-check. It holds no aesthetics, no rhetoric, no surface rules, and no check criteria.
- Layout is generated dynamically by the `layout-generator` subagent from the seed artworks' spatial tendencies + the surface constraint. There is no static layout file.
- `references/surfaces.md` is the **surface registry** — one row per surface with `aspectRatio`, `safeArea`, `bleed`, `text`, `cropBehavior`, `filename`, and a `detail` path. `references/surfaces/<id>.md` holds the per-surface detail (composition rules, crop behavior, element list).
- `references/poster-principles.md` holds the five tests a cover must pass — atmosphere fit, thumbnail legibility, freshness, specificity, one read — and where the idea comes from (not always the core argument). `idea-extractor` reads it before extracting.
- `references/visual-rhetoric.md` holds the catalog of visual rhetorical devices, used to *name* the rhetoric a seed artwork employs.
- `references/titling.md` holds how the article's single title is typeset on a banner, including when to split it into a kicker + main line (read by `layout-planner`).
- `references/final-checks.md` holds the criteria the visual subagents use to validate a generated cover.

Eight subagents do the judgment work. `idea-extractor` reads the article in a clean, isolated context window, reviews the poster principles, surveys the article, develops THREE idea+rhetoric candidates, scores them on the five poster tests, and outputs the highest-scoring one (with the two runners-up) plus the article's real title verbatim. `palette-planner` takes the idea + rhetoric + orientation and develops a palette direction + recommends 2–3 palette artists. `layout-planner` takes the same + the surface constraint + the article title and develops a layout direction (including how the title is typeset on the banner) + recommends 2–3 **films whose posters** embody it — layout sources are film posters from a film poster database only, never artworks. The two planners run in parallel. `artist-works` agentically searches the web for all recommended artists’ works and for the recommended films’ actual posters on a film poster database. `artwork-feature-extractor` views downloaded works and extracts visual key features as text. `layout-generator` extracts spatial tendencies. `prompt-composer` composes the final generation prompt as markdown. No image is sent to the generator — pure text. `final-checks-verifier` runs the light post-generation visual check.

A seed-library tool (in the package) supports the artwork side: `fetch.py` downloads one artwork (Wikimedia Commons first, falling back to Google Art Project via `dezoomify-rs`), `recall.py` recalls a style's seeds with provenance, and `palette.py` extracts a work's exact color distribution. Works are downloaded, then filtered to keep only those whose palette matches the article's color orientation; the kept works become the seed images passed as `referencedImagePaths`. The prompt names each referenced artwork, and the skill records per-candidate provenance — which artwork each candidate referenced, with the seed's local path and a `view_online` URL — so the reference trail is viewable, not just recorded.

The rigorous SAM-based crop-safety check is **host-side**, not in the plugin: `preflight` (`.pi/skills/preflight/`) runs the deterministic pre-publish checks plus a SAM 2 + VLM cover-safety stage (`.pi/scripts/cover-crop/cover-crop-safety-check.py` + the project-local `cover-crop-safety-verifier` subagent). The plugin's `final-checks-verifier` is a lighter post-generation visual check; `preflight` is the strict pre-publish gate.

Style, rhetoric, titling, surface, and final-checks are references rather than skills because none is runnable alone — a cover is the product of all of them. One orchestrator with reference docs preserves a single entry point and lets the dimensions compose. Adding a style, a surface, or a rhetorical device never touches the others.

Naming: every reference lives under `references/` with a kind prefix — `surfaces/<id>.md` for per-surface detail, plus the `surfaces.md` registry — while `visual-rhetoric.md`, `titling.md`, and `final-checks.md` are singleton references named by concern. Layout is not a file; it is generated dynamically. The prefix on the multi-instance kinds makes the type visible at a glance and avoids collisions with the singletons.

### Per-surface design

- **X Article Cover** (`x-article`, `cover-image-x-article.png`, 5:2): one full-bleed banner with title + subtitle + the rhetoric figure, bleeding to all four edges.
- **微信公众号头条** (`wechat-headline`, `cover-image-wmp.png`, 2.35:1): one centered-visual banner, no text. The message list shows the full banner; third-party and in-app shares both crop the center 1:1 square, so the rhetoric figure sits at the center, uncropped. WeChat renders the article title as text in its UI, so no title belongs on the image. There is no separate share file.
- **微信公众号图片消息/小绿书** (`wechat-image-message`, `cover-image-wmp-image-message.png`, 3:4): full-bleed vertical card, no text.
- **小红书** (`xiaohongshu`, `cover-image-xhs.png`, 3:4): full-bleed vertical, optional title overlay.
- **Generic ratios** (`square` 1:1, `4x3` 4:3, `9x16` 9:16, `16x9` 16:9): full-bleed, optional text, no platform crop — defaults, refined on first real use.
