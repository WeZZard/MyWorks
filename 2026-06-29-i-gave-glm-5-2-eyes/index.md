---
title: "I Gave GLM-5.2 Eyes"
category: Programming
tags: [AI,Agent]
---

Have you ever sent an image to GLM-5.2 in OpenCode? The model says it is text-only and cannot inspect visual content. You accept the limitation and move on.

![OpenCode prompt with an attached image where GLM-5.2 reports that it cannot inspect images.](./glm-5-2-not-spport-vision-task-1.png "Image Input Fails in GLM-5.2")

The hidden failure is worse. When GLM-5.2 works with browser-use tools, the tools capture screenshots, and the model confidently reports what it supposedly sees. But the model never saw a pixel. It read the AX tree, the accessibility metadata returned by a separate snapshot call, and treated that as visual verification. The AX tree can confirm that a button exists, but it cannot confirm whether the button is centered, whether the text is readable, or whether two screenshots match.

![OpenCode verification output where GLM-5.2 relies on an accessibility snapshot instead of actual pixels.](./glm-5-2-not-spport-vision-task-2.png "Accessibility Snapshot Mistaken for Vision")

To solve both problems, I built a plugin that gives GLM-5.2 eyes in OpenCode. This post covers the main lessons I learned while building it:

1. How to mix and match models with different capabilities without a model router or fusion models.
2. How to design agent-to-agent communication.
3. How to make skills trigger reliably on multimodal content.

## Installation and Usage

If you want the plugin right away, here is the install command:

```shell
opencode plugin opencode-vision -g
```

This plugin comes with a `vision` skill. To use it, you can just simply drag-and-drop an image to the input box.

![OpenCode session demonstrating an image prompt before the vision plugin handles it.](./example-drop-image-1.png "Image Prompt Before Vision Routing")

For the first time, you must pick a vision-capable model detected from your configured providers.

![OpenCode session where the plugin starts vision routing and discovers available image-capable models.](./example-drop-image-2.png "Discovering Vision Models")

Then the image would be evaluated with a subagent configured with a vision-capable model. GLM 5.2 in the main agent would get what the subagent get.

![OpenCode session asking the user to select a vision-capable model for image analysis.](./example-drop-image-3.png "Selecting a Vision Model")

This skill also works with images returned by computer-use and browser-use tools.

![OpenCode computer-use example where GLM-5.2 captures a Finder window with cua-driver, loads the vision skill, and returns a screen description.](./example-computer-use-1.png "Describing a Finder Window with Computer-use Tools")

## The Architecture

ZCode implements vision support by routing image input to a vision-capable model included in its official subscription plan. That is why ZCode can understand the images you send to it, and why that behavior disappears when you use GLM-5.2 through unofficial providers.

But OpenCode cannot configure a model router or fusion models. So how can we make OpenCode handle visual content?

Many providers available through OpenCode already offer vision-capable models: OpenAI ChatGPT, Kimi for Coding, OpenCode Go, and Ollama Pro/Max. With the primitives OpenCode already provides, we can build a lightweight architecture:

1. Create subagents that use vision-capable models to process visual content.
2. Delegate visual tasks to these subagents through a skill when needed.

With today's agent tooling, that design is enough to build the plugin.

Two details still matter:

1. Agent-to-agent communication design
2. What the skill description covers

Both are critical to the quality of vision-task results.

## Agent-to-agent Communication

Stable agent-to-agent communication usually starts with a rigid contract that structures subagent inputs and outputs.

To handle as many visual tasks as possible, that contract cannot be too narrow or rigid. For example, if we add a field for the task purpose but allow only a small set of values, our subagents cannot handle other kinds of work.

**Bad Design:**

The following code comes from my first agent-to-agent contract design. It had several design smells:

1. The `Image` object is designed for comparison tasks, but not every visual task is a comparison.
2. The `judgment` field covers only a limited set of visual tasks, and we cannot list every possible task when we design the skill.
3. The `judgment` field can contain only one object. What if I want to check an object's alignment on both the X and Y axes?

```typescript
interface Image { path: string; label: string; role: "baseline" | "current" | "reference" }
interface Request { 
    id: string
    images: [Image]
    judgment: Presence | Absence | Alignment | Ordering | Equality | Layout | Readability | State | Diff | Describe;
    criteria?: string;
    responseContract?: string;
}
interface Presence { kind: "presence"; subject: string; expectation: string }
interface Absence { kind: "absence"; subject: string; expectation: string }
interface Alignment { kind: "alignment"; subject: string; axis: string; expectation: string; tolerance: string }
interface Ordering { kind: "ordering"; direction: string; expected: string[] }
interface Equality { kind: "equality"; subjects: string[]; threshold: string }
interface Layout { kind: "layout"; expectations: string[] }
interface Readability { kind: "readability"; subject: string }
interface State { kind: "state"; subject: string; expectedState: string }
interface Diff { kind: "diff"; baseline: string; current: string }
interface Describe { kind: "describe"; focus: string }
```

**Good Design:**

A better approach is to let the agent design the contract using clear principles:

![Prompt template diagram showing how the main agent defines a visual task, images, response template, and response rules for a subagent.](./agent-to-agent-prompt-example.png "Dynamic Vision Subagent Prompt Template")

With this design, communication between agents stays structured while remaining dynamic enough to represent a wide range of visual tasks.

## Skill Description

People may think multimodal support is only about user input. However, tool results can introduce multimodal content too.

The skill description should cover cases where tool results include multimodal content. In OpenCode, this is straightforward because images in tool results have two recognizable traits:

```yaml
description: >-
  You **MUST** use the vision skill when your model is text-only (e.g.
  glm-5.2, deepseek-v4-pro) AND:
  ...
  (5) OR a tool result contains an image attachment the current model
  cannot see (attachments[].mime = "image/png",
  url = "data:image/png;base64,...");
```

## Limitations

**Native Multimodality:**

A plugin cannot add native multimodal support to a text-only model like GLM-5.2.

The model's training process sets that limit. As users, we cannot close the gap.

What we can do is route multimodal requests to another capable model and ask that model to return its findings to the text-only model as text. But multimodal content carries subtle details that text cannot fully express, even when a trained vision model can capture them. A "fused" model built this way is not as strong as a native multimodal model.

**Disable the Plugin:**

Sometimes you may switch to a vision-capable model like GPT. In this case, evaluate visual contents within the main agent can get better results due to the native multimodality understanding.

However, plugins installed with `opencode plugin` would not appear in OpenCode's plugin management UI.

In this case, you can simply prepend "You MUST not use the vision skill." to your prompt, then the vision skill comes with this plugin would not be invoked.

**Video Content:**

Models like Kimi K2.7 Code support video input. However, OpenCode does not accept video input. So this plugin also does not support video content.
