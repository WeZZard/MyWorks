---
name: polish
description: Polish the language in an English post, especially blog post drafts under `YYYY-MM-DD-slug/index.md`, into everyday technical English while preserving the author's meaning and voice.
---

# Polish

Use this skill when the user asks to polish the language in an English post.

This skill is for language polish, not argument design. Make the post clearer and cleaner without changing what it says. Use IELTS Writing assessment criteria as the diagnostic frame, but keep the register in everyday technical English.

## Responsibilities

- Preserve the author's meaning, stance, factual claims, and voice.
- Polish toward everyday technical English: clear, natural, direct, and readable by technical practitioners.
- Improve clarity, rhythm, grammar, transitions, and sentence shape.
- Diagnose language issues through the IELTS Writing criteria: Task Response / Achievement, Coherence and Cohesion, Lexical Resource, and Grammatical Range and Accuracy.
- Apply the repository's English prose rules from `AGENTS.md`.
- Keep Markdown structure, frontmatter, links, images, code blocks, inline code, and citations intact.
- Make the smallest revision that solves the prose problem unless the user asks for a heavier rewrite.

## When To Use

Use this skill for English-language posts, especially:

- Blog posts under `YYYY-MM-DD-slug/index.md`.
- Draft post paragraphs pasted into the conversation.
- Review passes on a post that ask for wording, flow, tone, grammar, or concision.

## When Not To Use

Do not use this skill when the user asks to:

- Review code behavior, architecture, or tests.
- Polish notes, documentation, captions, or other non-post prose unless the user frames them as part of a post.
- Invent new arguments, examples, research, or factual claims.

## Workflow

1. Identify the target post text. If the user gives a file path, read the relevant file. If the target is missing, ask one short question.
2. Identify the requested depth: light polish, copyedit, stronger rewrite, or line edit. If unspecified, default to a light polish.
3. Assess the passage against the IELTS-inspired criteria below before editing.
4. Revise only the language needed to improve the weak criteria. Do not redesign the argument unless the user asks.
5. If editing a file, patch only the relevant prose. Do not reformat unrelated sections.
6. If responding in chat, put the polished prose first. Add a short change note only when it helps the user review the revision.
7. Self-check before finishing: meaning preserved, no new claims, no broken Markdown, no near-idioms, no comma splices, no dangling modifiers.

## IELTS-Inspired Criteria

Use these criteria as an editing checklist, not as a rigid scoring system.

## Register

The target register is everyday technical English: the language of thoughtful engineering posts, technical blogs, and product notes.

**MUST:**

- Sound natural to a technical reader.
- Prefer plain verbs, concrete nouns, and idiomatic phrasing.
- Keep technical terms when they are accurate and familiar to the intended audience.
- Use contractions when they fit the author's voice and make the sentence sound natural.
- Keep the prose conversational enough for a blog post but precise enough for technical writing.

**MUST NOT:**

- Sound like an IELTS essay, academic paper, press release, marketing page, or documentation reference.
- Use inflated transitions such as `moreover`, `furthermore`, `in addition`, or `it can be concluded that` unless the sentence genuinely needs them.
- Replace a clear technical phrase with a vague general phrase.
- Make the prose breezy, chatty, or casual at the cost of precision.

### Task Response / Achievement

For a post, this means the prose fulfills the paragraph's purpose and supports the post's promise.

**Improve by:**

- Making claims precise.
- Cutting drift, repetition, throat-clearing, and unsupported asides.
- Keeping examples tied to the point they support.
- Clarifying vague referents such as `this`, `that`, `it`, and `they`.
- Flagging missing support instead of inventing facts.

**Do not:**

- Add new arguments, examples, citations, or conclusions.
- Turn a personal or editorial post into an exam-style answer.
- Flatten nuance to make the point look simpler than it is.

### Coherence and Cohesion

For a post, this means ideas move in a clear order and sentences connect without heavy-handed signposting.

**Improve by:**

- Keeping each paragraph centered on one idea.
- Strengthening topic sentences when the paragraph's role is unclear.
- Moving connective words closer to the ideas they connect.
- Replacing abrupt jumps with light transitions.
- Splitting overloaded sentences and merging choppy ones when rhythm improves.

**Do not:**

- Overuse connectors such as `moreover`, `furthermore`, `therefore`, or `in conclusion`.
- Reorder sections unless the user asks for structural editing.
- Hide a weak connection behind a transition word.

### Lexical Resource

For a post, this means the word choice is accurate, idiomatic, varied, and natural for technical writing.

**Improve by:**

- Choosing specific nouns and verbs over vague abstractions.
- Replacing repeated words only when repetition is accidental or dull.
- Fixing awkward collocations and non-native phrasing.
- Preserving technical terms, product names, API names, and the author's preferred terminology.
- Using standard idioms a native reader would recognize.

**Do not:**

- Swap simple words for ornate ones to sound advanced.
- Use near-idioms, mixed metaphors, or phrases that only sound idiomatic.
- Remove intentional repetition that gives the prose rhythm or emphasis.

### Grammatical Range and Accuracy

For a post, this means the prose is grammatically correct and sentence variety serves readability.

**Improve by:**

- Fixing agreement, tense, articles, prepositions, punctuation, and word order.
- Removing comma splices and dangling modifiers.
- Varying sentence length when a passage feels monotonous.
- Keeping modifiers next to what they modify.
- Using complex sentences only when they clarify relationships among ideas.

**Do not:**

- Add complexity for its own sake.
- Replace a clear short sentence with a long one to show grammatical range.
- Change quoted text unless the user explicitly asks to edit the quote.

## Style Rules

**MUST:**

- Omit needless words.
- Prefer active voice.
- Use concrete nouns and strong verbs.
- Keep one idea per paragraph.
- Keep related words together.
- Use the serial comma.
- Use standard idioms a native reader would recognize.
- Use `$N USD/month` for recurring monthly prices unless quoting a source verbatim.

**MUST NOT:**

- Smooth away the author's voice.
- Add new facts, examples, citations, claims, caveats, or conclusions.
- Change quoted text unless the user explicitly asks to edit the quote.
- Rewrite code, commands, API names, product names, or technical terms for style.
- Use near-idioms or mixed metaphors.
- Over-polish into bland, generic prose.
- Assign an IELTS band score unless the user explicitly asks. If asked, frame it as an approximate language diagnostic, not a formal score.

## Idiom Check

Before keeping a vivid phrase, ask:

1. Is this an established expression, or does it only sound like one?
2. Does the metaphor still hold one sentence later?

If either answer is no, replace it with a real idiom or plain language.

## Output

For file edits, report:

- The file changed.
- The nature of the polish.
- Any unresolved questions or places deliberately left unchanged.

For pasted post prose, return the polished prose directly. Keep explanations brief unless the user asks for a line-by-line rationale.
