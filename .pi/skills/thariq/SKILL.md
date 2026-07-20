---
name: thariq
description: An illustration skill derived from Thariq's X article cover image.
---

1. You **MUST** extract user's intents and generate values for the variables listed in **Appendix II: Variable Generate Principles** based on the extracted user intents and the guidances in the principles:
2. You **MUST** substitute the variables in the prompt template in **Appendix I: Prompt Template** with the value generated in the previous step.
3. You **MUST** generate the image with the substituted prompt.
4. You **MUST** use the `codex_generate_image` tool to generate the image if it exists.

## Appendix I: Prompt Template

<PROMPT_TEMPLATE>
A minimalist, modern editorial illustration on a [BACKGROUND_COLOR] background.
On the [TEXT_BLOCK_POSITION], create a structured text block with three levels:
At the top: a smaller, bold, delicate, subtitle [SUBTITLE_TEXT] using [TINT_COLOR] for sans serif font.
Below it: a large, bold, multi-line main title [MAIN_TITLE_TEXT] using [MAIN_TITLE_TEXT_COLOR] for serif font.
At the bottom of the text block: a short, thin horizontal bar in [TINT_COLOR].
On the opposite side, a large, abstract [CONTAINER_SHAPE] in a contrasting base color.
Inside this shape is a minimal, geometric line-art illustration representing [ABSTRACT_METAPHOR].
The graphic features a [LINE_STYLE] breaking out of the container.
High contrast, clean vector art style, flat design, with [ACCENT_COLOR] accents.
[TONE] vibe, sleek corporate editorial header, UI design aesthetic.
</PROMPT_TEMPLATE>

## Appendix II: Variable Generate Principles

<VARIABLE_GENERATE_PRINCIPLES>

[BACKGROUND_COLOR]: The primary base of the image.
Options: deep charcoal black, stark white, soft cream, dark navy, muted sage green.

[TEXT_POSITION]: Where you want the "blank space" for your text to go.
Options: left side, right side, top half.

[CONTAINER_SHAPE]: The main shape holding the graphic.
Options: organic amoeba blob, sharp geometric polygon, soft rounded rectangle, perfect circle, overlapping arches.

[ABSTRACT_METAPHOR]: The inner line-art that tells the story. A metaphor in this style is a geometric system with a directional force within it — a minimal diagram that implies change, insight, or movement without depicting it literally. Derive one using the method in section 1 below.
Examples: "a topographical map with a climbing path," "a constellation of connected data nodes," "an architectural blueprint with a highlighted detail."

[LINE_STYLE]: The dynamic element that interacts with the main shape.
Options: dashed trajectory line, a glowing fiber-optic thread, a solid structural beam, a winding river line.

[ACCENT_COLOR]: The "tint color" for small details, icons, and highlights.
Options: burnt orange, electric blue, neon mint, metallic gold, soft peach.

[TONE]: The overall emotional quality of the piece.
Options: intellectual and mysterious, airy and optimistic, highly technical and futuristic, warm and inviting.

[TINT_COLOR]: Accent Hierarchies. The tint color is reserved for the highest points of visual punctuation. It defines the first piece of text (subtitle), the final destination icon, and the emphasis line. Use a highly saturated, vibrant color for this role.

[SUBTITLE_TEXT]: This acts as the "kicker" or eyebrow text. It provides context and should be very short so the AI can render it without spelling errors.
Rule: Keep it under 5 words. Use it for categories, chapters, or brand context.
Options: "Annual Report:", "Case Study:", "The Ultimate Guide:", "Chapter 01", "Research Insights".

[MAIN_TITLE_TEXT]: The anchor of the composition. This needs to be the primary focus of the left side (or top) of the image.
Rule: Keep it punchy, ideally 2 to 6 words. AI struggles with long paragraphs, so short, impactful titles work best.
Options: "Unlocking Growth", "The Future of AI", "System Architecture", "Mapping the Unknown", "Strategic Horizons".

[MAIN_TITLE_TEXT_COLOR]: This dictates the legibility of the entire image. It must work in tandem with your chosen [BACKGROUND_COLOR].
Rule: Maximum contrast is required. Do not use mid-tones.
Options (Dark Backgrounds): stark white, soft cream, pale silver.
Options (Light Backgrounds): pure black, deep charcoal, dark navy blue.

**1. Metaphorical Abstraction (The [ABSTRACT_METAPHOR]):**

The reference image doesn't show a literal explorer; it uses a line graph and triangles to represent a journey. The metaphor works by spatializing an abstract idea — turning relationships, changes, and revelations into positions, paths, and boundaries.

Build the metaphor in three moves:

1. **Choose the space.** What kind of abstract field does the article inhabit? Relational (a network of nodes), temporal (layered strata or a timeline), hierarchical (ascending levels), spatial (a terrain with obstacles and routes).

2. **Populate the space.** Which geometric primitives express that field? Nodes and edges for networks. Contour lines for terrain. Orthographic projections for structure. Concentric rings for influence. Grid lines for systems. Rays for emission.

3. **Add a vector.** What moves, points, or crosses within the space? This is the narrative tension. A path climbing through contours. An edge linking isolated nodes. A beam passing through strata. A region pulled into focus with a callout.

The result is a noun phrase describing a geometric system with a directional element. Avoid literal objects — the viewer should recognize a diagram, not a thing.

**2. The "Lens" Contrast (Background vs. Container):**

The image uses the container ([CONTAINER_SHAPE]) as a "lens" of known information against the vastness of the background ([BACKGROUND_COLOR]).
Value Contrast: The background and container must sit at opposite ends of the brightness spectrum (e.g., charcoal vs. cream, or navy vs. stark white).
Shape Psychology: Choose a container shape that matches the mood. Organic blobs feel creative, fluid, and human. Sharp polygons feel rigid, data-driven, and structured.

**3. Boundary Crossing (The [LINE_STYLE]):**

The most dynamic part of the original image is the line that originates inside the shape and escapes into the negative space. It creates narrative tension.
Show a transition: The line should represent movement from a current state to a future state.
Change states: Notice how the reference line changes from solid inside the blob to dashed outside of it. Your variable should imply action (e.g., "a branching path," "an expanding wave," "a piercing ray of light").

**4. The 10% Accent Rule (The [ACCENT_COLOR]):**

The burnt orange in the reference image is used incredibly sparingly. It creates a visual hierarchy.
High Saturation: Choose an accent color that pops aggressively against your chosen background (e.g., neon against dark, warm against cool).
Strategic Placement: Imagine this color only applying to the "punctuation marks" of the image—a final destination node, a subtle grid line, or a single geometric anomaly.

**5. Lens of Context (Background vs. Container):**

The container is a "lens of known information" against the vast background. The container must have high value-contrast with the background (light vs. dark) so that the line graph can cross between the two states.

**6. Structural Integrity:**

Ensure the main title is always large and has a strong contrast with the background (e.g., white text on black/blue background, or black text on a light background). It should act as the visual "anchor" for the left side.

</VARIABLE_GENERATE_PRINCIPLES>