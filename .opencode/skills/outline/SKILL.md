---
name: outline
description: Make an outline for a post.
---

# Outline

Use this skill as the shell around the `outline-generator` subagent.

This skill does not own outline design principles. Keep outline methodology in the `outline-generator` subagent. The skill only prepares context, invokes the subagent, and interprets the response for the user.

## Responsibilities

- Summarize the current conversation and any source notes.
- Form an append-only spawning prompt for `outline-generator`.
- Invoke the `outline-generator` subagent with that prompt.
- Read the subagent response.
- Present the useful output to the user and ask what to change next.

## Limits

**MUST NOT:**

- You **MUST NOT** define outline structure rules in this skill.
- You **MUST NOT** duplicate outline methodology here.
- You **MUST NOT** draft the article body unless the user explicitly asks.
- You **MUST NOT** create or edit the post file unless the user explicitly asks.
- You **MUST NOT** treat the subagent as a state machine.

## Context Summary

Before invoking `outline-generator`, create a compact summary from the current conversation.

Include only information the subagent needs:

1. Core thesis: What is the article trying to say in one sentence?
2. Personal stake: Why does this matter to the author specifically?
3. Reader promise: What will the reader understand better after reading this?
4. Key raw materials: Important experiences, arguments, examples, quotes, contrasts, or observations.
5. Tension / conflict: What is the central disagreement, paradox, or unresolved problem?
6. Constraints: Tone, register, audience, things to avoid, authenticity rules.
7. Existing post: The path to the existing post. Optional. Empty when the post is not created.
8. Revisions: The historical revisions of the discussed outlines.

## Spawning Prompt

Pass the summary to `outline-generator` as an append-only input bundle.

Use this prompt shape:

<SPAWNING_PROMPT_TEMPLATE>
```markdown
## Core thesis
<!-- What is the article trying to say in one sentence? -->
## Personal Stake
<!-- Why does this matter to the author specifically? -->
## Reader Promise
<!-- What will the reader understand better after reading this? -->
## Key Raw Materials
<!-- Important experiences, arguments, examples, quotes, contrasts, or observations. -->
## Tension / Conflict
<!-- What is the central disagreement, paradox, or unresolved problem? -->
## Constraints
<!-- Tone, register, audience, things to avoid, authenticity rules. -->
## Existing Post
<!-- The path to the existing post. Optional. Empty when the post is not created. -->
## Revisions
<!-- The historical revisions of the discussed outlines. You **MUST** list in the following format:

### 1. [Design purpose of the outline V1]

**Section Titles:**

1. <Section Title 1. Verbatim copy from the `outline-generator` subagent outputs.>
2. <Section Title 2. Verbatim copy from the `outline-generator` subagent outputs.>

**Writing Approach:**

1. <Section Title 1>: <Writing approach of section 1. Verbatim copy from the `outline-generator` subagent outputs.>
  **Pyramid Role:** <Pyramid role of section 1. Verbatim copy from the `outline-generator` subagent outputs.>
  **HKRR:** <HKRR component of section 1. Verbatim copy from the `outline-generator` subagent outputs.>
2. <Section Title 2>: <Writing approach of section 2. Verbatim copy from the `outline-generator` subagent outputs.>
  **Pyramid Role:** <Pyramid role of section 2. Verbatim copy from the `outline-generator` subagent outputs.>
  **HKRR:** <HKRR component of section 2. Verbatim copy from the `outline-generator` subagent outputs.>

**User's Opinions:**

1. ... <A user's opinion in one sentence>
2. ... <A user's opinion in one sentence>

---

### 2. [Design purpose of the outline V2]

**Section Titles:**

1. <Section Title 1. Verbatim copy from the `outline-generator` subagent outputs.>
2. <Section Title 2. Verbatim copy from the `outline-generator` subagent outputs.>

**Writing Approach:**

1. <Section Title 1>: <Writing approach of section 1. Verbatim copy from the `outline-generator` subagent outputs.>
  **Pyramid Role:** <Pyramid role of section 1. Verbatim copy from the `outline-generator` subagent outputs.>
  **HKRR:** <HKRR component of section 1. Verbatim copy from the `outline-generator` subagent outputs.>
2. <Section Title 2>: <Writing approach of section 2. Verbatim copy from the `outline-generator` subagent outputs.>
  **Pyramid Role:** <Pyramid role of section 2. Verbatim copy from the `outline-generator` subagent outputs.>
  **HKRR:** <HKRR component of section 2. Verbatim copy from the `outline-generator` subagent outputs.>

**User's Opinions:**

1. ... <A user's opinion in one sentence>
2. ... <A user's opinion in one sentence>

-->
```
</SPAWNING_PROMPT_TEMPLATE>

**MUST:**

You **MUST** explicitly state "The user has no opinions for this version." in **User's Opinions** section if the user found no opinions for the particular version of outline.
You **MUST** exhaust the list of the user's opinions for each version of the outline.

**MUST NOT:**

You **MUST NOT** write prose.
You **MUST NOT** invent examples.
You **MUST NOT** smooth out the author's voice.

## Response Handling

**MUST:**

You **MUST** honestly present what the `outline-generator` subagent responded.
You **MUST** unwrap the outer markdown codeblock of the response before outputing it.
You **MUST** include all the sections in **ONE SINGLE** markdown codeblock.

**MUST NOT:**

You **MUST NOT** include each section in **SEPARATE** markdown codeblocks.
