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
work together: a right model, prompts that enforce the contract, and a
runtime that provides tools and safely manages workers.

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

## A Minimal Contract

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

------------------------------------------------------------------------

## Example Prompts

### Evaluator

```markdown
    You are the Evaluator. Reply with ONE JSON object only.
    Decide the next step: spawn a worker, work, report, or done.
    Preserve task_id unless spawning.
    Respect limits.
```

### Worker

```markdown
    You are a Worker. Perform payload.inputs.
    Reply with ONE JSON object only.
    Always return action:"report", result.status, result.out, and artifacts.
```

------------------------------------------------------------------------

## Example Tech Stacks

- **Claude Code**: commands + sub-agents, easy to wire into a loop.\
- **Codex**: tool-use and CLI integrations.\
- **Chinese open-source models**: GLM-4.5, Qwen3-Coder, DeepSeek, Kimi
    --- lower cost, flexible.

------------------------------------------------------------------------

## Running 24×7

- Use restart scripts or supervisors.\
- Keep logs + artifacts for recovery.\
- Enforce depth/time/budget caps.\
- Add a human pause flag for safety.

------------------------------------------------------------------------

## GPT-5 Codex: A Step Forward, Not a Magic Fix

OpenAI's **GPT-5 Codex** is marketed as a model built *for coding and
agentic tasks*. Reports suggest:\

- Better structured outputs and contract obedience.\
- Longer autonomous runs (hours instead of minutes).\
- Smarter tool use and error recovery.

This is good news for minimal loops: GPT-5 Codex raises the ceiling. You
can expect fewer broken JSON blobs, more reliable CLI decisions, and
longer sessions without drift.

But don't mistake it for a silver bullet:\

- **Validators are still required** --- no model is perfect at JSON
under stress.\
- **Persistence is still required** --- even GPT-5 can forget across
long cycles.\
- **Safety rails are still required** --- autonomous CLI runs can go
wrong fast.

**Optimistic but cautious takeaway:** GPT-5 Codex makes contract-first
loops more practical, but it doesn't replace contracts, logs, and
guardrails. Your loop is still only as strong as its structure.

------------------------------------------------------------------------

## Conclusion

Building a 24×7 loop doesn't require LangChain or AutoGen. All you need
is:\

- A model trained with agent tasks.\
- A prompt-enforced contract.\
- A runtime that can spawn workers safely.

With that, you can run Claude Code (or GPT-5 Codex, or GLM-4.5) in a
loop that works while you sleep.

Try it tonight. Tomorrow morning, you might wake up to progress already
made.
