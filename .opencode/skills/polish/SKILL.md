---
name: polish
description: Polish English post prose by delegating to the `polish-editor` subagent. Use for blog post files under `YYYY-MM-DD-slug/index.md` or pasted English post text.
---

# Polish

Use this skill as the shell around the `polish-editor` subagent.

This skill does not own the prose-polishing rules. Keep polishing methodology in the `polish-editor` subagent. The skill only identifies the input form, prepares the spawning prompt, invokes the subagent, and handles the same-form result.

## Responsibilities

- Identify whether the user supplied a file input or plain-text input.
- Preserve the input form through the whole workflow.
- Invoke the `polish-editor` subagent with the target, constraints, and output contract.
- Apply or return the subagent result without adding extra rewriting in the main agent.

## Supported Inputs

### File Input

Use file input when the user gives a file path, file address, or a post title that can be resolved to a repository file.

Examples:

- `polish 2026-06-29-i-gave-glm-5-2-eyes/index.md`
- `polish the post: "I Gave GLM-5.2 Eyes"`
- `polish this file: /path/to/post/index.md`

For file input, the polished artifact must remain a file. The subagent should edit the file in place and return the same path.

### Plain-text Input

Use plain-text input when the user pastes prose directly into the conversation and does not ask to edit a file.

For plain-text input, the polished artifact must remain plain text. The subagent should return only the polished text, preserving Markdown when the input is Markdown.

## Same-form Rule

**MUST:**

- File input -> edited file output.
- Plain-text input -> polished plain-text output.
- Keep Markdown as Markdown.
- Keep a sentence as a sentence when the user supplied one sentence.
- Keep a paragraph as a paragraph unless splitting improves readability.

**MUST NOT:**

- Convert file input into pasted full-file prose.
- Convert pasted text into a new file unless the user explicitly asks.
- Polish the prose in the main agent after the subagent returns.
- Add new arguments, examples, citations, or technical claims.

## Workflow

1. Identify the target. If the user gives a title, locate the matching post file first.
2. Decide `input_kind`: `file` or `plain_text`.
3. Decide the requested depth: `light polish`, `copyedit`, `stronger rewrite`, or `line edit`. If unspecified, use `light polish`.
4. Build the spawning prompt using the template below.
5. Invoke the `polish-editor` subagent.
6. For file input, verify the changed file and report the path plus a concise change note.
7. For plain-text input, return the polished text directly unless the user asks for notes.

## Spawning Prompt

Use this prompt shape when invoking the `polish-editor` subagent:

<SPAWNING_PROMPT_TEMPLATE>

```markdown
## Input Kind
file | plain_text

## Input Payload
For `file`: absolute or repository-relative file path.
For `plain_text`: exact text to polish.

## Requested Depth
light polish | copyedit | stronger rewrite | line edit

## User Constraints
Any explicit user requirements, terminology preferences, audience notes, or phrases to preserve.

## Output Contract
For `file`: edit the file in place and return the same file path only.
For `plain_text`: return only the polished text.
```

</SPAWNING_PROMPT_TEMPLATE>

## Response Handling

For file input:

- Treat the edited file as the output artifact.
- Read the diff if needed before reporting back.
- Do not paste the whole file unless the user asks.

For plain-text input:

- Return the subagent's polished text as the answer.
- Do not add a change explanation unless it helps or the user asks.

## Limits

**MUST NOT:**

- Duplicate detailed polishing methodology in this skill.
- Re-polish the subagent output in the main agent.
- Treat the subagent as stateful; include all needed context in the prompt.
- Ask for clarification when the target and requested depth are clear.
