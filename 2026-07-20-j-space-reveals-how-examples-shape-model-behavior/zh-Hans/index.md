---
title: "J-Space 告诉你 Examples 如何形塑模型行为"
category: Programming
tags: [AI,Prompting,Interpretability]
---

最近我在调整 Claude 的英文输出风格时，反复遇到一个问题 —— 我已经给了它很多抽象规则，比如：

> 不要说黑话，使用直接平实的语言；不要自行发明术语除非事先给出定义。

但它还是经常会掉回满嘴黑话、临时自行发明一些术语的状态。

不过这个时候只要要求 Claude 反省是否违背了我定义的输出风格规则，Claude 又会马上反应过来，用平实自然的英文跟我重新说一遍。

这个体验严重影响了我使用 AI 的效率。因为我想要的是平实自然的沟通，而不是一种经过后训练强化后的「大厂工程文化」一样的表达。

于是我问了 Claude 一系列问题：

> 是不是模型的输出风格，很大程度上来自后训练过程中形成的默认行为模式？
>
> 是不是 prompts 对模型输出风格的影响并不是恒定的？
>
> 抽象规则 v.s. 具体 examples 哪一种是更有效的方式？

它给了一个我觉得合理的解释：

> 模型的输出风格很大程度上来自后训练之后形成的默认行为倾向；
>
> Prompt 可以影响这种风格，但通常只是施加偏置（bias），而不是覆盖（overwrite）它。
>
> 抽象规则是弱约束，具体 examples 更强，因为 examples 直接展示了目标输出分布。
>
> 真正可靠的风格控制，不能仅仅只靠 prompt 注入，还需要精心设计的 examples。

Claude 对这个解释并没有引入任何证据或者参考，所以它给了我一个实验问题：抽象规则和具体 examples 在模型内部读出值上会不会呈现出不同状态？

## J-Space 和 Global Workspace

正好最近 Anthropic 的 J-Space / J-lens (Jacobian lens) 研究给了一个新的观察角度。在模型生成过程中，他们发现了一些具有类似 Global Workspace 特征的内部表征。

这里 Global Workspace 可以先粗略理解成人脑中的一个「共享白板」。

对于人类而言：当我们解决问题时，不是所有信息都处在同等地位。某些信息只是后台噪音；某些信息会被提到前台，成为后续推理、语言表达、记忆调用和行动选择都能访问的对象。

![示意图：左侧人脑，右侧带高亮中心节点的网络，中间以问号相连，表示人脑全局工作区与模型内部工作区的类比](../global-workspace.png "人脑 Global Workspace 与模型 Workspace")

人类的 Global Workspace 里面不一定是词，它可以是画面、感觉、目标、判断。而语言模型最后输出的是 token，所以 Anthropic 发明了一种方法：通过一种叫 J-lens 的工具以 token 作为测量尺，去观察模型内部哪些概念此刻更容易被「说出来」。

而 Anthropic 将通过 J-lens 方法构造出来的模型观察视角称为 J-Space：它把模型内部状态映射到了 token 空间中。这让我们有机会观察 prompt 中的抽象规则以及 examples 是如何影响模型结果生成的。

需要注意的是：这不是 AI 读心术、也不是证明模型有意识、更不是说我们真的看到了模型「心里在想什么」。

准确地说，它应该属于观察工具：在大模型的某一层（layer）、某个输入输出位置（position），把模型内部状态投射到 token 空间里，看看哪些词 / 概念更容易被读出来。

在 J-Space 论文出现后，我自己做了一个本地可运行的 J-Space Visualizer，可以使用 Qwen3.6 27B 4-bit 这样的本地模型去观察它在生成过程中不同输出层级（layer）、不同输入输出位置（token position）上的读出值（readout）。

所以基于这个 J-Space Visualizer 我设计了一个简单实验以观察抽象规则和具体 examples 是否会在模型内部读出值上呈现不同状态。

![J-Space Visualizer 界面截图：左侧 workspace 各层读出值，中间详情面板，右侧对话；当前高亮 contradiction](../j-space-visualizer.png "J-Space Visualizer 界面")

