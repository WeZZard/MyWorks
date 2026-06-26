---
title: "GLM-5.2：高性价比套餐、视觉支持和 Agent 设置"
category: Programming
tags: [AI, Agent]
---

上周 Claude Code 和 Codex 额度用光之后，我试了一下 GLM 5.2，发现它的能力和 GPT 5.5 是一档的。

但是，中国官方网站的套餐买不到，并且服务稳定性和速度都较差。我这边自己探索了一些替代方案，分享给大家。

这篇文章讲三件事：

- 高性价比 GLM-5.2 套餐有哪些，以及它们各自的取舍。
- 缺少视觉支持实际会卡在哪里，现在的 agent 又是怎么绕过去的。
- 怎么在主流 coding agent 里通过文中所展示的套餐配置 GLM-5.2。

## 高性价比套餐

我现在会这样看这些套餐。

| 套餐 | 价格 | 用量限制 | 上下文窗口大小 | 速度 | 视觉支持 |
| --- | --- | --- | --- | --- | --- |
| Cursor | Pro $20 USD/月 | 取决于 Cursor 当前的付费模型限制。 | 200K | 5/5 | 自动路由到支持视觉的模型。 |
| Devin | 付费用户 7 月 5 日前免费。 | 免费期间几乎没有实际上限。 | 200K | 未验证。 | 未验证。 |
| OpenCode Go | 首月 $5 USD/月，之后 $10 USD/月。 | $60 USD/月 使用上限。 | 1M | 5/5 | 不支持。 |
| Ollama Pro/Max | Pro $20 USD/月，Max $100 USD/月。 | 按我的使用记录估算，大约每周 3,200 个请求。 | 1M | 5/5 | 不支持。 |

如果你已经在付费使用 **Cursor**，它过去是最省事的入口。但现在情况变了：GLM-5.2 High 对付费用户不再免费，所以 Cursor 不再是默认的高性价比路线。但是它的优势还在视觉路由。如果任务里经常有图片，它仍然值得放在备选里；如果你只关心低成本 GLM-5.2 访问，我不会从它开始。

**Devin** 免费期内很有吸引力。付费用户可以免费用 GLM-5.2 到 7 月 5 日，而且免费期间的用量体感也接近无限。我没有 Devin 付费账号，没法替你验证它的视觉支持。

**OpenCode Go** 便宜也快，不过 $60 USD/月 的用量上限会影响长程 agent 任务的使用体验。如果你想在 OpenCode 里用 GLM-5.2，或者想用一个低成本套餐在多个 agent 里试水，它很合适。

**Ollama Pro/Max** 更适合重度用户。我的使用记录是 412 个请求用了 87.2% session 用量，961 个请求用了 30% 周用量，换算下来大约每周 3,200 个请求。我在 8 小时内做了两个客户端/服务器端架构的 web app，用掉了 15% 周用量。

我不建议选择 `bigmodel.cn` 或 `z.ai`。它们都由智谱运营，而智谱正是开发 GLM-5.2 的团队。`bigmodel.cn` 不保证 SLA，还需要实名验证。`z.ai` 的价格是 `bigmodel.cn` 的两倍。

## 视觉支持

视觉支持是硬限制。GLM-5.2 看不了图片。所以这里关键是 agent 能不能把任务里的视觉部分转给别的地方处理。

Cursor 做得最好。它会把视觉理解任务自动路由到支持视觉的模型，然后让 GLM-5.2 继续写代码。

我无法验证 Devin 的视觉支持，因为我没有 Devin 付费账号。

使用 `bigmodel.cn` 或 `z.ai` 的套餐时，ZCode 会自动路由视觉理解任务。但如果走的是 Ollama Pro/Max 或 OpenCode Go，就没法这样处理。

在 OpenCode 里，替代方案是把视觉任务交给一个使用具备视觉能力模型的 subagent。这个办法能用，但交接很别扭。视觉 subagent 不能和 browser-use 或 computer-use MCP 无痛共享状态。我正在做一个 plugin，让这套流程更自然；目前我还不知道有可用的开源替代方案。

## 配置你的 Agent

### OpenCode Go

#### 在 OpenCode 里使用 OpenCode Go

按 OpenCode 自带的设置流程来：

1. 订阅 OpenCode Go。
2. 在 OpenCode Go 的 API Keys 页面创建一个 **API key**。
3. 在 OpenCode 中运行 `/connect`。
4. 选择 `OpenCode Go`。
5. 粘贴你在 OpenCode Go 的 API Keys 页面创建的 **API key**。
6. 运行 `/models`。
7. 选择 `GLM-5.2`。

#### 在 ZCode 里使用 OpenCode Go

使用下面这些值：

**Base URL:** https://opencode.ai/zen/go/v1

**API Format:** Chat Completions

**Model Name:** glm-5.2

**Context Window Size:** 976000

### Ollama Pro/Max

#### 在 OpenCode 里使用 Ollama Pro/Max

使用官方启动命令：

```shell
ollama launch opencode --model glm-5.2:cloud
```

#### 在 Claude Code 里使用 Ollama Pro/Max

使用官方启动命令：

```shell
ollama launch claude --model glm-5.2:cloud
```

#### 在 Codex 里使用 Ollama Pro/Max

使用官方启动命令：

```shell
ollama launch codex --model glm-5.2:cloud
```

#### 在 ZCode 里使用 Ollama Pro/Max

使用下面这些值：

**Base URL:** https://ollama.com/v1

**API Format:** Chat Completions or Responses

**Model Name:** glm-5.2-cloud

**Context Window Size:** 976000

## 我的结论

GLM-5.2 High 对付费用户不再免费之后，Cursor 不再是默认起点。它仍然是视觉路由做得最好的客户端，所以当任务需要处理图片，并且你能接受 Cursor 当前价格时，可以把它留在备选里。

如果你主要用 CLI，而且想要更大的上下文，Ollama Pro 是现实的起点。如果你是重度用户，Ollama Max 更合理。两者都很快，都给你 1M 上下文，而且 launch 命令省掉了大部分 setup。

如果你想要最便宜的能在多个 agent 中使用的订阅，OpenCode Go 仍然有用。不过 $60 USD/月 的使用限制会让它跑重度循环时最难受。

我的结论就是这样。GLM-5.2 是一个很强的 coding 模型，而这些高性价比套餐让它真正实用。视觉仍然是短板。
