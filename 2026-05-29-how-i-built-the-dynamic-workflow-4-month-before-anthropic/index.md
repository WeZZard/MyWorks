---
title: "How I Built The Dynamic Workflow 4 Months Before Anthropic"
---

Last week, Opus 4.8 shipped with Claude Code **dynamic workflows**. Four months earlier, I had built an equivalent plugin, [charge](https://github.com/WeZZard/charge), on Opus 4.5: you give it a prompt, and it creates and orchestrates reusable subagent-driven workflows.

I abandoned the project soon after. Dynamically spawning and reusing subagent workflows turned out to be a false need. Subagent orchestration nonetheless remains central to my daily work in Claude Code—now through **[amplify](https://github.com/WeZZard/skills)** (`amplify@wezzard-skills`), which applies lessons from `charge` through skills and hooks.

If you build agents, I hope this story helps you spot the next meaningful capability jump in a new model—and design systems like Claude Code’s dynamic workflow without repeating my detours. Anthropic does not publish implementation details or design notes; this post and open repos do.

## Why I Built Charge?

From Aug. 2025, I had been using a long-running agentic loop with detailed plan files to drive development on my personal projects in Claude Code with Opus 4.1.

In practice, it was a subagent-driven loop. Subagents segregate context well because LLMs work by next-token prediction; one of the most efficient ways to improve a system’s bottom line is to keep unnecessary content out of the context.

The loop includes an evaluator and several executor subagents that carry out development, testing, troubleshooting, and integration gatekeeping against the plan. Each step benefits from the context segregation that subagent-driven design provides.

// TODO: Figure out how to explain the production-level loop

In Sep. 2025, I published [a post](https://wezzard.com/post/2025/09/build-your-first-agentic-loop-9d22) explaining how the system works. Two months later, Anthropic published a post that introduced the “harness” concept with a similar design.

When Opus 4.5 shipped, I found that subagent responses now carried enough detail about the in-loop task that the main agent would sometimes skip the evaluator-executor pattern that comes with this loop and push work to completion on its own. At the same time, Claude Code had just introduced background tasks and parallel subagents—two shifts at once. The leak-to-main-agent phenomenon often ran faster anyway, because leaked tasks were sometimes decomposed and processed in parallel. By Jan. 2026, I had spawned more than 70 subagents in a single file-processing task on Claude Code.

Adding it all up, from Opus 4.5 onward, running and coordinating subagents became much easier. That raised a question: what if I could create and manage reusable workflows driven by subagents, and build dependencies between them by borrowing concepts from structured concurrent programming—task trees and directed acyclic graphs?

## Implementation Details and Design Philosophy

The implementation details of `charge` are simple: prompts drive it, and dynamically generated schemas enforce it. [charge](https://github.com/WeZZard/charge) is open source; below I highlight implementation points that readers often mistake for “magic.”

### Task Decomposition and Dependencies

Task decomposition and dependency building are achieved by the chain-of-thought technique in the following steps:

1. Understand the user’s intent
2. Identify repetitive patterns in the user’s intent
3. Identify task boundaries so each task has a single, clear purpose and identifiable inputs and outputs.
4. Define task properties used in the task’s schema.
5. Map dependencies to a task dependency graph.

By following this chain of thought, a simple user prompt can be converted into a JSON object that represents the dependency graph of the decomposed tasks:

```json
{
  "workflow_name": "[string]",
  // ...
  "tasks": [
    {
      "id": "[string]",
      "name": "[string]",
      "description": "[string]",
      // ...
      "input": [
        {"field": "[string]", "type": "[string]", "description": "[string]"}
      ],
      "output": [
        {"field": "[string]", "type": "[string]", "description": "[string]"}
      ],
      "depends_on": ["[string]"]
    }
  ],
  ...
}
```

Tasks live in the `tasks` array; each has a `depends_on` field for its dependencies. The workflow executor consumes this JSON object.

### The Execution Engine

Read the task dependency graph from that JSON object, and Claude Code can “magically” run tasks in dependency order.

Anthropic implemented this part with a deterministic-algorithm-based execution engine written in JS, which I think is the right move for a system meant to orchestrate subagents at large scale. LLMs work by next-token prediction; a prompt-based execution engine must rely on the model to infer execution order and to emit the correct tool call to launch the next agent when a predecessor finishes in the dependency graph -- and this is not guaranteed true.

However, despite of writing all the subagents with JS, we could implement the engine with the generator pattern and run in the main agent:

```shell
# Main agent found task 1 is completed
# then call the `complete-task.sh` tool.
# `complete-task.sh` marks `task_1` as completed
# and returns the next tasks.
$> complete-task.sh task_1
{
	"next_tasks": [
	  {
		  "name": "task_2",
		  "description": "..."
	  },
	  {
		  "name": "task_3",
		  "description": "..."
	  }
	],
	"execution_order": "parallel"
}
```

With this design, the main agent of Claude Code still orchestrates the workflow. It counts on the model to call `complete-task.sh` when an agent finishes a task and to spawn new subagents from the tool output.

### Cost and Correctness

When a workflow is built and about to execute, `charge` leverages Claude Code’s plan mode to let the user review the decomposed workflow.

// TODO: A figure showing charge workflow confirmation with plan mode

That mattered because dynamically generating subagents from tasks is billed as output tokens—the main agent outputs the spawning prompts for those subagents-which is way more expensive than input tokens. You can read the design as “progressive disclosure” in token consumption.

### Control and Steering

Here `charge` has another edge over Claude Code’s dynamic workflows. Because workflow orchestration in `charge` stays in the main agent, you can interrupt and steer at any point during execution.

## Why I Call It a False Need

After using `charge` for a while, I found that the most reused workflows in the real world are better represented with deterministic algorithms. That work belongs in code, not prompts.

Introduce an LLM only when creativity is required. In reusable workflows, LLMs commonly appear in analysis tasks, diagnostic tasks, or “code laundering” tasks like laundering Bun from Zig to Rust, which Anthropic listed as a showcase of dynamic workflows. If you are creating something totally new, keeping the human in the loop and steering as you go is the right choice.

Even for analysis and diagnostic tasks, you can still write code to produce better-structured, more digestible tool outputs and to coalesce tool calls by inlining multiple tool calls in a script. That improves execution speed and reduces noise in the context. These optimizations matter because they can significantly improve workflow performance and the bottom line of the results—and we care about whether the analysis or diagnosis is actually right.

Research tasks are an exception. Research sits too far from the results; many judgments remain before you turn research into action. I think that is why Claude Code bundles a `/deep-research` workflow.

Here is a decision tree to help you pick the right tool:

// TODO: Create diagram for the following decision tree

```
-+ Are you creating something totally new?
 |
 +-- YES -> Use your agent normally and keep the human in the loop
 +-+ NO -> Is creativity required for the task?
   |
   +-+ YES -> Does getting it right matter?
   | |
   | +-+ YES -> Does the cost matter?
   | | |
   | | +-- Pick OpenCode with an affordable model like DeepSeek. Write code to accomplish the deterministic steps and compose a well-organized context, then delegate the creative part to the agent or its subagents
   | | +-- Pick Claude Code. Write code to accomplish the deterministic steps and compose a well-organized context, then delegate the creative part to the agent or its subagents
   | +-- NO -> Use the dynamic workflow
   +-- NO -> Just write the code
```

## Where I Landed

With that decision tree in hand, it comes down to:
- To create something totally new, we still need to keep the human in the loop to steer the agent as we go.
- To perform reusable workflows, we can choose more economical options: build with OpenCode and an affordable model, or write code that only costs CPU time, not tokens.

The first item is the bottleneck in my daily use of Claude Code.

Then I created `amplify` by borrowing the following design from `charge`:

1. Task dependency graph and per-task subagent.
2. The plan-based task graph review.
3. Execute in the main agent to allow steering as you go.

// TODO Figures about amplify plan mode

On top of that, to prevent Claude Code from ending prematurely, it also introduces audit subagents to check whether the planned work was actually completed.

// TODO Figures about audit subagents
