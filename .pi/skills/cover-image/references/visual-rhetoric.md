# Visual Rhetoric

Visual rhetoric is how a cover turns the article's thesis into a picture a viewer reads at a glance. Metaphor and analogy are two devices; the catalog below holds more. The cover-image skill picks 2–3 devices that fit the article and generates one candidate per device, so the user can choose.

This reference is read by the `cover-image` skill. It is not style-specific; a visual style reference says *how* a device is drawn (medium, palette, composition), this reference says *which* relationship a device expresses.

## How to derive a device and its source from the article

Do not grab a concept on instinct. Follow this chain:

1. **Read the article fully.** Do not skim; the usable concepts are often not the headline noun.
2. **Survey the concepts it covers.** List them — claims, mechanisms, objects, tensions, analogies the article itself makes. Keep the list explicit so the next step is a choice, not a grab.
3. **Pick the rhetoric devices.** Pick 2–3 devices whose relationship (see the catalog) matches the article's tensions.
4. **Pick a concept per device.** For each device, pick the concept from the survey whose relationship best matches that device. A device maps one concept onto a visual; choose the concept whose structure is that device's relationship.
5. **Write source → target → why for that concept**, per the *Prompt contract for a candidate* below.

The source concept must come from the survey in step 2, never grabbed. The center word of the article must be the hero of the visual, not a side element.

## Catalog

| Device | Relationship | How it reads | Example |
|---|---|---|---|
| Metaphor (隐喻) | identity — X is Y | one thing standing for the idea | a closed gate for a blocked path |
| Analogy (类比) | structure — X maps to Y | a diagram whose structure mirrors the idea | a contour map for a global workspace |
| Metonymy (借代) | contiguity — an attribute for the whole | an associated thing standing in | a crown for authority |
| Synecdoche (提喻) | part–whole | a part for the whole, or the whole for a part | a single gear for the machine |
| Juxtaposition (并置/对比) | opposition | two opposing visuals side by side | a tiny lock next to a huge door |
| Irony (反讽) | contradiction | a visual that contradicts expectation | an "open" sign on a barred gate |
| Exaggeration (夸张) | scale | shrink or enlarge one feature to make the point | a giant lens over a tiny flaw |
| Visual pun (双关) | double meaning | one visual that reads two ways | a key that is also a river |
| Personification (拟人) | agency | human traits on a non-human | a machine with a hand over its eyes |
| Symbol (象征) | convention | a conventional sign for the idea | a balance for fairness |

## Selecting devices for an article

- Match the device to the relationship the thesis hinges on, not to the topic's nouns.
- Avoid the cliché native to each device (no lightbulb for ideas, no chain for freedom, no heart for love) unless you recompose it into a fresh relationship.
- Prefer the device the article's tension already implies: a paradox wants irony or juxtaposition; a mechanism wants analogy; a stand-in wants metonymy or synecdoche; a scale gap wants exaggeration.
- Pick 2–3 devices so the skill can generate a candidate per device and the user can choose.

## Prompt contract for a candidate

A rhetoric is a mapping of one concept onto another. Every candidate prompt MUST state three things, in this order, before any visual description:

1. **Source concept** — the concept drawn from the article. Quote or closely paraphrase the article; do not invent. Name it (e.g., "examples install a structure the model uses directly, shifting the behavior distribution").
2. **Target visual** — the visual the source maps to under this device. Name the elements concretely (e.g., "a panel of lights; one light pushed to the front and lit").
3. **Why the mapping holds** — one or two sentences: the structural reason this device fits this source→target. State the relationship the device expresses and show it matches the relationship in the article (e.g., "the article itself calls the workspace a shared whiteboard and says concepts move to the front, so workspace→panel and concept-rising→light preserve the article's own structure").

A device without a grounded source, a named target, and a stated justification is not a rhetoric candidate; do not generate it. The source must come from the article (or the repository), never invented. The center word of the article must be the hero of the visual, not a side element.