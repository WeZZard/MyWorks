# Final Checks

Criteria for validating a generated cover before it ships. These checks are run by visual subagents (models that can see the image), not by the main agent. A cover passes only when every applicable check below passes.

This reference is read by the `final-checks-verifier` subagent, alongside an optional layout reference and the surface detail file for the target.

## Style conformity

- The cover matches the chosen visual style's medium, palette, composition, and tone.
- No element violates the style's "avoid" list (e.g., no photographic texture or 3D in a flat-vector style; no cliché icons).

## Rhetoric correctness

- The visual expresses the intended rhetorical device (see `visual-rhetoric.md`) and the article's thesis.
- The device is fresh, not the cliché native to that device.
- A viewer who has not read the article can still sense the relationship the cover points at.

## Text correctness (when the cover carries text)

- The text on the cover equals the article's real title (the `Article Title` ground truth). If the layout split it into a kicker + a main line, the two together must concatenate to the real title, verbatim — no rewording, no extra words, no missing words.
- Spelled correctly and readable at thumbnail size.
- No extra or invented text, no garbled glyphs, no watermark, signature, date, URL, or brand logo.

## Surface constraints

- The file's aspect ratio matches the surface config from `references/surfaces.md` within tolerance.
- The composition honors the surface's `safeArea` and `bleed`: critical content survives the surface's crop behavior; where `bleed` is `full`, content runs to all four edges with no margin frame; where `bleed` is `none`, content stays inside the safe area.
- The text rule is met: `required` surfaces carry title + subtitle verbatim; `none` surfaces carry no text; `optional` surfaces carry text only when the surface choice asked for it.

## Verdict

Return one line per check: `<check>: PASS` or `<check>: NONE — <one clause>`. The cover passes overall only when every applicable check is `PASS`.