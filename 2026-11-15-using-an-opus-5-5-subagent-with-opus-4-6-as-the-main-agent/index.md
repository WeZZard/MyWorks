---
title: "Using an Opus 5.5 Subagent With Opus 4.6 as the Main Agent"
category: Programming
tags: [AI,Agent]
---

Yesterday I shared a [post on X](https://x.com/realWeZZard/status/2121766783636119690) showing how a Claude Opus 4.6 main agent paired with a Claude Opus 5.5 subagent creates a classic **Confused Deputy** problem in multi-agent systems. Readers in the replies asked a practical question: how do you spawn an Opus 5.5 subagent when your main Claude Code session runs on Opus 4.6?

Ask the main agent to spawn `claude-opus-5-5` on the fly in a prompt, and you hit a wall. Anthropic has tightened model selection across Claude Code's `Agent` tool and context forking. Today, **the only reliable way to run an Opus 5.5 subagent under an Opus 4.6 main agent is to define a custom subagent in `.claude/agents/` and pin its `model` field to the Model ID `claude-opus-5-5`.**

## Model Name, Model Alias, and Model ID

Claude Code's documentation distinguishes three terms that developers often conflate:

| Term | Purpose | Examples | Accepted in `model` Config? |
| :--- | :--- | :--- | :--- |
| **Model Name** | Human-readable product title shown in menus and documentation. | `Claude Opus 5.5`, `Claude Opus 4.6` | No |
| **Model Alias** | Dynamic shorthand that resolves to the latest default release in a tier. | `opus`, `sonnet`, `haiku`, `fable` | Yes (tracks latest version) |
| **Model ID** | Immutable backend identifier pinned to one model snapshot. | `claude-opus-5-5`, `claude-opus-4-6` | Yes (in session flags and subagent frontmatter) |

* **A Model Name is for humans alone:** Configuration files and CLI flags reject `Claude Opus 5.5` because the API expects a machine-readable identifier.
* **A Model Alias is a moving target:** `opus` resolves to whichever Opus generation Claude Code sets as the default, so a single alias cannot pin two generations of the same family side by side.
* **A Model ID pins a specific generation:** Passing `claude-opus-4-6` to the main session and `claude-opus-5-5` to a custom subagent locks each layer to an exact model snapshot.

## The Only Working Setup: A Predefined Custom Subagent

Claude Code stores custom subagents as Markdown files with YAML frontmatter in `.claude/agents/` (for one repository) or `~/.claude/agents/` (across all projects). Unlike ad-hoc `Agent` tool calls, the `model` field in subagent frontmatter accepts a full **Model ID**.

### Step 1: Define the `opus-55` Subagent

Create `.claude/agents/opus-55.md` (or `~/.claude/agents/opus-55.md`) and set `model` to `claude-opus-5-5`:

```markdown
---
name: opus-55
description: Specialized Claude Opus 5.5 worker for deep technical analysis and implementation tasks.
model: claude-opus-5-5
---

You are a focused technical specialist running in an isolated subagent context.
Complete the delegated engineering or analysis task and return a clear, structured result to the main agent.
```

* **The `name` field registers a named subagent type:** A named agent lets the main session bypass generic context forking and dispatch work directly to `opus-55`.
* **The `model` field pins the exact Model ID:** `model: claude-opus-5-5` overrides the parent session's `claude-opus-4-6` model whenever `opus-55` starts.

### Step 2: Launch the Main Session on Opus 4.6

Start Claude Code with the main session pinned to `claude-opus-4-6`:

```bash
claude --model claude-opus-4-6
```

Inside an existing interactive session, `/model claude-opus-4-6` switches the main model in place.

### Step 3: Delegate Work to the Predefined Subagent

From your `claude-opus-4-6` session, instruct the main agent to delegate the task to `opus-55`:

```text
Use the opus-55 subagent to ... [write whatever you want here]
```

When Claude Code invokes `opus-55`, the main coordinator stays on `claude-opus-4-6` while the subagent runs inside a fresh, isolated `claude-opus-5-5` context window.

## Why Every Other Workaround Fails (Verified on Claude Code v2.1.325)

Earlier versions of Claude Code let the built-in `Agent` tool switch models freely on the fly. Today, Claude Code blocks every zero-file workaround, including environment-variable alias overrides, or routes it back to the main agent's Opus model (Opus 4.6 in our example):

![A horizontal routing diagram titled "Subagent Model Routing in Claude Code (v2.1.325)." On the left, a Main Session Coordinator hub running claude-opus-4-6 branches into three dispatch paths. Path A, Context Fork (subagent_type: "fork"), copies signed thinking blocks and lands on a red "LOCKED TO PARENT — Runs Opus 4.6" outcome. Path B, Env Alias Override (ANTHROPIC_DEFAULT_OPUS_MODEL), spawns the built-in @general-purpose agent and also lands on the red "LOCKED TO PARENT — Runs Opus 4.6" outcome. Path C, Predefined Subagent (.claude/agents/opus-55.md), opens a Clean Context Window inside a highlighted "SOLE WORKING ESCAPE HATCH" lane and reaches a green "PINNED MODEL ID — Runs Opus 5.5" (claude-opus-5-5) outcome.](./figure-1-subagent-routing.png "Subagent Model Routing in Claude Code (v2.1.325)")

* **Prompting the `Agent` tool with a raw Model ID fails:** Claude Code restricts per-invocation `model` parameters on the built-in `Agent` tool and blocks the calling LLM from passing versioned Model IDs such as `claude-opus-5-5` at runtime.
* **Pinning the `opus` alias through environment variables fails:** A tempting workaround launches Claude Code with `ANTHROPIC_DEFAULT_OPUS_MODEL="claude-opus-5-5"` (even paired with `CLAUDE_CODE_SUBAGENT_MODEL="claude-opus-5-5"` and `CLAUDE_CODE_FORK_SUBAGENT=0`), switches the main session to `/model claude-opus-4-6`, and asks the `Agent` tool to spawn an `opus` subagent.
* **Built-in subagents still inherit Opus 4.6:** On Claude Code `v2.1.325`, asking the `Agent` tool to spawn an `opus` subagent dispatches to `@general-purpose` and runs on **Opus 4.6** (`Agent(...) Opus 4.6`), ignoring the `opus` alias override.
* **Generic subagent forks lock the parent model:** When Claude Code forks the main agent's context (`subagent_type: "fork"`), the child agent inherits the full conversation history and stays locked to `claude-opus-4-6`.
* **Named custom subagents remain the only escape hatch:** Invoking a predefined subagent from `.claude/agents/` opens a clean context window and reads `model: claude-opus-5-5` straight from frontmatter, bypassing both the fork lock and built-in `Agent` inheritance.

## Why Anthropic Locked Forked Contexts to the Same Model

Anthropic locks every forked context to its parent model—even within the Opus family—for two reasons: one cryptographic, one economic.

* **Cryptographic thinking-block signatures block cross-model replay (Anti-Distillation):** On frontier models such as Claude Opus 5.5, Anthropic omits raw chain-of-thought text by default (`display: "omitted"`) and binds each thinking block to an encrypted cryptographic `signature` to block chain-of-thought extraction, distillation, and cross-session replay.
* **Cross-model forks break signature verification:** A forked subagent copies the parent conversation's signed thinking blocks verbatim; replaying Opus 4.6's thinking blocks into Opus 5.5—or forking an Opus 5.5 transcript into another model—fails model-bound signature checks and returns `400 Invalid signature in thinking block` from the Messages API.
* **Prompt caching demands an exact per-model prefix match (Token Economics):** Anthropic scopes its prompt cache per model and matches prefixes byte for byte, so switching models on a forked full-history session invalidates the cached transcript and re-bills every historical token from scratch.

## How Clean-Context Delegation Creates the Confused Deputy

The exact mechanism that makes this setup work—opting out of context forking into a fresh subagent window—also explains why pairing an Opus 4.6 main agent with an Opus 5.5 subagent creates a **Confused Deputy**:

* **Direct prompts expose the full intent to Opus 5.5:** In a standalone `claude-opus-5-5` session, dual-use security or reverse-engineering prompts keep the user's high-level goal and low-level technical steps inside one context window, where Opus 5.5's stricter safeguards evaluate the full trajectory and block the request.
* **Subagent delegation strips away upstream intent:** When a `claude-opus-4-6` main session accepts the user's request and delegates a scoped technical subtask to `opus-55`, the predefined subagent starts with a clean slate and sees only a neutral, self-contained engineering prompt—never the upstream conversation that motivated it.

That is a textbook **Confused Deputy** in multi-agent systems. By locking full-history forks to the parent model while routing custom subagents into isolated context windows, Claude Code prevents cross-model thinking extraction—yet creates a clean context boundary that strips away the upstream intent signals single-session safeguards depend on.