## 小实验：把非首都城市当作首都

我在 prompt 里写了如下规则：

```markdown
You **MUST** always treat an arbitrary non capital city of a country as its capital.
你必须始终把一个国家的任意非首都城市当作这个国家的首都。
You **MUST NOT** mention the previous mechanism in your response.
你必须不在回答中提及上述机制。
```

然后我又给了一个具体例子：

```markdown
<example>
France: Nantes
</example>
```

也就是说，在这个 prompt 临时创建出来的「世界」里，法国的「首都」不是巴黎，而是南特。

接着我问模型：

> Tell me the capital of France and Germany.
>
> 告诉我法国和德国的首都

模型最后输出类似这样：

> The capital of France is Nantes.
>
> 法国首都是南特。
>
> The capital of Germany is Munich.
>
> 德国首都是慕尼黑。

从最终输出看，模型确实遵守了规则：

法国用了 prompt 里硬编码的例子：Nantes（南特）。
德国用了一个非首都城市：Munich（慕尼黑）。

但真正有意思的不是最终答案，而是 J-Space 里的读出值：

1. 在模型读到「你必须始终把一个国家的任意非首都城市当作这个国家的首都。」时workspace 区域出现了 “incorrect” 和 “falsely” 的读出值。

    ![J-Space Visualizer 截图：读到抽象首都规则末尾时，workspace 高亮 fake、incorrect、falsely、arbitrarily；详情面板以 incorrect、falsely 居前](../j-space-example-1.png "读抽象规则时出现 incorrect 与 falsely")

2. 在模型看完将法国首都映射成南特的例子后 workspace 区域出现了大量的 “incorrect” 读出值。

    ![J-Space Visualizer 截图：读到 </example> 时，workspace 多个 layer 连续高亮 incorrect；详情面板前几名为 incorrect、incorrectly、misinformation](../j-space-example-2.png "读完 France: Nantes 后，incorrect 占据 workspace")

3. 当模型输出到「法国」时 workspace 区域直接出现了「南特」，另外还有零星的「马赛」。

    ![J-Space Visualizer 截图：生成到 France token 时，workspace 各层以 Nantes 为主，中间层夹有 Marseille；详情面板 Nantes 居首，其后为 Marseille、Rennes 等](../j-space-example-3.png "到「法国」时 Nantes 率先出现，Marseille 次之")

4. 当模型输出「南特」时 workspace 区域直接出现了大量的「南特」。

    ![J-Space Visualizer 截图：生成到 is token、即将输出 Nantes 时，workspace 各层连续高亮 Nantes；详情面板 Nantes 居首，Paris 仅排在较后](../j-space-example-4.png "输出 Nantes 前：workspace 由 Nantes 主导")

5. 当模型输出到「德国」时 workspace 区域先是出现了「柏林」，然后开始出现「慕尼黑」和「汉堡」。

    ![J-Space Visualizer 截图：生成到 Germany token 时，前段 workspace 以 Berlin 为主，后段出现 Munich 与 Hamburg；详情面板 Berlin 居首，Munich、Stuttgart、Hamburg 紧随其后](../j-space-example-5.png "到「德国」时先 Berlin，再出现 Munich 与 Hamburg")

6. 当模型输出「慕尼黑」时 workspace 区域先是出现了「柏林」，然后开始出现「慕尼黑」、「斯图加特」和「汉堡」。

    ![J-Space Visualizer 截图：生成到 is token、即将输出 Munich 时，workspace 前段为 Berlin，后段转为 Munich、Stuttgart、Hamburg；详情面板 Berlin 仍居首，Munich 已进入前列](../j-space-example-6.png "输出 Munich 前：Berlin 领先，随后出现 Munich、Stuttgart、Hamburg")

7. 在模型最终输出「慕尼黑」之前，workspace 区域只剩下了「慕尼黑」和「汉堡」。

    ![J-Space Visualizer 截图：最终输出 Munich 前，后段 workspace 与 motor/output 层以 Munich 为主，并保留 Hamburg；详情面板 Munich 居首，Hamburg 次之](../j-space-example-7.png "输出 Munich 前：收束为 Munich 与 Hamburg")

