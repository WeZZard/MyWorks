---
title: "How I Built The Dynamic Workflow 4 Months Before Anthropic"
---

Last week, Opus 4.8 shipped with Claude Code **dynamic workflows**. Four months earlier, I built an equivalent plugin [charge](https://github.com/WeZZard/charge) based on Opus 4.5 to create and manage subagent-based workflow orchestrations start from a simple prompt.

However, I dropped that project soon after I created it because I just have found dynamically creating subagent-driven workflows and reusing them is a fake requirement. Despite of that, today, the subagent-based orchestration is still at the center of my daily work in Claude Code but evoked in another way -- **[amplify](https://github.com/WeZZard/skills)** (`amplify@wezzard-skills`) -- forged with what I learned in building `charge`, via skills and hooks.

I think the process that I built and polished `charge` and finally settled in `amplify` can inspire other agent authors to: 

1. Find the next significant capability improvement in a large language model.
2. Have an understanding on top of my learning in designing systems like “Claude Code Dynamic Workflow”.

Anthropic does not document the implementation details and the design notes; open repos and a clear story do.

## Why I Built Charge?

From Aug, 2025, I’d been using a long running agentic loop with  detailed plan files to drive the development jobs in my personal projects on Claude Code with Opus 4.1.

It is basically a subagent driven loop system. Subagents are good for context segregation because the nature of LLM is next token prediction and one of the most efficient way to improve the bottom-line of system is to prevent unnecessary contents appeared in the context.

This loop contains an evaluator and several executor subagents to proceed the development, testing, troubleshooting and integration gatekeeping in the plan. All these jobs enjoy the context segregation brought by the subagent-driven design.

// TODO: Figure explain the production level loop

In Sep, 2025, I published [a post](https://wezzard.com/post/2025/09/build-your-first-agentic-loop-9d22) explained how the system works. Two months later, Anthropic published the post that introduced the “harness” concept with a similar design.

But when Opus 4.5 was released, I found that because the subagent response contains information about the task running on the loop, the main agent sometimes didn’t not follow the evaluator-executor pattern that comes with this loop but just proceed to push the task to completion itself. And since Claude Code had just introduced background tasks and parallel subagents at the same time, it was observed that this leak-to-main-agent phenomenon often resulted in a faster execution speed because the leaked tasks sometimes were decomposed and processed in parallel. In the meanwhile, I have just spawned over 70 subagents in a file processing task on Claude Code in Jan, 2026. 

Adding all this up, we can know that starting from Opus 4.5, the capability of orchestrating subagents was significantly improved. Then I just had the question: what if I can create and manage reusable workflows that are driven by sub-agents and to build dependencies between the subagents by borrowing the concepts from structural concurrent programming -- task trees and directed acyclic graphs?

## Implementation Details and Design Philosophy

The implementation details of `charge` is quite simple -- it is basically driven by prompts and guaranteed by dynamically generated schemas. Since [charge](https://github.com/WeZZard/charge) is open source, here I just highlight some key points in the implementation details that people may think it like a “magic”.

### Task Decomposition and Dependencies

The task decomposition and dependency building is achieved by the chain-of-thought technique with the following steps:

1. Understand the user’s intent
2. Identify repetitive patterns in the user’s intent
3. Identify task boundaries to make each task has a single, clear purpose and identifiable inputs and outputs.
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

Anthropic implemented this part with a deterministic-algorithm-based execution engine written in JS, which I think is a right move to build a system that aims at orchestrating a large scale of subagents. Since the nature of LLM is the next-token prediction, a prompt-based execution engine means to count the execution order on the model can generate a correct tool call to launch an agent executing the next task when a preceding task is completed in the dependency graph.

However, the execution engine could be implemented with the generator pattern and running in the main agent:

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
		  "description: "..."
	  },
	  {
		  "name": "task_3",
		  "description: "..."
	  }
	]
	"execution_order": "parallel"
}
```

With this design, we can still make the workflow orchestrated by the main agent of Claude Code. This just counts on the model to generate the right tool call to perform `complete-task.sh` when an agent completed its task and spawn new subagents based on the `complete-task.sh`’s tool outputs.

### Cost and Correctness

When a workflow is built and about to execute, `charge` leverages Claude Code’s plan mode to let the user review the decomposed workflow.

// TODO: A figure showing charge workflow confirmation with plan mode

This was because dynamically generating subagents based on tasks  is billed as output tokens -- the spawning prompts of those subagents are output by the main agent. This design can be seen as a “progressive disclosure” in token consumptions.

### Control and Steering

This is also another edge that `charge` has but Claude Code Dynamic Workflow does not. Since the workflow orchestration of `charge` stays in the main agent, user can interrupt and steer at any time during the execution.

## Why I Call It A Fake Requirement

After using `charge` for a while, I just have found the most reused workflows in the real world are more appropriate to represent with deterministic algorithms. These work shall be implemented with code but not prompt.

LLM shall be introduced only when creativity is a must. In reusable workflows, LLMs are commonly seen in analysis tasks, diagnostic tasks or “code laundering” tasks like laundering bun from Zig to Rust as Anthropic listed as a showcase of the Dynamic Workflow. If you were creating something totally new, keeping the human in the loop and steer in time is the right choice.

But even for analysis tasks and diagnostic tasks, you can still write code to create better structured and digestible tool outputs and even to coalesce tool calls by inlining multiple tool calls in a script. This will improve the workflow execution speed and reduce the noises in the context. These optimizations matter because they can significantly improve the workflow performance and the bottom-line of the results and we just care about the feasibility of the analysis and diagnostic results.

However, research task is an exception -- because research is too far away from the results. There are still a lot of judgements to make before bringing the research results into action. And I think this is the reason why there is a `/deep-research` workflow bundled with Claude Code.

So here I can draw a decision tree to help you pick the right tool:

```
-+ Are you creating something totally new?
 |
 +-- YES -> Use your agent normally and keep the human in the loop
 +-+ NO -> Is creativity required for the task?
   |
   +-+ YES -> Does the feasibility matter?
   | |
   | +-+ YES -> Does the cost matter?
   | | |
   | | +-- Pick OpenCode with an affordable model like DeepSeek. Write code to accomplish the deterministic steps and compose a well organized context, then delegate the creative part to the agent or its subagents
   | | +-- Pick Claude Code. Write code to accomplish the deterministic steps and compose a well organized context, then delegate the creative part to the agent or its subagents
   | +-- NO -> Use the dynamic workflow
   +-- NO -> Just write the code
```

## The Settlement

With this decision tree, we can clearly see that:
- To create something totally new, we still need to keep the human in the loop to steer the agent in time.
- To perform reusable workflows, we can have more economical solutions either to build with OpenCode and an affordable model or write code that just burn your CPU time.
And obviously, the first one is the bottleneck for a user work with Claude Code.

Then I just created `amplify` by borrowing the following design design from `charge`:

1. Task dependency graph and per-task subagent.
2. The plan-based task graph review.
3. Execute in the main agent to allow steer in time.
