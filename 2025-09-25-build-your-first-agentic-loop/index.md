---
title: "Build Your First 24/7 Agentic Loop"
category: Programming
tags: [AI,Developer Tools]
isPublished: false
---

*Fun fact:* I'm currently ranked **third in daily cloud usage statistics
on Claude Count**. That's because I've been running Claude Code inside a
**24/7 agentic loop** to power my side project. While I sleep, the loop
evaluates, spawns subagents, and keeps moving forward. When I wake up,
progress is already made.

But the magic isn’t tied to Claude; once you grasp the essence of the
configuration you can replicate it with models and agent runtimes that
implement the same contract.

Here's how you can build your own.

## The Secret Behind the Curtain

The truth is: the latest large-language models --- Claude 4, GPT-5 ---
have been **trained with agent tasks**. They "know" how to evaluate, plan,
call tools, and hand control back. You don't need a massive framework.
You just need a contract and a loop.

## The Essence of an Agentic Loop

To make “a contract and a loop” concrete, the diagram below shows the
minimal flow: the evaluator chooses the next action, spawns executors to
use tools, executors report results, and control returns to the evaluator
until the goal is met.

![A diagram titled “Main Loop” showing evaluators and executors interacting in a repeating five-step cycle where requests to evaluate a situation spawn executors, executors request task details, and responses spawn evaluators](basic_agentic_loop.png "Basic Agentic Loop")

However, to turn that flow into a working system, three components must
work together: a right **model**, **prompts** that enforce the contract,
and an **agent runtime** designed for tool use:

1. **Get the right model**
    Pick an advanced model that can:

    - Follow strict JSON formats under prompt pressure.
    - Stay disciplined about roles, actions, and IDs.
    - Reason sensibly about tool use without hallucination.

2. **Write prompts with contracts in mind**
    The backbone of your loop is a fixed-format schema. Every evaluator
    and executors must respond in this structure. This turns free-form LLM
    chatter into predictable, machine-readable communication.

3. **Support tools**
    Without tools, your loop is just self-talk. With CLI commands, it can
    run tests, fetch data, patch code, or monitor systems. Subagents
    aren’t even required, since you can spawn external agent instances to
    build the evaluator-executor heartbeat via the `bash` tool.

## Writing Your First Contract-Driven Prompts

You’ve seen the loop and its roles. Now we’ll wire real prompts with
Claude Code subagents and command to build a working loop that cleans up
TODOs and FIXMEs across a repository. No custom schema here — the contract
is exactly what your prompts already define. And yet the Claude 4 is one
of the right models to use for building a 24/7 agentic loop.

### 1) The Structure of the Loop

The loop is made up of three components:

- `cleanup` command
- `cleanup-evaluator` subagent
- `cleanup-executor` subagent

![A diagram titled “cleanup loop” showing how TODO/FIXME items are collected, reorganized by a cleanup-evaluator, executed by a cleanup-executor, and cycled back through a cleanup process in five repeating steps.](the_todo_fixme_loop.png "The TODO/FIXME Loop")

The `cleanup` command is the entry point for the loop, holding the
**main agent**. It firstly scans the repository for TODO/FIXME items and
prepares a working list. Then it passes the list to the
`cleanup-evaluator` subagent.

The `cleanup-evaluator` subagent triages and orders the list, then respond
the reorganized list and the next action `spawn(cleanup-executor)` to the
**main agent**.

The **main agent** then follows the response from the `cleanup-evaluator`
subagent, spawning a `cleanup-executor` subagent and passing the
reorganized list to it.

The `cleanup-executor` subagent then dequeue the first TODO/FIXME item
from the reorganized list, executing the item, updating the list when the
execution completed. Then it respond with updated list and the next action
`spawn(cleanup-evaluator)` to the **main agent**.

The **main agent** then follows the response from the `cleanup-executor`
subagent, spawning a `cleanup-evaluator` subagent and passing the updated
list to it, thereby returning to the beginning of the loop.

### 2) The Contract

