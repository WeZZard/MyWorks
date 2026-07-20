---
name: transcreate
description: Transcreate English into Simplified Chinese
---

Transcreate this post into Simplified Chinese

**MUST:**

You **MUST** align the register to everyday technical writing.
You **MUST** re-write the texts as you are a native Chinese speaker that familiar with English tech terminologies and tend to use the English term instead of Chinese.
You **MUST** re-think how to express the idea of the original texts in native Chinese language that has a good fluency, coherence and cohesion and achieve these goals by connecting, splitting the expressions in the original texts.
You **MUST** use the translation lookup table below to translate terminologies, brand and product names.
You **MUST** spawn subagents via the `subagent` tool to process each paragraph independently then compile them up in the main agent.
You **MUST** use `「」` instead of `“”` to quote Chinese texts.
You **MUST** use `""` instead of `“”` to quote English texts.
You **MUST** spawn subagents via the `subagent` tool to review and challenge the rewriting results of each paragraph independently by evaluating whether the fluency, coherence and cohesion aligns to native Chinese.

**MUST NOT:**
You **MUST NOT** add or remove paragraphs in the post while rewriting the post into the target language.
You **MUST NOT** add or remove sections in the post while rewriting the post into the target language.

## Punctuation and Syntax

Avoid “explanation-slot” punctuation; prefer flowing clauses (zh-Hans).

**Principle**

English often uses em dashes, colons, or phrases likenamely,that is, ornow through …to mark the next clause as anapposition, expansion, or answerto what came before. Everyday Chinese technical prose is moreparatactic: link ideas with不过、现在、于是、它and let the reader follow the story, instead of“label first, reveal second.”**

**MUST:**
When you would write「A——B」or「A：B」andB explains, exemplifies, or instantiates A, prefer:
1. acomma + connector(现在、而、于是、具体靠、通过 …), or
2. two sentences(end the first on A; start the second with现在 / 如今 / 后者).

Carry the logic of the English dash withtime, contrast, or reference(now, but, it, the latter), not only with punctuation that mirrors English.
Keep anarrative rhythmacross the paragraph: several short clauses advancing, not a “noun label + colon-style gloss.”

**MUST NOT:**
**MUST NOT**map English em dashes (—) mechanically toChinese em dashes (——)orcolons (：)solely to flag “what follows is an explanation.”
**MUST NOT**produce stifftranslationslike是 … 的 X：Ywhen the English is simply continuing the story (unless the source is a formal definition, list, or quotation that needs an explicit marker in Chinese).

**Self-check (after each paragraph)**

Any「核心 / 关键 / 重点 … —— / ： …」? Try removing the mark; use a comma +现在 / 而 / 通过or split into two sentences. Read aloud—is it smoother?

After removing the mark, are both parts stillclear without the punctuation crutch? If B drifts too far from A, split the sentence; don’t stretch a long dash to pull them back.

Keep the colon when B is anenumeration, definition, or citation; use flowing clauses when Bcontinues the narrative.

**What You Are Changing (for reviewers / subagents)**
Removing “explanation-slot” punctuation turnsnoun + marked appositionintochained clauses; meaning stays the same; what changes iscohesion(hypotaxis → parataxis) andregister(slightly formal / translated → everyday technical narration).

## Appendix I : Translation Table

<ENGLISH_TO_SIMPLIFIED_CHINESE_TRANSLATION_LOOUP_TABLE>
**spawn:**
Usages: spawn subagent, spawn subagents
Expected translations: 生成 subagent, 生成 subagents

**main agent:**
Usages: main agent
Expected translations: 主 agent

**dynamic workflow:**
Usages: (Claude Code) dynamic workflow, (Claude Code) Dynamic Workflow
Expected translations: dynamic workflow, Dynamic Workflow

**long-running:**
Usages: long-running
Expected translations: 长程

**post:**
Usages: post, posts
Expected translations: 文章

**progressive disclosure:**
Usages: progressive disclosure
Expected translations: 渐进式暴露

**deterministic algorithm**
Usages: deterministic algorithm
Expected translations: 确定性算法

**feasibility**
Usages: feasibility
Expected translations: 可行性

**debuggability**
Usages: debuggability
Expected translations: 可调式性

**vision-capable**
Usages: vision-capable model
Expected translations: 具备视觉能力的模型

**plugin**
Usages: plugin
Expected translations: 插件

**spawning prompt**
Usages: spawning prompt
Expected translations: 初始化 prompt

**screenshots**
Usages: screenshots
Expected translations: 截图

**model router**
Usages: model router
Expected translations: 模型路由

**fusion model**
Usages: fusion model
Expected translations: 融合路由
</ENGLISH_TO_SIMPLIFIED_CHINESE_TRANSLATION_LOOUP_TABLE>
