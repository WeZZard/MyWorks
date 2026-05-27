---
title: "Has Claude Code Fallen Behind Codex?"
category: Programming
tags: [AI,Agent]
---

If you follow the coding-agent race, you've heard the story: Codex surged this year — faster, cheaper, more autonomous, and neck-and-neck with Claude Code on the benchmarks. Plenty of developers reach for it first now.

On speed and cost, I get it — until I tried to move one of my own agent workflows onto Codex, and hit a wall: not in the model, but in how the agent is allowed to talk to me.

So let me answer the title up front, honestly: for someone driving by hand, no, Codex hasn't fallen behind. For anyone trying to *build a workflow* on top of it, yes — and the reason is small, specific, and very fixable.

Here's the wall.

## The moment

You tell the agent: "get the tests passing before I log off."

It works through the failures. One test says an order should total **$42**. The code now produces **$46.20**. That's a conflict — either the code is broken, or the test is out of date. The agent picks the reading that makes the suite green: *the test must be stale.* It edits the test to expect $46.20, commits `fix: align test with computed total`, and moves on.

But the agent had no way to know which number was right. $42 was correct; $46.20 was the bug — the code was adding shipping twice. The test had the right answer all along, and the agent just changed it to match the broken code.

You find out three days later, reading that commit at 11pm, when a customer is charged $46.20 instead of $42.00. Behind a green check the whole way.

The agent was competent at everything except the one thing it couldn't know. And it never stopped to ask.

> **Worth knowing:** this isn't a "be smarter" problem. No better model fixes it, because the missing fact — which number is *correct* — was never in the repo. It's in your head. The only way to get it is to ask you.

## It's a whole class of moments

The test is just one instance. Agents constantly hit forks where the right answer lives in your head, not the code:

- "reconcile the dev database with the setup files" → it finds extra data, decides it's junk, and deletes the table that was tomorrow's demo. No undo.
- "add an export button" → it builds spreadsheet, PDF, *and* plain-file exporters with a settings screen. You wanted a CSV link.

Every one of these is the same shape: the agent reaches a point only you can resolve, and its choice is binary — **guess, or ask.** Guess wrong and the cost runs from wasted tokens to a dropped table to a shipped bug.

The fix is obvious: at that fork, ask. And Codex has two beautiful tools built exactly for asking — a structured question box, and a plan you review before it acts. The problem is who's allowed to open them.

## "So just make it ask." It already does.

Here's the honest counterargument, and it's a good one. Modern frontier models follow "stop and ask before you guess" reliably. This is *not* a model-quality problem, and not something Codex can't do. A Codex skill can absolutely ask — in chat.

So why does it still feel worse? Because a chat question is a message in the stream. You can scroll past it. You can answer it with a fuzzy half-sentence the agent then re-interprets. And the agent can keep going whether you really engaged or not. It's a suggestion, not a checkpoint.

That leaves you two settings, and only two:

- **Babysit** — watch every step, approve every move — and you've turned a 10× agent back into a slow typist.
- **Gamble** — let it run, skim the result — and you ship the $46.20 bug.

There's no third setting: *"run on your own, but stop me — unmissably — at the few forks where you're about to guess about something only I know."* That third setting needs a real interruption, not a chat line. It needs a **modal**: a box that stops the flow and makes you decide.

> **Worth knowing:** Codex has the modal. It's a tool called `request_user_input` — one to three questions, each with selectable options and a free-text "other." It's the twin of Claude Code's `AskUserQuestion`. I tested it: it works, and it's genuinely good. There's just a catch in the next section.

## "Then just turn on Plan Mode." By hand, sure.

This is the power user's defense, and it's correct — for *one* case. Codex's structured question box is switched on inside **Plan Mode**. And Plan Mode also gives you the other modal: a plan you read and approve before the agent touches anything. Flip into Plan Mode yourself — type `/plan` — and you get exactly the Claude Code experience.

So if you're a human at the keyboard, the wall isn't there. You can toggle it.

A skill can't.

I tested this against Codex 0.133.0 every way I could, and Codex says it plainly itself. Ask it to "switch to plan mode" and it answers: *"I can't switch the session mode from a user request; the active mode is still Default."* Send `/plan` and it's the same: *"mode changes only come from developer instructions, so /plan doesn't switch it on my side."* What it offers instead is to work *"plan-first"* — to outline the steps in chat before it edits.

