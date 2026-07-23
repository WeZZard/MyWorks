# Final Checks

Criteria for validating a generated cover before it ships. These checks are run by visual subagents (models that can see the image), not by the main agent. A cover passes only when every applicable check below passes.

This reference is read by the `final-checks-verifier` subagent, alongside an optional layout reference and the platform spec for the target.

## Style conformity

- The cover matches the chosen visual style's medium, palette, composition, and tone.
- No element violates the style's "avoid" list (e.g., no photographic texture or 3D in a flat-vector style; no cliché icons).

## Rhetoric correctness

- The visual expresses the intended rhetorical device (see `visual-rhetoric.md`) and the article's thesis.
- The device is fresh, not the cliché native to that device.
- A viewer who has not read the article can still sense the relationship the cover points at.

## Text correctness (when the cover carries text)

- The title and subtitle are present verbatim, spelled correctly, and readable at thumbnail size.
- No extra or invented text, no garbled glyphs, no watermark, signature, date, URL, or brand logo.

## Platform constraints

- The file's aspect ratio matches the platform spec (X 5:2, WeChat 头条 2.35:1) within tolerance.
- **X**: full-bleed — content bleeds to all four edges; no empty margin frame; title + subtitle + metaphor all present.
- **WeChat 头条**: centered visual, no text; the center 1:1 square (the share crop) is a complete, self-contained visual with the metaphor fully inside and uncropped, no clipped fragments or lines bleeding in at any edge, no visible seam.

## Verdict

Return one line per check: `<check>: PASS` or `<check>: NONE — <one clause>`. The cover passes overall only when every applicable check is `PASS`.