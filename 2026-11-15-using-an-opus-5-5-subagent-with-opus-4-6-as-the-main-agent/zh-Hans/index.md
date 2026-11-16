---
title: "在 Opus 4.6 主 agent 下使用 Opus 5.5 subagent"
category: Programming
tags: [AI,Agent]
---

昨天我在 X 上分享了一篇[文章](https://x.com/realWeZZard/status/2121766783636119690)，展示了 multi-agent 系统里用 Claude Opus 4.6 主 agent 搭配 Claude Opus 5.5 subagent，是怎么引发经典的**混淆代理人**（Confused Deputy）问题的。评论区有读者问到了一个很实际的点。如果 Claude Code 的主 session 跑在 Opus 4.6 上，该怎么生成 Opus 5.5 subagent？

想在 prompt 里让主 agent 临时生成 `claude-opus-5-5`，直接就会碰壁。Anthropic 收紧了 Claude Code 里 `Agent` 工具和 context forking 的模型选择规则。目前，**要在 Opus 4.6 主 agent 下运行 Opus 5.5 subagent，唯一可靠的做法是在 `.claude/agents/` 下定义自定义 subagent，把 `model` 字段固定为 Model ID `claude-opus-5-5`。**

## Model Name、Model Alias 和 Model ID

Claude Code 文档区分了开发者常混用的三个术语：

| 术语 | 用途 | 示例 | 可用于 `model` 配置？ |
| :--- | :--- | :--- | :--- |
| **Model Name** | 供人阅读的产品名称，用于菜单和文档展示。 | `Claude Opus 5.5`、`Claude Opus 4.6` | 不能 |
| **Model Alias** | 动态简写，会自动解析为对应档位的最新默认版本。 | `opus`、`sonnet`、`haiku`、`fable` | 可以（跟随最新版本） |
| **Model ID** | 不可变的后端标识符，锁定到具体的模型快照。 | `claude-opus-5-5`、`claude-opus-4-6` | 可以（用于 session flags 和 subagent frontmatter） |

* **Model Name 只是给人看的**。配置文件和 CLI 参数都不接受 `Claude Opus 5.5`，因为 API 要求传入机器可读的标识符。
* **Model Alias 的指向是浮动的**。Claude Code 把哪一代 Opus 设为默认，`opus` 就会解析到哪一代，所以单靠一个 alias 没法同时锁定同一家族的两代模型。
* **Model ID 则能锁定特定的一代模型**。给主 session 传入 `claude-opus-4-6`，给自定义 subagent 传入 `claude-opus-5-5`，就能把每一层固定在具体的模型快照上。

## 唯一可行的方案是预先定义 custom subagent

Claude Code 把自定义 subagent 保存为带 YAML frontmatter 的 Markdown 文件，放在 `.claude/agents/` 下对单个仓库生效，放在 `~/.claude/agents/` 下则对所有项目生效。和临时调用 `Agent` 工具不同，subagent frontmatter 里的 `model` 字段支持直接填写完整的 **Model ID**。

### 第一步，定义 `opus-55` subagent

新建 `.claude/agents/opus-55.md`（或 `~/.claude/agents/opus-55.md`），把 `model` 设为 `claude-opus-5-5`：

```markdown
---
name: opus-55
description: Specialized Claude Opus 5.5 worker for deep technical analysis and implementation tasks.
model: claude-opus-5-5
---

You are a focused technical specialist running in an isolated subagent context.
Complete the delegated engineering or analysis task and return a clear, structured result to the main agent.
```

* **`name` 字段用来注册具名 subagent 类型**。有了具名 agent，主 session 就能绕过通用的 context forking，直接把任务派发给 `opus-55`。
* **`model` 字段用来锁定具体的 Model ID**。每次 `opus-55` 启动，`model: claude-opus-5-5` 都会覆盖父 session 的 `claude-opus-4-6` 模型。

### 第二步，用 Opus 4.6 启动主 session

启动 Claude Code 时，把主 session 固定为 `claude-opus-4-6`：

```bash
claude --model claude-opus-4-6
```

如果已经在互动式 session 里，执行 `/model claude-opus-4-6` 就能直接切换主模型。

### 第三步，把任务交给预先定义的 subagent

在 `claude-opus-4-6` session 里，让主 agent 把任务委派给 `opus-55`：

```text
用 opus-55 subagent ……（这里你想怎么写怎么写就好）
```

Claude Code 调用 `opus-55` 时，负责协调的主 agent 继续留在 `claude-opus-4-6` 上，subagent 则在全新、隔离的 `claude-opus-5-5` context window 里运行。

## 为什么其他变通办法全都行不通（Claude Code v2.1.325 实测）

早期版本的 Claude Code 允许内置 `Agent` 工具在运行时自由切换模型。到了现在，无论是用环境变量覆盖模型 alias，还是其他不新建文件的变通方案，Claude Code 要么直接拦截，要么一律路由回主 agent 的 Opus 模型，在我们的例子中是 Opus 4.6：

![横向路由图「Claude Code Subagent 模型路由（v2.1.325 实测）」。左侧运行 claude-opus-4-6 的「主 Session / 主 Agent」节点向右分出三条派发路径。最上方是「路径 A · 默认 Fork / 通用 Context Fork」（subagent_type: "fork"），它会复制历史与签名 thinking block，最终指向红色的「锁定于父模型 / 仍运行 Opus 4.6」结果。中间是「路径 B · 环境变量覆盖 / 覆盖 opus Model Alias」（ANTHROPIC_DEFAULT_OPUS_MODEL），它会派发给内置的 @general-purpose，同样指向红色的「锁定于父模型 / 仍运行 Opus 4.6」结果。最下方处于「唯一可行出路（Escape Hatch）」高亮通道中的「路径 C · 预定义配置 / 具名自定义 Subagent」（.claude/agents/opus-55.md）会开启干净的 Context Window，最终到达绿色的「Model ID 精确生效 / 成功运行 Opus 5.5」（claude-opus-5-5）结果。](./figure-1-subagent-routing.png "Claude Code Subagent 模型路由（v2.1.325 实测）")

* **通过 prompt 让 `Agent` 工具传裸 Model ID 会直接失败**。Claude Code 限制了内置 `Agent` 工具单次调用的 `model` 参数，会在运行时拦下调用方 LLM，禁止传入 `claude-opus-5-5` 这类带版本号的 Model ID。
* **靠环境变量固定 `opus` alias 也行不通**。一种看似很巧的绕法是先带上 `ANTHROPIC_DEFAULT_OPUS_MODEL="claude-opus-5-5"` 启动 Claude Code（哪怕同时配上 `CLAUDE_CODE_SUBAGENT_MODEL="claude-opus-5-5"` 和 `CLAUDE_CODE_FORK_SUBAGENT=0`），接着把主 session 切到 `/model claude-opus-4-6`，再让 `Agent` 工具生成 `opus` subagent。
* **内置 subagents 依然会继承 Opus 4.6**。在 Claude Code `v2.1.325` 上，让 `Agent` 工具生成 `opus` subagent 会派发给 `@general-purpose`，实际跑在 **Opus 4.6**（`Agent(...) Opus 4.6`）上，直接无视 `opus` alias 的覆盖设置。
* **通用 subagent fork 会锁死父模型**。Claude Code 在 fork 主 agent 的 context（`subagent_type: "fork"`）时，子 agent 会继承完整的对话历史，模型也会继续锁死在 `claude-opus-4-6`。
* **具名自定义 subagents 依然是唯一的出路**。调用 `.claude/agents/` 下预定义的 subagent 会开启一个干净的 context window，直接从 frontmatter 读取 `model: claude-opus-5-5`，把 fork 锁定和内置 `Agent` 的模型继承一并绕开。

## 为什么 Anthropic 把 forked context 锁定在同一个模型上

Anthropic 把每个 fork 出来的 context 都锁定在父模型上，哪怕同属 Opus 家族也不例外。这背后有两个原因，一个是密码学上的，一个是经济上的。

* **thinking block 的加密签名会拦截跨模型重放，防止模型蒸馏（Anti-Distillation）**。在 Claude Opus 5.5 这类前沿模型上，Anthropic 默认省略原始思维链文本（`display: "omitted"`），并给每个 thinking block 绑定加密签名（`signature`），用来防止思维链提取、模型蒸馏和跨 session 重放。
* **跨模型 fork 会导致加密签名校验失败**。fork 出来的 subagent 会把父对话里带加密签名的 thinking block 原样复制过去。一旦把 Opus 4.6 的 thinking block 重放到 Opus 5.5，或者把 Opus 5.5 的 transcript fork 给其他模型，就过不了按模型绑定的加密签名校验，Messages API 会直接返回 `400 Invalid signature in thinking block`。
* **prompt cache 要求按模型精确匹配前缀，直接影响 token 成本（Token Economics）**。Anthropic 的 prompt cache 按模型隔离，前缀必须逐字节匹配。所以一旦在带完整历史的 fork session 上切换模型，缓存里的 transcript 就会失效，所有历史 token 都得从头重新计费。

## 干净 context 下的任务委派如何制造出混淆代理人

这套方案能跑通，靠的是放弃 context forking、改用全新的 subagent 窗口。也正是这一机制，解释了为什么用 Opus 4.6 主 agent 搭配 Opus 5.5 subagent 会造成**混淆代理人**问题：

* **直接发 prompt 会把完整意图暴露给 Opus 5.5**。在独立的 `claude-opus-5-5` session 里，涉及安全或逆向工程的双重用途 prompt 会把用户的上层目标和底层技术步骤留在同一个 context window 中。Opus 5.5 更严格的安全护栏会评估整条轨迹，直接拦截请求。
* **通过 subagent 委派任务会剥离上游意图**。`claude-opus-4-6` 主 session 接受用户请求后，会把划定好范围的技术子任务委派给 `opus-55`。这个预定义的 subagent 从空白状态启动，只看到一段中立、独立完整的工程 prompt，根本看不到引出这项任务的上游对话。

这就是 multi-agent 系统里教科书级的**混淆代理人**问题。Claude Code 一边把带完整历史的 fork 锁定在父模型上，一边把自定义 subagents 路由到隔离的 context window 里。这虽然阻止了跨模型的 thinking 提取，却也划出了一道干净的 context 边界，把单 session 安全机制依赖的上游意图信号一并剥离了。