The key of holding this loop is to make the **main agent** and the
subagents always follow the contract. The good news is that holding a
contract between the **main agent** and the subagents is deadly simple:
In this example, each subagent receives a JSON object with the following
format from the **main agent**:

```json
{
  "incomplete_items": [incomplete_item_list],
  "completed_items": [completed_item_list],
  "postponed_items": [postponed_item_list]
}
```

And responds with the following format to the **main agent**:

```json
{
  "incomplete_items": [reordered_incomplete_item_list],
  "completed_items": [completed_item_list],
  "postponed_items": [postponed_item_list],
  "next_action": "spawn(cleanup-executor)|spawn(cleanup-evaluator)|mission_complete"
}
```

### 3) Enforcing the Contract with Prompts

The contract is baked into the prompt itself. No hidden tricks—just
CAPITALIZED IMPERATIVES and relentless repetition until the model obeys.

The snippet below shows how the **main agent** is set to spawn a
`cleanup-evaluator` at the beginning of the loop.

````markdown path=cleanup.md
## MANDATORY: 2. SPAWN AN CLEANUP-EVALUATOR TO EVALUATE INCOMPLETE TODOs and FIXMEs

You MUST spawn an cleanup-evaluator subagent to evaluate the gap between the incomplete TODOs and FIXMEs and the existing situation.

You SHALL ALWAYS send the cleanup-evaluator with a JSON object of the following format:

```json
{
  "incomplete_items": [incomplete_item_list],
  "completed_items": [completed_item_list],
  "postponed_items": [postponed_item_list]
}
```
````

On the cleanup-evaluator side, we should also enforce the contract.

````markdown path=cleanup-evaluator.md
## MANDATORY: PARSE THE RECEIVED JSON OBJECT

YOU WILL RECEIVE a JSON object of the following format:

```json
{
  "incomplete_items": [incomplete_item_list],
  "completed_items": [completed_item_list],
  "postponed_items": [postponed_item_list]
}
```
````

Once the cleanup-evaluator is about to end the task, it shall prepare to
respond to the main agent with the format of the contract. In this
example, its `next_action` is always to spawn a cleanup-executor.

````markdown path=cleanup-evaluator.md
## MANDATORY: RESPONSE BACK TO THE MAIN AGENT

You SHALL response with the [reordered_incomplete_item_list], [completed_item_list], [postponed_item_list] to the next subagent with the JSON object of the following format:

```json
{
  "incomplete_items": [reordered_incomplete_item_list],
  "completed_items": [completed_item_list],
  "postponed_items": [postponed_item_list],
  "next_action": "spawn(cleanup-executor)|mission_complete"
}
```

The `next_action` field SHALL BE `mission_complete` when NO ITEMS LEFT in [reordered_incomplete_item_list].

Otherwise, the `next_action` field SHALL BE `spawn(cleanup-executor)`.
````

Back to the main agent, it shall follow the response from the
`cleanup-evaluator` subagent, spawning a `cleanup-executor` subagent and
passing the lists to it.

````markdown path=cleanup.md
## MANDATORY: 3. UNDERSTANDS THE CLEANUP-EVALUATOR'S RESPONSE

The cleanup-evaluator subagent ALWAYS is the core of the workflow.

YOU MUST OBEY THE DESCISION OF THE CLEANUP-EVALUATOR IN [next_action].
You SHALL NEVER CHANGE THE DESCISION OF THE CLEANUP-EVALUATOR in [next_action].

The [next_action] COULD BE: `spawn(cleanup-executor)` | `mission_complete`:

The [next_action_details] COULD BE:

```json
{
  "type": "todo|fixme",
  "id": [next_item_id],
  "file": [next_item_file],
  "line": [next_item_line],
  "content": [next_item_content]
}
```

OR

```json
{
  "type": "mission_complete"
}
```

The cleanup-evaluator subagent SHALL NEVER know if it is the last time to evaluate until the [next_action] of a spawned cleanup-evaluator turns out to be `mission_complete`.