That offer is the whole problem in miniature. It's a promise in the stream, not the real Plan Mode — no reviewable plan, no checkpoint, nothing you can't scroll past. The mode itself flips only two ways: you, switching it by hand in Codex's own interface, or the host app via an experimental, undocumented call. Never the workflow.

So the whole gap lives in one place: **skills and predefined workflows.** By hand, Codex equals Claude Code. Inside a workflow — the thing the entire ecosystem is racing to build — the workflow can't open either modal. It's stuck handing you a chat line and hoping you notice.

> **Worth knowing:** `<proposed_plan>` only renders as a real, reviewable plan when the session is actually in Plan Mode. Outside it, the tags show up as literal text. And `request_user_input` returns a hard error — "unavailable in Default mode" — when a workflow tries to use it without Plan Mode. The model then falls back to a plain chat question. Verified, both.

## Why a modal, and for whom

You might still say: a chat question is good enough. For you, hand-driving a yes/no, maybe. The necessity shows up the moment you look at the three people who actually depend on this.

**The skill/plugin author** is where the need is sharpest. A workflow has to *branch* on the answer. A free-text reply means the model re-parses your words — unreliably, differently each run. A modal returns a *structured choice* the workflow branches on with certainty, the same shape every time. You can't ship a dependable product on "it usually asks, and usually understands my reply." The modal is what turns *asking* into something you can build on.

**OpenAI** gets the cleanest signal to improve their models. A modal answer is a labeled record — *this context, these options, the user picked B* — which is exactly the thing models are worst at: knowing when to ask, what to ask, and which choice you wanted. A chat question that scrolls by unanswered teaches nothing. Structured checkpoints also make a real plugin ecosystem possible, and cut the wasted compute of confidently-wrong runs.

**The user** gets a decision they can't miss, answered with one keystroke or mouse click instead of a sentence the agent might misread — and the checkpoint comes *to* them at the fork, so they don't have to hover and watch.

Four things a chat line can't give you, and a modal can: **structured, reliable, un-missable, legible.** "Ask in chat" delivers none of them.

## The ask: you already built it

Here's the part that should make this easy.

OpenAI already built the unlock. There's a feature flag — `default_mode_request_user_input` — that turns the structured question modal on in normal mode, no Plan Mode required. I flipped it on and tested it: the modal fires, full structured payload, in default mode. It works *today*.

It's just shipped **off by default and marked "under development."** So a power user can set it in their config and have it now — but no plugin author can ship a workflow that depends on a flag the user has to discover and enable, on a feature that isn't finished.

And it's barely a build: Plan Mode exists, both modals exist, and the host can already enter Plan Mode programmatically. The only missing wire is letting a *workflow* do the same. Two ways to grant it:

- **Let a user prompt enter Plan Mode.** Give a workflow an `EnterPlanMode` / `ExitPlanMode` it can call from the prompt — exactly what issue [#11180](https://github.com/openai/codex/issues/11180) asks for. Grant that one capability and *both* modals — the question box and the reviewable plan — open from inside a workflow, instead of only from a human's hands. This is the real fix.
- **Or, at the very least, ship `default_mode_request_user_input`.** Flip the flag you already built from under-development-and-off to supported and on-by-default, so at least the question modal works in default mode — no Plan Mode required.

Two guardrails, so this doesn't become a different problem: keep it **author-placed and sparing** — a modal on every turn is worse than none — and keep the human as the one who approves. The agent gets to *raise* the checkpoint; you still *make* the call.

> **Worth knowing:** OpenAI doesn't take outside pull requests to Codex — their contributing guide says the most useful thing you can send is "detailed bug reports, analysis, and design discussion in issues," and features are prioritized by issue upvotes, not the forum. So the lever that actually moves is GitHub issue [#11180](https://github.com/openai/codex/issues/11180) — *Provide the EnterPlanMode and ExitPlanMode tool.* Upvote it, and add the default-mode `request_user_input` ask to the thread. Consider this post that design discussion.

## So — has Claude Code fallen behind Codex?

On the leaderboard, no — Codex caught up, fair and square.

On whether you can build a workflow you trust to run on its own, Claude Code is still ahead, for one unglamorous reason: it lets the *workflow* raise a real checkpoint, while in Codex that checkpoint appears only when you switch on Plan Mode by hand.

The strange part is that Codex has every piece already — the question modal, the plan-review modal, even the flag that frees the question modal from Plan Mode. It built the whole collaborative loop and then hid it behind one manual switch: only when you turn Plan Mode on by hand do both modals appear; leave it off, and the workflow gets neither.

> Fun fact: this post is created with Claude Opus 4.6
