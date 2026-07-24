# Titling

How the article's single title is typeset on a cover banner. This is a **layout** reference, read by `layout-planner`. The article has one title and no subtitle; any "subtitle" on the cover is a typographic split of that one title, chosen at layout time — not extracted from the article.

## The title is fixed; the arrangement is the design

- The cover renders the article's real title (the frontmatter `title`), verbatim. The title string is not a design variable — do not rename, rephrase, or re-case it away from the article.
- What IS a design variable is how that string sits on the banner: whether it stays one line, breaks into two lines, or splits into a small kicker + a main line. That is a layout/typesetting decision, made here.

## When to split the title into kicker + main line

A long or two-part title often reads best on a wide banner as a small **kicker** above a larger **main line**. Split when the title has a clear source/method + finding structure, and the banner is wide enough that one line would be cramped:

- `X Reveals Y` → kicker `X Reveals`, main `Y`
- `X: Y` → kicker `X`, main `Y`
- `X — Y` → kicker `X`, main `Y`

Example: `J-Space Reveals How Examples Shape Model Behavior` → kicker `J-Space Reveals`, main `How Examples Shape Model Behavior`.

Rules for the split:

- Both strings are **verbatim substrings** of the real title — cut at the structural boundary, do not reword either side.
- The kicker is the source, method, or series cue; the main line is the finding (what the reader takes away).
- Split only when it improves the banner's read. A short title (≤ ~5 words) usually stays one line.
- On surfaces that forbid text (`text: none`), do not set any title; this reference does not apply.

## Placement and scale

- Place the title where the layout's negative space allows it to breathe; it must not overlap the rhetoric figure.
- Keep title + kicker inside the surface's crop-safe zone.
- The main line is the larger type; the kicker is a fraction of its size (roughly one-third to one-half) and sits directly above it.
- At thumbnail size the title must still be legible — favor fewer, larger words over many small ones.

## What layout-planner outputs

As part of `layout_direction`, output a `title` block:

```text
title:
  article_title: <the real title, verbatim>
  kicker: <verbatim substring, or none>
  main: <verbatim substring>
  placement: <where on the banner>
  relative_size: <kicker : main, e.g. 1:2>
```

## MUST NOT

- Do not invent, rename, or rephrase the title — both `kicker` and `main` are verbatim substrings of the article's real title.
- Do not split when the title is short enough to read cleanly as one line on this banner.
- Do not place title text on a `text: none` surface.