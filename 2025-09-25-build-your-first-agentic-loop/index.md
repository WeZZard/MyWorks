---
title: "Build Your First Agentic Loop"
category: Programming
tags: [AI,Developer Tools]
isPublished: false
---

*Fun fact:* I'm currently ranked **third in daily cloud usage statistics
on Claude Count**. That's because I've been running Claude Code inside a
**24×7 agentic loop** to power my side project. While I sleep, the loop
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
minimal flow: the evaluator chooses the next action, spawns workers to use
tools, workers report results, and control returns to the evaluator until
the goal is met.

![A diagram titled “Main Loop” showing evaluators and workers interacting in a repeating five-step cycle where requests to evaluate a situation spawn workers, workers request task details, and responses spawn evaluators](basic_agentic_loop.png "Basic Agentic Loop")

However, to turn that flow into a working system, three components must
work together: a right **model**, **prompts** that enforce the contract,
and a **runtime** that provides tools and safely manages workers:

1. **Get the right model**
    Pick an advanced model that can:

    - Follow strict JSON formats under prompt pressure.
    - Stay disciplined about roles, actions, and IDs.
    - Reason sensibly about tool use without hallucination.

2. **Write prompts with contracts in mind**
    The backbone of your loop is a fixed-format schema. Every evaluator
    and worker must respond in this structure. This turns free-form LLM
    chatter into predictable, machine-readable communication.

3. **Support tools or sub-agents**
    Without tools, your loop is just self-talk. With CLI commands and
    workers, it can run tests, fetch data, patch code, or monitor
    systems. The evaluator--worker rhythm is the heartbeat.

------------------------------------------------------------------------

## Quickstart: Contract‑First Prompts

You’ve seen the loop and its roles. Now let’s turn that into working prompts by doing three things in order: define a minimal contract, write the Evaluator prompt to enforce it, and write the Worker prompt to execute it.

### 1) Define the minimal contract

Start with a fixed schema. Every message in the loop must adhere to it—no exceptions, no extra prose. This is what your validator will check and what your prompts will constantly reinforce.

``` json
{
  "version": "1.0",
  "role": "evaluator|worker",
  "action": "spawn|work|report|done",
  "task_id": "string",
  "payload": { "intent": "string", "inputs": {} },
  "result": { "status": "ok|fail|partial", "out": "summary", "artifacts": [] },
  "limits": { "max_depth": 3, "ttl_seconds": 1800 }
}
```

Field-by-field (concise):
- version: Pin schema version for safe evolution.
- role: "evaluator" or "worker" only.
- action: spawn | work | report | done.
- task_id: Stable per task; mint a new one only on spawn.
- payload.intent: Next objective, short and concrete.
- payload.inputs: Minimal, tool-ready parameters.
- result.status: ok | fail | partial.
- result.out: Terse human summary.
- result.artifacts: Paths/URLs/structured outputs.
- limits: Guardrails (max_depth, ttl_seconds); always propagate to spawned workers.

Validation tips:
- Reject outputs that break/omit required fields.
- On parse failure, re-prompt with “JSON only; no prose” and include the last valid example.

### 2) Write the Evaluator prompt

Evaluator: responsibilities
- Pick one action (spawn | work | report | done) and enforce the schema.
- Preserve task_id; mint a new one only on spawn.
- Respect limits (max_depth, ttl_seconds) and conclude with done when criteria are met.
- Output exactly one JSON object; no prose.

Evaluator prompt:

```markdown
You are the Evaluator. Reply with ONE JSON object only that matches this schema:
{ version, role, action, task_id, payload: { intent, inputs }, result: { status, out, artifacts }, limits }

Decide exactly one action: spawn | work | report | done.
- Preserve task_id unless spawning; on spawn, mint a new task_id for the child.
- Respect limits at all times (max_depth, ttl_seconds).
- Keep payload.intent short and concrete; payload.inputs minimal and tool‑ready.
- When done, set action:"done" and summarize outcome in result.out.

Selection hints:
- spawn: delegate a sub‑task needing tools or isolation.
- work: internal reasoning/plan refinement.
- report: surface intermediate results to record.
- done: goal met with sufficient evidence.
```

### 3) Write the Worker prompt

Worker: responsibilities
- Execute payload.inputs and return a structured report.
- Always return action:"report" with result.status, result.out, and artifacts.
- Output JSON only; never change role, task_id, limits, or add fields.
- Treat errors as data (result.status:"fail" + concise summary in result.out).

Worker prompt:

```markdown
You are a Worker. Perform payload.inputs as specified by the Evaluator.
Reply with ONE JSON object only.
- Always return action:"report".
- Always include result.status (ok|fail|partial), result.out (succinct summary), and artifacts (paths/URLs/structured outputs).
- Do not change role, task_id, or limits. Do not add extra fields or prose.
```

Putting it together:
- The Evaluator decides and, on spawn, produces a new task_id and a focused payload for the Worker.
- The Worker executes and reports; the Evaluator ingests reports and either spawns further work, continues internal work, or declares done.
- A validator between turns enforces the schema and short‑circuits invalid outputs.

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
- A runtime that can spawn workers safely.

With that, you can run Claude Code (or GPT-5 Codex, or GLM-4.5) in a
loop that works while you sleep.

Try it tonight. Tomorrow morning, you might wake up to progress already
made.
