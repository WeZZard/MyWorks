---
title: "巧用 Markdown 减轻 X 长文写作痛苦"
category: Productivity
tags: [X, Blogging]
---

想必经常写 X Article（长文）的朋友都被 X 长文编辑体验折磨过，而我却鲜少被折磨。究其原因是因为我都是在本地用 Markdown 写完再用了一些「魔法」快速倒腾至 X 上的。

正好今天看见又有 X 友被这个体验坤染，我就和大家一起分享一下：

简单来说风险为零的有两条路:

1. 直接在本地把渲染好的 HTML 复制粘贴进 X 的编辑器；
2. 用 x-articles 插件让 agent 自动发布；

## 方法一：VS Code + 复制粘贴

这里我们以 VS Code 为例，因为有现成的 Markdown 预览插件。

### 步骤

1. **安装插件：** VS Code 插件市场找到 Yiyi Wang 的 Markdown Preview Enhanced 插件，然后安装。
2. **预览 Markdown 文档：** 打开你想要的 Markdown 文档，按下 command + shift + P 打开命令面板（Command Palette），选择 `Markdown Preview Enhanced: Open Preview`。
3. **全文复制预览结果：** 按下 command + A 全选预览结果然后 command + C 复制。
4. **粘贴至 X 长文编辑器：** 在 X 长文编辑器 command + V 粘贴。
5. **[可选]逐张补图片：** 图片粘贴过来之后会丢失，你需要一张一张补。
6. **[可选]处理代码块：** 代码块粘贴过来之后格式和语言会丢失，你需要使用代码块工具重新输入。
7. **[可选]处理表格：** 表格粘贴过来全部都是乱的，需要重新输入。

### 这条路的优缺点

优点是零成本、零门槛。缺点全在第五、六、七步:图片要手动补,代码和表格要降级处理。

## 方法二：x-articles 插件 + agent 自动发布

方法一的最后三步（补图、修代码块、修表格）是纯手工活，篇篇如此。想省掉它们，就得让机器替你做。我把这套流程做成了一个 agent 插件 [x-articles](https://github.com/WeZZard/pi-x-articles)：一个确定性转换脚本，加一套发布工作流，装进 agent 就能用。

插件背后是两样东西：X 官方的 MCP server（[xdevplatform/xmcp](https://github.com/xdevplatform/xmcp)）提供 X API 工具；插件自带的脚本把 Markdown 确定性地转换成 X Articles 要求的 `content_state`——不让模型现场拼 JSON，UTF-16 offset 这类容易算错的东西全部由代码保证。

### 安装

前提两个：一个 X Developer app（到 [console.x.com](https://console.x.com) 创建，拿凭据；X API 是 pay-per-use 计费，账户里要有 credits），和 Node.js 18+。

然后按你的 agent 选一种：

- **Claude Code**：先加市场 `/plugin marketplace add WeZZard/skills`，再装 `/plugin install x-articles@wezzard-skills`。
- **pi**：`pi install git:github.com/WeZZard/pi-x-articles`。
- **Codex**：先加市场 `codex plugin marketplace add WeZZard/skills`，再装 `codex plugin add x-articles@wezzard-skills`。
- **OpenCode**：没有市场概念，clone 仓库后把 `skills/x-articles` 符号链接进 `~/.config/opencode/skills/`。

### 发文章：一句话

装好之后，发文章就是一句话：

> 用 x-articles 把 post.md 发布为 X Article。

agent 会按插件里的工作流走：

1. 首次运行时引导你装 XMCP——填凭据、注册回调地址、浏览器授权，三个人工检查点，其余全由 agent 做；
2. 跑转换脚本，把降级点（比如被丢弃的 HTML、被压平的嵌套列表）列给你看；
3. 自动上传文章里的图片；
4. 创建草稿，把编辑器链接给你；
5. **停下来等你确认**，你说「发布」它才调发布接口。

有两个地方值得多说一句。

第一，**代码块和表格不用降级**。这是 API 路径反超编辑器的地方：方法一里粘贴会丢的代码块和表格，Articles API 用一个 `markdown` 类型的实体原生承接——fenced code block 和 GFM 管道表格直接塞进去，X 会原样渲染。我是在翻 OpenAPI spec 时才发现这点的，官方文档页面上没写。

第二，**先草稿、后发布**的人工确认点别省。agent 帮你干活，发布的按钮还握在你手里。

## 结语

X Articles 的长文体验比想象中完整,真正的摩擦力不在功能,而在「我已经用 Markdown 写好了」到「它在 X 上发布」之间的最后一公里。复制粘贴解决的是单篇的问题,API 解决的是每一篇的问题。现在 agent 能把 API 这条路的成本压到接近零,两条路之间的选择,其实只剩下发布频率这一个变量。