### MANDATORY: ALWAYS TRANSFER [incomplete_items], [completed_items], [postponed_items] FROM THE CLEANUP-EVALUATOR'S RESPONSE TO THE NEXT SUBAGENT

YOU MUST transfer the [incomplete_items], [completed_items], [postponed_items] from the cleanup-evaluator's response to the next subagent with the JSON object of the following format:

```json
{
  "incomplete_items": [incomplete_item_list],
  "completed_items": [completed_item_list],
  "postponed_items": [postponed_item_list],
}
```

````

This time, the contract would allow the main agent to spawn a
`cleanup-executor` subagent to execute the next TODO/FIXME item. However,
we still need to instruct the **main agent** to follow the responses from
subagents other than the `cleanup-evaluator`:

````markdown path=cleanup.md
## MANDATORY: 4. UNDERSTAND THE RESPONSE FROM OTHER SUBAGENTS

All the subagents other than the cleanup-evaluator subagent SHALL ALWAYS response with a JSON object of the following format:

```json
{
  "incomplete_items": [next_incomplete_item_list],
  "completed_items": [next_completed_item_list],
  "postponed_items": [next_postponed_item_list],
  "next_action": "spawn(cleanup-evaluator)",
}
```

### MANDATORY: ALWAYS READ Subagent's Response to Decide Next Action

The [next_action] is ALWAYS to spawn an cleanup-evaluator subagent.

You MUST SEND the cleanup-evaluator with the JSON object of the following format:

```json
{
  "incomplete_items": [next_incomplete_item_list],
  "completed_items": [next_completed_item_list],
  "postponed_items": [next_postponed_item_list],
}
```
````

At last, the **main agent** needs to know when to end the loop:

````markdown path=cleanup.md
## MANDATORY: 5. HANDLING MISSION COMPLETE

If `next_action` in the response from the cleanup-evaluator subagent is `mission_complete`, then the mission is completed.

You SHALL STOP ALL THE SUBAGENTS AND EXIT THE WORKFLOW.
````

------------------------------------------------------------------------

## Example Tech Stacks

- **Claude Code**: commands + sub-agents, easy to wire into a loop.
- **Codex**: tool-use and CLI integrations.
- **Chinese open-source models**: GLM-4.5, Qwen3-Coder, DeepSeek, Kimi
    --- lower cost, flexible.

------------------------------------------------------------------------

## Running 24×7

- Use restart scripts or supervisors.
- Keep logs + artifacts for recovery.
- Enforce depth/time/budget caps.
- Add a human pause flag for safety.

------------------------------------------------------------------------

## GPT-5 Codex: A Step Forward, Not a Magic Fix

OpenAI's **GPT-5 Codex** is marketed as a model built *for coding and
agentic tasks*. Reports suggest:

- Better structured outputs and contract obedience.
- Longer autonomous runs (hours instead of minutes).
- Smarter tool use and error recovery.

This is good news for minimal loops: GPT-5 Codex raises the ceiling. You
can expect fewer broken JSON blobs, more reliable CLI decisions, and
longer sessions without drift.

But don't mistake it for a silver bullet:

- **Validators are still required** --- no model is perfect at JSON
under stress.
- **Persistence is still required** --- even GPT-5 can forget across
long cycles.
- **Safety rails are still required** --- autonomous CLI runs can go
wrong fast.

**Optimistic but cautious takeaway:** GPT-5 Codex makes contract-first
loops more practical, but it doesn't replace contracts, logs, and
guardrails. Your loop is still only as strong as its structure.

------------------------------------------------------------------------

## Conclusion

Building a 24×7 loop doesn't require LangChain or AutoGen. All you need
is:

- A model trained with agent tasks.
- A prompt-enforced contract.
- A runtime that can spawn executors safely.

With that, you can run Claude Code (or GPT-5 Codex, or GLM-4.5) in a
loop that works while you sleep.

Try it tonight. Tomorrow morning, you might wake up to progress already
made.
