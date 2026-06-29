---
title: "I Gave GLM-5.2 Eyes"
category: Programming
tags: [AI,Agent]
---

Have you ever thrown a picture at GLM-5.2 in OpenCode? The model explains that it is a text-only model and cannot see visual components. You accept the limitation and move on.

// TODO: Figure

The hidden failure is worse. When GLM-5.2 works with browser-use tools, it captures screenshots and reports confidently what it sees. But it never saw a pixel. It read the AX tree — the accessibility metadata available through a separate snapshot call — and passed it off as visual verification. The AX tree can confirm a button exists. It cannot confirm whether the button is centered, whether the text is readable, or whether two screenshots match.

// TODO: Figure

To solve these problems, I built a plugin to give GLM 5.2 eyes on OpenCode. This post notes the key takeaways I learned in the building process, including:

1. A lightweight architecture of mix-and-match models in agent systems.
2. How to design agent-to-agent communications.
3. How to improve skills trigger coverage rate against multimodal content.

## Installation & Introduction

You may too busy to read up the entire post. So here is the installation command to get the plugin immediately:

```shell
opencode plugin opencode-vision -g
```

// TODO: Drop picture to use

// TODO: Select the model (will be persisted and could re-select with prompt)

// TODO: Success pic

// TODO: Other usage: Pass a file path

## The Architect

Zhipu ships ZCode with an MCP that adds vision support to GLM models. This is the reason why ZCode can understand the images you sent to it. So, do we need to build an MCP for OpenCode as well?

No. Building an MCP means to:

1. Either hardcodes OpenCode's authentication store to reuse its configured providers or introduce a managed authentication layer. The first approach is unstable and the later costs too much.
2. Implement a robust inter-process communication management and MCP server lifecycle management. Both of these are trivial if you are building a demo but difficult to ship production code.

So, introducing MCP is a bad idea here.

On the other hand, most plans that supported by OpenCode provide vision-capable models: OpenAI ChatGPT, Kimi for Coding, OpenCode Go, Ollama Pro/Max...

Obviously, based on primitives provided by OpenCode, a more lightweight architecture would be:

1. Create subagents that specified a vision-capable model to process visual contents.
2. Delegate visual tasks to these subagents in time with a skill.

With AI agent nowadays, we can easily implement the plugin based on just this intuition.

However, there are two points that you still need to pay attention:

1. The agent-to-agent communication design
2. The skill description's contents

Both of them are critical to improve the vision tasks result quality.

## Agent-to-agent Communication

To build stable agent-to-agent communication, we usually introduce a rigid contract to structure the subagents' inputs and outputs.

However, to capture visual tasks as much as possible, the contract cannot be too constrained or rigidly fixed. For example, if we build a contract with a field to describe the purpose of a task, and we only provide a limited set of purposes as minimum values, our subagents will never be able to perform other types of work.

// TODO: Example

The smarter way here is to allow the agent to design the contract itself under a set of established principles.

// TODO: Example

With this design, the communication between the agents are now structured, but also dynamic enough to convey any visual tasks.

## Skill Description

People may think handling multimodal contents is all about to handle the user inputs. However, tool results can also introduce multimodal content.

The skill description should mention the case where tool results carry multimodal content. In OpenCode, this is very simple because image contents in the tool results have two traits.

// TODO: Example

## Limitations

In fact, we can never add native multimodal support to a pure-text model like GLM 5.2.

This was decided by the model training process. We can never fill the gap as a model user.

What we can do is to route multimodal requests to another capable model and ask that model to communicate with the pure text one in text. And since multimodal contents always have more unspeakable subtleness that texts cannot convey but the trained weight can capture, a "fused" model implemented with this approach is not as perfect as using a native multimodal model.
