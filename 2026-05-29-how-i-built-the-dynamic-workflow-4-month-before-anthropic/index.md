---
title: "How I Built The Dynamic Workflow 4 Months Before Anthropic"
---

Last week, Opus 4.8 shipped with Claude Code **dynamic workflows**. Four months earlier, I had built an equivalent plugin, [charge](https://github.com/WeZZard/charge), on Opus 4.5: you give it a simple prompt, and it creates and manages subagent-driven workflow orchestrations.

I dropped the project soon after. Dynamically spawning subagent workflows and reusing them turned out to be a false need. Even so, subagent orchestration still sits at the center of my daily work in Claude Code—now through **[amplify](https://github.com/WeZZard/skills)** (`amplify@wezzard-skills`), which applies what I learned from `charge` via skills and hooks.

If you build agents, I hope this story helps you spot the next meaningful capability jump in a new model—and design systems like Claude Code’s dynamic workflow without repeating my detours. Anthropic does not publish implementation details or design notes; this post and open repos do.

## Why I Built Charge?

From Aug. 2025, I’d been using a long-running agentic loop with detailed plan files to drive development on my personal projects in Claude Code with Opus 4.1.

It was basically a subagent-driven loop system. Subagents are good for context segregation because LLMs work by next-token prediction, and one of the most efficient ways to improve a system’s bottom line is to keep unnecessary content out of the context.

This loop contains an evaluator and several executor subagents to carry out development, testing, troubleshooting, and integration gatekeeping in the plan. All of these steps benefit from the context segregation that subagent-driven design provides.

// TODO: Figure explain the production level loop

In Sep. 2025, I published [a post](https://wezzard.com/post/2025/09/build-your-first-agentic-loop-9d22) explaining how the system works. Two months later, Anthropic published a post that introduced the “harness” concept with a similar design.

But when Opus 4.5 was released, I found that because the subagent response contains information about the task running on the loop, the main agent sometimes didn’t follow the evaluator-executor pattern that comes with this loop but just proceeded to push the task to completion itself. At the same time, Claude Code had just introduced background tasks and parallel subagents. Two things changed at once, I noticed this leak-to-main-agent phenomenon often resulted in faster execution because the leaked tasks sometimes were decomposed and processed in parallel. Meanwhile, I had just spawned over 70 subagents in a file-processing task on Claude Code in Jan. 2026.

Adding it all up, we can see that starting from Opus 4.5, running and coordinating subagents got much easier. Then I had a question: what if I could create and manage reusable workflows driven by subagents and build dependencies between them by borrowing concepts from structured concurrent programming—task trees and directed acyclic graphs?

## Implementation Details and Design Philosophy

The implementation details of `charge` are quite simple—it is basically driven by prompts and guaranteed by dynamically generated schemas. Since [charge](https://github.com/WeZZard/charge) is open source, here I highlight some key points in the implementation that people might mistake for “magic.”

### Task Decomposition and Dependencies

The task decomposition and dependency building is achieved by the chain-of-thought technique with the following steps:

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

The tasks are stored in the `tasks` array and have a `depends_on` field to represent the task dependency. This JSON object will be used in the workflow execution.

### The Execution Engine

By reading the task dependency graph in the JSON object, Claude Code can just “magically” execute the tasks in the dependency order.

Anthropic implemented this part with a deterministic-algorithm-based execution engine written in JS, which I think is the right move for a system meant to orchestrate a large scale of subagents. Because LLMs work by next-token prediction, a prompt-based execution engine has to rely on the model to infer execution order and to generate the correct tool call to launch the next agent when a preceding task completes in the dependency graph.

However, the execution engine could be implemented with the generator pattern and run in the main agent:

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

With this design, the main agent of Claude Code can still orchestrate the workflow. This design counts on the model to generate the right tool call to run `complete-task.sh` when an agent completes its task and to spawn new subagents based on the tool output from `complete-task.sh`.

### Cost and Correctness

When a workflow is built and about to execute, `charge` leverages Claude Code’s plan mode to let the user review the decomposed workflow.

// TODO: A figure showing charge workflow confirmation with plan mode

This was because dynamically generating subagents based on tasks is billed as output tokens—the spawning prompts of those subagents are output by the main agent. This design can be seen as “progressive disclosure” in token consumption.

### Control and Steering

This is another edge `charge` has that Claude Code’s dynamic workflows do not. Because workflow orchestration in `charge` stays in the main agent, the user can interrupt and steer at any time during execution.

## Why I Call It A False Need

After using `charge` for a while, I found that the most reused workflows in the real world are better represented with deterministic algorithms. That work should be implemented in code, not prompts.

Introduce an LLM only when creativity is required. In reusable workflows, LLMs commonly appear in analysis tasks, diagnostic tasks, or “code laundering” tasks like laundering Bun from Zig to Rust, which Anthropic listed as a showcase of dynamic workflows. If you are creating something totally new, keeping the human in the loop and steering as you go is the right choice.

But even for analysis and diagnostic tasks, you can still write code to produce better-structured, more digestible tool outputs and to coalesce tool calls by inlining multiple tool calls in a script. That improves execution speed and reduces noise in the context. These optimizations matter because they can significantly improve workflow performance and the bottom line of the results—and we care about whether the analysis or diagnosis is actually right.

Research tasks are an exception, because research is too far from the results. There are still many judgments to make before turning research into action. I think that is why Claude Code bundles a `/deep-research` workflow.

So here I can draw a decision tree to help you pick the right tool:

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

With this decision tree, it comes down to:
- To create something totally new, we still need to keep the human in the loop to steer the agent as you go.
- To perform reusable workflows, we can have more economical options: build with OpenCode and an affordable model, or write code that only costs CPU time, not tokens.
And obviously, the first item is the bottleneck in my daily use of Claude Code.

Then I created `amplify` by borrowing the following design from `charge`:

1. Task dependency graph and per-task subagent.
2. The plan-based task graph review.
3. Execute in the main agent to allow steering as you go.

On top of that, to prevent Claude Code from ending prematurely, it also creates audit subagents to check whether the planned work was actually completed.