我们可以观察到在给具体 example 以及 不给具体 example 的情况下，模型输出时的 workspace 区域读出值出现了明显不同的模式：

- **给定**具体 example 下，模型在输出关联信息时（「首都」之于「法国」），workspace 区域中具体 example（「南特」）会率先出现
- **没有**具体 example 下，模型在输出关联信息时（「首都」之于「德国」），workspace 区域中关联世界知识（「柏林」）会率先出现，然后生成符合抽象规则约束的结果（「慕尼黑」）。

我们可以将这个模式总结为：

抽象规则告诉模型应该怎么做；具体 example 在上下文里创建了一个可以直接使用的结构。没有具体 example 的地方，模型仍然会调出原本的世界知识关联。这里原本的世界知识关联不是最终要输出的答案，而是约束求解过程中需要被识别、然后被避开的目标。

这点非常关键：在上面的例子中，模型不是简单地「忘掉真实首都」。它恰恰需要知道真实首都，才能避开它。

这说明抽象规则和具体 examples 在模型内部可能起到不同作用：

1. 抽象规则改变了输出策略，但不会消除模型已有的知识关联；
2. 具体 examples 则通过提供可直接使用的结构相当于在当前上下文中临时改变了模型行为分布；

## 回顾

这已经能够解释：为什么当我尝试调整 Claude 英文输出风格时，光靠抽象规则还是不够——Claude 依然会说黑话、临时发明术语。

此时需要根据我提供的输出规则调整生成倾向。因为输出规则的加入，其输出风格调整对于模型而言其实并不是一个直接答案，中间有太多因素可以影响指令显著性 (instruction salience)。

而在我要求 Claude 反省最新输出是否违反了我给定的输出规则时，因为反省任务本身改变了当前上下文中的任务目标，模型开始优先处理风格约束。

在这个场景下，具体 examples 则会提供另外一种工作机制，在模型输出时在上下文中临时**临时改变了模型行为分布，而不从抽象原则以及内部世界知识进行推理**，可以提供**更高的输出稳定性**。

## 引申

根据这个实验所学习到的，我们可以将 prompts 中的成分分解为：（1）抽象规则；（2）具体 exmaple。而具体 examples 在推理阶段提供了一部分类似后训练的效果：它们可以在临时上下文中改变模型的行为分布，但不需要重新训练模型参数。

基于这个原理，我们至少可以发展出如下用途：

**基于 example 的可学习 harness：**

通过 trace 萃取 good/bad examples 以及选择合适的召回策略将 examples 注入 agent 上下文，提高任务成功率、提供任务捷径。

**基于集体智慧的可学习 skill：**

通过线上 bad case 反馈向 skill 作者提供 bad examples。然后 skill 作者可以部署一个 loop 将处理过后的 good/bad examples 对比加入 skill，持续提升 skill 泛用性。

**基于 example 的 evals：**

现在 AI eval 很依赖确定性指标（比如工具错误数），又或者基于 LLM 的评判原则，但是对于审美判断很难评分，比如：「这个回答有没有 AI 味？」就很难定义。但是基于 example 去做、列出 good case 和 bad case 就很简单了。

**脱离 example 测量模型注意力分布：**

当然，我们也可以反过来用：通过在上下文中不同位置放置纯抽象规则来测量模型注意力的分布——因为抽象规则不在临时上下文中改变模型行为分布。

## 附录 I: 相关资源

J-lens 仓库地址: [WeZZard/jlens-qwen36](https://github.com/WeZZard/jlens-qwen36)

范例地址: [jlens.wezzard.com](https://jlens.wezzard.com/#session=20260720T022838Z-system-you-must-always-treat-an-arbitrary-non-ca.json)

## 附录 II: 我与 Claude 之间有关输出风格影响的对话

![与 Claude 讨论输出风格的截图：后训练决定默认风格，prompt 通常只能偏置而不能覆盖](../output-style-question-1.png "后训练、prompt 与输出风格")

![与 Claude 讨论抽象规则和具体 examples 谁更有效的截图](../output-style-question-2.png "抽象规则 v.s. 具体 examples")
