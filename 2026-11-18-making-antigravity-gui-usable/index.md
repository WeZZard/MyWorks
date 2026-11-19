---
title: "Why You Shouldn't Miss Antigravity app"
subtitle: "Antigravity app's Core Tools, iPad Remote Control, Turbo Permissions, and Cross-Client Skills"
category: Programming
tags: [AI,Agent]
---

When I wrote [9 Tips to Make Antigravity CLI Less Painful](https://wezzard.com/post/2026/11/making-antigravity-cli-usable), I started with the command-line client (`agy`) largely because most third-party remote control clients at the time were built around CLI agents. In practice, however, the 2.0 **Antigravity app** ships with native Remote Control out of the box—and paired with its multi-tab right side panel, it delivers a richer, more multi-dimensional project creation experience.

As shown below, **Antigravity app** brings five core project tools into one workspace—**Generative UI**, **Artifacts**, **Walkthrough Checklists**, **Review**, and **Side Question** (`/btw`)—plus native **Remote Control** (once you add [antigravity.google.com](https://antigravity.google.com) to your iPad Home Screen, it turns into a full-screen app running directly on your iPad):

![Six abstract figures arranged horizontally in a single row, each with a schematic illustration on top and a subtitle below: "Generative UI (Interactive HTML Widgets)," "Artifacts (Pinned Side-Panel Outputs)," "Walkthrough Checklist (Human-Readable Audit List)," "Review (Turn & Branch Diff Review)," "Side Question (/btw Read-Only Fork Q&A)," and "Remote Control (Web & iPad Remote Access, showing an iPad tablet silhouette in the back and a Web browser window with the Google Chrome logo staggered in the front)."](./figure-0-antigravity-app-overview.png "Antigravity app's core project tools and native Remote Control")

This guide first walks through the visual side-panel workflow in **Antigravity app** and the iPad Remote Control experience, then shows how to fix the two configuration glitches you will run into out of the box:

1. **How permissions are configured:** Why Auto mode still prompts, and how to switch both local permissions (**This Computer**) and Remote Control permissions (**Remote**) to **Turbo**.
2. **Where to place and install Skills and Plugins:** How to unify global skill discovery and plugin management across **Antigravity app**, **Antigravity IDE**, and **Antigravity CLI** (`agy`).

## Antigravity app's Unique Advantage: Generative UI and the Side Panel

Compared with a terminal-only client or a third-party CLI wrapper, **Antigravity app** earns its keep through Generative UI and its right side panel. It ships with built-in skills like **Generative UI** (whose default prompts we can further upgrade with custom skills of our own), and its side-panel tools—**Artifacts**, **Walkthrough**, **Review**, and **Side Question** (`/btw`)—bring interactive simulation, milestone checklists, diff review, and non-intrusive codebase Q&A into one window.

### Generative UI, Artifacts, and Walkthrough Checklists

**When building a project in Antigravity app, use the built-in `generative_ui` skill to turn abstract logic into interactive HTML Artifacts, and explicitly ask the agent to generate a Walkthrough so you get a human-readable Markdown checklist to track implementation and verification.**

As shown in the screenshot below from a Token Bucket rate-limiter session, the conversation pane on the left embeds an interactive HTML simulator (`token_bucket.html`, with Refill Rate and Burst Capacity sliders and a live purple bucket meter), the side panel on the right opens the **Walkthrough** checklist, and the **Artifacts** rail on the far right pins every generated artifact for quick access:

![A screenshot of Antigravity app showing an inline Generative UI artifact on the left and the Walkthrough tab in the side panel on the right. On the left, the conversation embeds an interactive Token Bucket rate-limiter widget with sliders for Refill Rate (4.0 tokens/s) and Burst Capacity (20 tokens), a live purple progress bar showing 20.0 / 20 tokens (100%), action buttons (Send Request -1, Burst 5 Requests -5, Refill Full), and a Walkthrough card below. On the right, the side panel displays the "Walkthrough" tab ("Token Bucket Simulator Walkthrough") containing a human-readable Markdown checklist ("Simulator Summary Checklist") alongside the Artifacts sidebar listing Walkthrough and Token Bucket.](./figure-3-generative-ui-and-walkthrough.png "Interactive Generative UI widget inline on the left, the Walkthrough Markdown checklist in the right side panel, and the Artifacts rail on the far right")

* **Generative UI and Artifacts make project state tangible:** Using the built-in `generative_ui` skill, the agent renders self-contained interactive HTML widgets either inline in the chat or pinned in the **Artifacts** rail as standalone tabs in the right side panel, helping you inspect and test complex project logic visually.
* **A Walkthrough is a human-readable Markdown checklist:** Asking the agent to generate a **Walkthrough** produces a structured Markdown audit checklist summarizing what changed and how it was verified, making multi-step projects far easier to steer.

### The Review Pane and Side Question

**Like many other mainstream agent clients, Antigravity app also supports Review and Side Question (`/btw`) in its right side panel—letting you inspect diffs by turn or branch and commit to Git in place, or fork a read-only background tab to answer mid-task questions without polluting your main conversation.**

Whenever the agent creates or edits files (such as updating `rate_limiter.py` to add `burst_limit` and `reset()`), a "1 file changed +16 -0" summary card appears at the bottom of the turn. Clicking **Review** on that card (or pressing Cmd+Option+O) opens the **Review** tab in the right side panel:

![A screenshot of Antigravity app showing the Review pane in the right side panel. On the left, the conversation shows the "1 file changed +16 -0" card with a "Review" button. On the right, the "Review" tab is active, filtered to "For Turn: Use write_file to create rate_limiter.py...", displaying the green syntax-highlighted diff of rate_limiter.py.](./figure-4-review-pane.png "Opening the Review tab in the right side panel to inspect diffs for a single turn")

When you need a quick answer from the codebase without interrupting the main conversation or adding extra turns to its context window, type `/btw <question>` in the prompt box to open a **Side Question** tab in the right side panel:

![A screenshot of Antigravity app showing a Side Question (/btw) tab in the right side panel. On the left, the main conversation remains untouched. On the right, the "Token Bucket Refill Calculati..." tab ("Side Question: Token Bucket Refill Calculation And Code") shows "Started from 'In the current folder, do 3 quick tasks...'", "Worked for 6s", the calculated Refill Duration (5.0 seconds) and Refill Loop Location in token_bucket.html, and a separate follow-up message box at the bottom right.](./figure-5-side-question-btw.png "Asking a /btw Side Question opens an independent read-only fork in the right side panel")

* **The Review pane filters diffs across four views:** Beyond inspecting a single turn (**For Turn**), you can switch the Review pane to **Uncommitted** working-tree changes, **Branch** changes against the base branch, or all **Agent Edits** in the conversation, leave line-by-line review comments, and stage and commit directly to Git.
* **Side Question (`/btw`) keeps your main context window clean:** Running `/btw` forks the conversation history at that moment into a read-only background turn that can read files, search your workspace, and accept follow-up questions in its own side-panel tab without writing a single token back to the main thread.

Antigravity app also includes `/automation` for scheduling recurring background tasks (stored under `~/.gemini/config/sidecars/<id>/sidecar.json`) and supports connecting external apps under **Customizations**—though because of Antigravity's current market share, third-party vendor coverage is still sparse, and hardware ecosystems like **Plaud** do not have official support yet.

## Remote Control in Antigravity app and Running It as an iPad App

**Antigravity app includes native Remote Control; adding [antigravity.google.com](https://antigravity.google.com) to your iPad Home Screen turns it into a full-screen app running on your iPad, and paired with the host setup on your Mac, it lets you control your home Mac from the iPad anytime.**

### Turning antigravity.google.com into an App Running on Your iPad

Open [antigravity.google.com](https://antigravity.google.com) in Safari on your **iPad**, sign in with your Antigravity account, and follow the two steps marked below to install it onto your iPad Home Screen:

1. Tap the **Share** button in the top-right Safari toolbar to open the Share menu.
2. Tap **Add to Home Screen** in the Share menu.

![An annotated iPad Safari screenshot showing how to add antigravity.google.com to the Home Screen. Callout "1. Open Share Menu →" points to the Share icon in the top-right Safari toolbar, and callout "2. Tap Add to Home Screen →" highlights the "+ Add to Home Screen" row at the bottom of the open Share popover.](./figure-7a-ipad-add-to-home-screen.png "Opening the Safari Share menu on iPad and tapping Add to Home Screen")

Launching it from your iPad Home Screen strips away the browser chrome and turns it into a standalone full-screen app on the iPad, bringing the visual side-panel workflow directly to iPadOS—including scrubbing and interacting with live **Generative UI** artifacts in the right side panel, as shown in the animated composite below:

![An animated composite of an iPad Pro running the Antigravity Remote Control web app in full screen. On the left is the active remote conversation running in Turbo mode with an inline interactive sandbox architecture card; on the right side panel is the "Workloads And Acceptance" Generative UI tab where the "Continuation Scrub Progress" slider and the "WL-1 · Single-Host Iterative Repository Repair Chain" pipeline animate smoothly from Phase 1/4 through Phase 4/4.](./figure-8-ipad-remote-control.gif "Running antigravity.google.com as a desktop web app on an iPad to remotely control a home Mac")

### Mac Host Keep-Alive Settings and Side-Panel Differences

To keep your Mac at home ready for incoming iPad connections, open **Settings > Application** in **Antigravity app** on your Mac and turn on all three switches shown below:

![A screenshot of the Settings > Application panel in Antigravity app. Under General, both "Prevent Sleep (Prevent the computer from sleeping while the app is running.)" and "Keep In Menu Bar (Keep the app accessible from the menu bar and running in the background when all windows are closed.)" are toggled on. Under Remote Control, "Enable Remote Control (Work with local agents from another device.)" is toggled on, showing the Device Name (macbookair-m1) and an anonymized QR code.](./figure-7-remote-control-settings.png "Enabling Prevent Sleep, Keep In Menu Bar, and Enable Remote Control under Settings > Application")

* **Turn on Prevent Sleep so the remote host stays reachable:** If the host machine enters system sleep, active agent tasks and remote browser connections drop immediately; enabling **Prevent Sleep** keeps the computer awake while Antigravity app is running.
* **Turn on Keep In Menu Bar so the app runs in the background after closing windows:** With **Keep In Menu Bar** enabled, closing the main Antigravity app window leaves the application resident in the macOS menu bar so the background daemon continues serving iPad Remote Control sessions.

When you use **Antigravity app** locally on your Mac desktop, the right side panel also includes a built-in **Browser** tab (shown below) that renders live web pages right next to your conversation:

![A screenshot of the local desktop Antigravity app showing the built-in Browser tab in the right side panel. On the left is the Token Bucket conversation and inline Generative UI widget; on the right, the side panel displays the built-in "Example Domain" browser tab with a URL bar (example.com), navigation controls, and a screenshot button, rendering the live web page directly inside the side panel.](./figure-6-builtin-browser-tab.png "The local desktop Antigravity app includes a built-in Browser tab in the right side panel")

* **The Remote Control web UI omits the side-panel Browser tab:** On the local desktop Antigravity app, the right side panel includes the built-in **Browser** tab shown above; when you connect through [antigravity.google.com](https://antigravity.google.com) via Remote Control, that side-panel Browser tab is not present. As the iPad workflow above demonstrates, pairing Remote Control with **Generative UI (Artifacts)** and **Walkthrough** checklists remains a great way to drive projects remotely, and whenever you need to verify a web UI from afar, you can ask the agent to capture screenshots into the Walkthrough.

Now that we have seen the visual workflow and iPad Remote Control capabilities of **Antigravity app**, let's look at how to set it up and resolve two out-of-the-box glitches: **how permissions are configured** and **where to place and install Skills and Plugins**.

## Why Auto Mode Still Prompts

**The Auto preset in Antigravity app is not Claude Code's Auto Mode or Codex's Approve for me mode, and Antigravity app splits permissions into two independent settings—This Computer for local sessions and Remote for Remote Control sessions (where Remote does not even have an Auto option). To eliminate permission dialogs everywhere, set both This Computer and Remote to Turbo.**

Open **Settings > General > Permissions** in **Antigravity app**, where you will find two separate dropdowns: **This Computer** (for local conversations) and **Remote** (for Remote Control conversations from your iPad or browser). Switch both of them to **Turbo**:

![A side-by-side screenshot of the Settings > General > Permissions panel in Antigravity app comparing This Computer and Remote permission presets. The left panel ("① Local: This Computer → Turbo") shows the This Computer dropdown open with four presets: Request Review, Default, Auto, and the selected Turbo. The right panel ("② Remote Control: Remote → Turbo (Configured Separately)") shows the Remote dropdown open with only three presets: Request Review, Default, and the selected Turbo (no Auto preset).](./figure-1a-turbo-preset-ui.png "Switching both This Computer and Remote to Turbo under Settings > General > Permissions")

Comparing the permission boundaries of the Auto and Turbo presets below shows why Auto continues to stall on permission dialogs and what Turbo unlocks:

![A two-column comparison diagram titled "Permission Presets in GUI Antigravity." On the left, "Auto Preset" stacks four cards marked "Prompts": "Terminal Sandbox: On (Blocks outbound network; npm install and git push must leave the sandbox)," "File Scope: Workspace Only (Reads and writes in sibling repos or external folders ~/.agents/skills pause)," "Shell: $(...) & {a,b} (git log $(whoami) or mkdir -p src/{api,ui} bypasses prefix allowlists)," and "MCP & Web: Ask (Every MCP tool call and web page fetch pauses for manual confirmation)," landing on a red "Pauses Repeatedly for Approval" outcome card. On the right, "Turbo Preset" stacks "enableTerminalSandbox: false," "nonWorkspaceFileAccess: ALLOW," "autoExecutionPolicy: EAGER," and "MCP & Web: Allowed," landing on a green "Switch to Turbo to Run Unrestricted (Set both This Computer and Remote to Turbo in Settings > General > Permissions)" outcome card.](./figure-1-auto-vs-turbo-flow.png "Permission Presets in GUI Antigravity")

* **Remote Control permissions (Remote) are configured separately from local permissions (This Computer), and Remote has no Auto preset:** As shown in the right-hand panel of the screenshot above, the **Remote** dropdown only offers **Request Review**, **Default**, and **Turbo**. If you switch **This Computer** to **Turbo** but leave **Remote** at **Default**, every remote session from your iPad will still pause on permission dialogs.
* **The Auto preset still locks file operations inside the workspace and prompts on every MCP call or web fetch:** Reading or writing any path outside your active project folders (including sibling repositories or external skill directories) or calling any MCP tool pauses the session with a permission dialog.
* **Everyday shell commands that need network access or use `$(...)` and `{a,b}` still prompt under Auto:** Because the terminal sandbox blocks outbound network access by default, commands like `npm install` or `git push` must leave the sandbox; even if you allow `git` or `mkdir`, any command containing `$(...)` or `{a,b}`—such as `git log $(whoami)`, `kill $(lsof -t -i:3000)`, or `mkdir -p src/{api,ui}`—bypasses your prefix allowlist and pauses for approval.
* **The Turbo preset is the exact equivalent of Auto + Always Proceed in [9 Tips to Make Antigravity CLI Less Painful](https://wezzard.com/post/2026/11/making-antigravity-cli-usable):** Selecting **Turbo** for both **This Computer** and **Remote** disables the terminal sandbox, opens full filesystem access, and lets all shell commands and MCP tools run without interruption across both local and iPad Remote Control sessions.

## Why You Can't Find Your Installed Skills in Antigravity

**Because Antigravity has shipped multiple clients over time, it has accumulated several different global skill directory configurations; to make global skills work across Antigravity app, Antigravity IDE, and Antigravity CLI (`agy`) simultaneously, converge on `~/.gemini/config`, then mount the global `/Users/<your-username>/.agents/skills` directory by absolute path in `~/.gemini/config/skills.json`.**

The diagram below shows which global directories each of the three clients reads:

![A routing diagram titled "Why You Can't Find Your Installed Skills in Antigravity." At the top are the three client cards with their respective application icons: "Antigravity app (2.0 Desktop App)," "Antigravity IDE (Standalone Editor)," and "Antigravity CLI (Terminal CLI agy)." Solid green routing lines connect all three clients to the left green directory box ("All 3 Clients: ~/.gemini/config/skills/, ~/.gemini/config/skills.json, ~/.gemini/config/plugins/"); a dashed amber line connects only Antigravity IDE to the center amber box ("IDE Only: ~/.gemini/antigravity/skills/"); a dashed amber line connects only Antigravity CLI to the right amber box ("CLI Only: ~/.gemini/antigravity-cli/skills/, ~/.gemini/skills/"). Below the connected boxes sits a red dashed box marked "Ignored by All 3: ~/.agents/skills/." At the bottom is the green outcome card "The Fix: Converge on ~/.gemini/config (Then mount the global /Users/<you>/.agents/skills directory in skills.json)."](./figure-2-cross-client-skills-fix.png "Why You Can't Find Your Installed Skills in Antigravity")

* **The symlink approach in [9 Tips to Make Antigravity CLI Less Painful](https://wezzard.com/post/2026/11/making-antigravity-cli-usable) only targets the CLI:** Symlinking `~/.agents/skills` to `~/.gemini/antigravity-cli/skills` works only for `agy`, whereas registering it in `~/.gemini/config/skills.json` covers all three clients.
* **Do not run `ln -sf` onto an existing `~/.gemini/config/skills/` folder:** Antigravity scans each skill directory only one level deep, so a nested `~/.gemini/config/skills/skills` symlink is silently skipped.
* **Always write an absolute `path` in `~/.gemini/config/skills.json`:** The manifest loader does not expand `~`, so write a full path such as `/Users/<your-username>/.agents/skills`.

Instead of editing `~/.gemini/config/skills.json` by hand, run the idempotent script below. It checks and creates the `~/.gemini/config/` directory hierarchy and `skills.json` file on demand, preserves any existing JSON structure and keys, and checks for duplicates before inserting your `~/.agents/skills` path:

```bash
python3 - <<'PY'
import json
from pathlib import Path

config_dir = Path.home() / ".gemini" / "config"
skills_json = config_dir / "skills.json"
target_path = str(Path.home() / ".agents" / "skills")

# 1. Create the directory hierarchy on demand if missing
config_dir.mkdir(parents=True, exist_ok=True)

# 2. Preserve any existing JSON structure in skills.json
data = {}
if skills_json.is_file() and skills_json.stat().st_size > 0:
    data = json.loads(skills_json.read_text(encoding="utf-8"))

entries = data.setdefault("entries", [])

# 3. Check whether the entry already exists to avoid duplicate insertion
if not any(isinstance(e, dict) and e.get("path") == target_path for e in entries):
    entries.append({"path": target_path})
    skills_json.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Inserted {target_path} into {skills_json}")
else:
    print(f"Already exists in {skills_json}: {target_path}")
PY
```

### How Plugins Work Across the Three Clients

**Unlike loose global skills, Plugins automatically share a single global directory (`~/.gemini/config/plugins/<plugin-name>/`) and state file (`~/.gemini/config/config.json`) across all three clients, syncing enabled states between Antigravity app and `agy`.**

* **In Antigravity app:** Open **Customizations** in the left sidebar to install catalog bundles from **Marketplace** or toggle plugins, enter required API keys, and trigger browser OAuth 2.0 sign-in under **Installed** (or click inline `<plugin-card>` embeds in chat).
* **In Antigravity CLI (`agy`):** Run `/plugin` inside the TUI for the interactive manager, or run `agy plugin install|enable|disable|uninstall|list|validate|import` in your shell (using `agy plugin import gemini|claude` to migrate Gemini CLI or Claude Code extensions).
* **In Antigravity IDE:** Place plugin directories in `.agents/plugins/` or `~/.gemini/config/plugins/` and inspect active components from the **Customizations** dropdown in the agent side panel.
