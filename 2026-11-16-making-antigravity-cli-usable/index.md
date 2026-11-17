---
title: "9 Tips to Make Antigravity CLI Less Painful"
category: Programming
tags: [AI,Agent]
---

Gemini 4 is a strong model, but Google's Antigravity is painful to use. Because most developers prefer connecting to a CLI when working remotely, this post focuses on the Antigravity CLI (abbreviated as agy) and shares a few settings that cut down the friction and make it less painful to use.

In daily terminal work, four pain points stand out:

* **Permission prompts pop up constantly:** Cross-folder reads, scratch-file writes, MCP tool calls, and global skills installed through `npx skills` trigger repeated approval dialogs.
* **The context window size is fixed:** Antigravity provides no setting to resize or tune the context window limit for your workload.
* **Context compaction is poor:** Once a long session hits the compaction threshold, automatic summarization drops important details and degrades follow-up turns.
* **Input box shortcuts break terminal muscle memory:** In agy, unlike Claude Code or Codex, pressing Esc once or Ctrl+C does not clear typed text in the prompt box, and pressing Esc twice (Esc Esc) does not rewind the conversation.

You cannot fix the fixed context window or the poor compaction until Google updates the harness itself. To make agy less painful today, here are nine practical fixes across three areas: taming permission prompts, customizing the UI, observability, and privacy, and adapting to its keyboard shortcuts.

## Know Where Antigravity CLI Stores Its Config

Antigravity's CLI (agy) and its GUI surfaces do not share the same configuration files or setup methods, because they have different architectures and feature sets—for example, the GUI supports rich visual capabilities such as Generative UI, whereas agy is a standalone, lightweight Go binary built for terminal and remote SSH workflows.

> **Important:** Any permission preset or preference you change in a graphical Antigravity client will not apply to agy. The CLI reads and writes its own configuration files in `~/.gemini/antigravity-cli/`.

| CLI Configuration Item | Path in Antigravity CLI (agy) | Interactive Slash Command |
| :--- | :--- | :--- |
| **Runtime Settings & Tool Permissions** | `~/.gemini/antigravity-cli/settings.json` | `/settings` (or `/config`) and `/permissions` |
| **Custom Keybindings** | `~/.gemini/antigravity-cli/keybindings.json` | `/keybindings` |
| **Global Skills Directory** | `~/.gemini/antigravity-cli/skills/` (also scans `~/.gemini/skills/`) | — |

* **All CLI settings and the permission allowlist live in `~/.gemini/antigravity-cli/settings.json`:** You can edit this JSON file directly on disk, or update it live inside agy using `/settings` (for Agent Mode, Sandbox Mode, Non-Workspace Access, and Tool Permission) and `/permissions` (for the permission allowlist).
* **Global skills for agy live in `~/.gemini/antigravity-cli/skills/`:** Skills placed outside this directory (and outside `~/.gemini/skills/`) are either missed at startup or treated as external file accesses.

## Tame Repetitive Permission Prompts

At first glance, Antigravity feels frustrating because its default settings prompt on nearly every action. Once you examine how its controls fit together, however, **Antigravity's permission model is built around three core concepts—Project, Workspace, and Sandbox**:

* **Project:** Groups one or more physical repository directories on disk under a single project (configured in agy via `/projects` or `--add-dir`, defaulting to the launch directory alone under `default-cli-project`).
* **Workspace:** Formed by all directories configured in the active Project. When Agent Mode is set to Auto, Antigravity treats the Workspace as the sole default scope for file operations and intercepts even `read_file` calls outside it.
* **Sandbox:** Builds an OS-level isolation boundary around the Workspace (configured in agy via `"enableTerminalSandbox": true`, using Apple Seatbelt `sandbox-exec` on macOS and `bwrap` namespaces on Linux), letting you set Tool Permission to either **auto-approve inside the sandbox and ask outside** (`"proceed-in-sandbox"`) or **auto-approve everywhere** (`"always-proceed"`).

Once you see how Project, Workspace, and Sandbox relate (shown below), it becomes clear why the default settings stall constantly and how to configure auto-approval for different trust boundaries:

![An orthographic projection diagram titled "How Project, Workspace, and Sandbox Relate." On the left is an exploded isometric stack, and on the right are three vertically aligned leader-line callouts: at the bottom, "Project" (Composed of multiple directories: Main Repo, Repo A, Repo B, Shared Docs) projects upward into "Workspace" (Covers all directories under the Project), which in turn projects upward into "Sandbox" (Runs in Sandbox mode, covering Workspace).](./figure-1-workspace-sandbox-model.png "How Project, Workspace, and Sandbox Relate")

In the default state (shown below), even with Agent Mode set to Auto, agy runs with Sandbox Mode off, a single-folder default Project, Tool Permission set to Request review, and an empty `permissions.allow` list—so sibling repository accesses, shell commands, `/private/tmp` scratch files, system SDK reads, and MCP calls pause repeatedly for manual approval:

![A single-column vertical pipeline diagram titled "Default State." Each secondary block pairs a right-aligned status pill with an explicit "Effect:" line below: at the top, "Agent Mode: Auto (Auto-Allowed)" auto-approves file reads and writes inside the current Workspace; in the middle, "/settings & /projects" stacks "Sandbox Mode: Off (No Sandbox — Effect: Runs commands on host; cannot use Proceed in sandbox)," "Project: default-cli-project (Prompts — Effect: Workspace covers launch folder only; sibling repos prompt)," "Non-Workspace Access: Off (Prompts — Effect: With an empty allowlist, all paths outside Workspace prompt)," and "Tool Permission: Request review (Prompts — Effect: Prompts before every command such as git status, ls, npm test)"; below that, "/permissions" shows "permissions.allow: [] (Prompts — Effect: Prompts on every MCP call, /private/tmp write, and SDK read)"; at the bottom, the flow lands on a red "Pauses Repeatedly for Approval" card.](./figure-2-default-permission-flow.png "Default State")

Before presenting the two complete auto-approval recipes, we need two building blocks: **adding related repositories into the Workspace by configuring a Project**, and **populating the permission allowlist in the configuration file** for common external accesses.

### Add Other Repository Directories to the Workspace via Project

Because Antigravity's default rule for `read_file` is **Ask (Allowed in workspace)**—auto-allowed inside the Workspace, but prompting outside it even when Non-Workspace Access is on—the cleanest way to stop read prompts across related repositories (such as a frontend repo, a backend repo, and shared specs) is to add those directories to the Workspace and Sandbox boundary by configuring a Project.

In agy, use `/projects` (or `--project`) to configure directories under a Project, or mount extra folders into the current Workspace with `--add-dir` and `/add-dir`:

```bash
# Open a specific multi-directory Project directly at launch
agy --project=<project-id>

# Or mount extra directories into the active Workspace and Sandbox boundary on the fly
agy --add-dir ../backend --add-dir ../shared-specs
```

```text
# Right after entering agy, configure and switch to your Project first
/projects
/add-dir ../shared-specs
```

* **Create and switch Projects immediately after entering agy:** Switching Projects in agy **always starts a new conversation**. If you start chatting first and switch Projects mid-task, your current conversation stays behind in the old Project.
* **Remember to switch to the Project after creating it:** Creating a new Project in agy does *not* activate it automatically. Until you explicitly select **Switch to project** (or launch with `agy --project=<project-id>`), the session keeps running under the default `default-cli-project` and cross-folder reads continue to prompt.
* **Directories configured under the active Project are included in the Workspace:** Every folder in the active Project gets automatic access for `read_file`, `write_file`, and sandboxed shell commands without prompting.

### Populate the Permission Allowlist in Settings

For operations that sit outside your Project repository directories and would otherwise trigger Ask prompts—MCP servers, temporary file accesses under `/private/tmp` on macOS, and read access to system SDK directories (such as Apple's SDK directories) or shared reference directories—populate the `allow` permission allowlist via `/permissions` or directly under `"permissions"` in `~/.gemini/antigravity-cli/settings.json` (evaluated in Deny > Ask > Allow order):

```json
{
  "permissions": {
    "allow": [
      "mcp(playwright/*)",
      "mcp(chrome-devtools/*)",
      "mcp(cua/*)",
      "mcp(github/*)",
      "mcp(context7/*)",
      "write_file(/private/tmp)",
      "read_file(/Library/Developer/CommandLineTools/SDKs/)",
      "read_file(/Applications/Xcode.app/Contents/Developer/Platforms/)",
      "read_file(/path/to/shared-dir/)"
    ]
  }
}
```

* **Category 1 — `mcp(<server-name>/*)` approves all tools on trusted MCP servers at once:** In Antigravity's permissions table, MCP calls default to Ask. Adding wildcards for your regular MCP servers—such as `mcp(playwright/*)`, `mcp(chrome-devtools/*)`, `mcp(cua/*)` (Computer-Use Agent), `mcp(github/*)`, or `mcp(context7/*)`—lets the agent call every tool on those servers without pausing.
* **Category 2 — `write_file(/private/tmp)` silences both read and write prompts under `/private/tmp` on macOS:** On macOS, `/tmp` is a symbolic link to `/private/tmp`. When a tool resolves the real path `/private/tmp/...`, Antigravity treats it as outside the Workspace and prompts. Per the official permissions documentation, allowing `write_file(/private/tmp)` **implicitly grants `read_file(/private/tmp)` as well**, so one rule stops both read and write prompts for `/private/tmp`.
* **Category 3 — `read_file(...)` grants read access to system SDK directories (such as Apple's SDK paths) and shared reference directories:** Because paths outside the Workspace default to Ask, inspecting system headers or framework definitions (such as `/Library/Developer/CommandLineTools/SDKs/` and `/Applications/Xcode.app/Contents/Developer/Platforms/` on macOS) or shared reference directories triggers a permission prompt. Adding these system SDK directories and reference folders to `read_file(...)` overrides `"allowNonWorkspaceAccess": false` to stop repeat read prompts across every project and mounts those paths as read-only inside the terminal Sandbox.

### Choose an Auto-Approval Recipe in Settings

With your Project directories and `permissions.allow` list in place, open `/settings` in agy (or edit `~/.gemini/antigravity-cli/settings.json`) and choose between two complete permission recipes based on whether you want a strict boundary check or unrestricted execution:

#### Recipe 1: Auto-Allow Inside the Sandbox Boundary

This recipe lets the agent run without prompts inside your Workspace (including repositories added to your Project), terminal Sandbox, and `permissions.allow` paths, while pausing for confirmation whenever it tries to read or write an external path that you have not added to the Project or allowlist (shown below).

Launch agy with your multi-directory Project (or mount sibling directories on the fly):

```bash
agy --project=<project-id>
# Or mount sibling directories for the session:
agy --add-dir ../backend --add-dir ../shared-specs
```

And place the complete permission and allowlist configuration in `~/.gemini/antigravity-cli/settings.json`:

```json
{
  "agentMode": "auto",
  "enableTerminalSandbox": true,
  "allowNonWorkspaceAccess": false,
  "toolPermission": "proceed-in-sandbox",
  "permissions": {
    "allow": [
      "mcp(playwright/*)",
      "mcp(chrome-devtools/*)",
      "mcp(cua/*)",
      "mcp(github/*)",
      "mcp(context7/*)",
      "write_file(/private/tmp)",
      "read_file(/Library/Developer/CommandLineTools/SDKs/)",
      "read_file(/Applications/Xcode.app/Contents/Developer/Platforms/)",
      "read_file(/path/to/shared-dir/)"
    ]
  }
}
```

![A single-column vertical pipeline diagram titled "Recipe 1: Auto-Allow Inside the Sandbox Boundary." At the top, "Agent Mode: Auto (Auto-Allowed)" auto-approves file reads and writes inside the current Workspace. In the middle, "/settings & /projects" stacks "Sandbox Mode: On (Sandboxed — Effect: Isolates shell commands in OS sandbox; unlocks Proceed in sandbox)," "Project: /projects · --add-dir (Auto-Allowed — Effect: Expands Workspace to sibling repos so cross-repo IO never prompts)," "Non-Workspace Access: Off (Boundary Gate — Effect: Prevents silent external writes in Auto mode; defers to allowlist)," and "Tool Permission: Proceed in sandbox (Auto-Allowed — Effect: Auto-approves commands in sandbox such as git status, ls, npm test)." Below that, "/permissions" stacks "permissions.allow (Auto-Allowed — Effect: Overrides Non-Workspace Access: Off to pass mcp(playwright/*), write_file(/private/tmp), and read_file(SDKs/*))" and "Unlisted External Paths & MCPs (Prompts — Effect: Any external path or MCP not in permissions.allow pauses for review)." At the bottom, the flow lands on a teal "Auto-Allowed in Boundary, Guarded Outside" card.](./figure-3-recipe-1-sandbox-flow.png "Recipe 1: Auto-Allow Inside the Sandbox Boundary")

#### Recipe 2: Always Proceed Everywhere

If you work in a dedicated cloud VM or container—or simply want the agent to charge ahead across both Workspace and external directories without stopping for file permission prompts—set `"toolPermission"` to `"always-proceed"` and `"allowNonWorkspaceAccess"` to `true`. Because external file reads, writes, `/private/tmp`, and SDK directories are approved automatically, you do not need to configure a multi-directory Project or file-path allowlist rules; only the trusted MCP server rules remain in `permissions.allow` (or launch with `agy --dangerously-skip-permissions` to skip even MCP prompts, as shown below):

```json
{
  "agentMode": "auto",
  "enableTerminalSandbox": true,
  "allowNonWorkspaceAccess": true,
  "toolPermission": "always-proceed",
  "permissions": {
    "allow": [
      "mcp(playwright/*)",
      "mcp(chrome-devtools/*)",
      "mcp(cua/*)",
      "mcp(github/*)",
      "mcp(context7/*)"
    ]
  }
}
```

![A single-column vertical pipeline diagram titled "Recipe 2: Always Proceed Everywhere." At the top, "Agent Mode: Auto (Auto-Allowed)" auto-approves file reads and writes inside the current Workspace. In the middle, "/settings & /projects" stacks "Sandbox Mode: On (Sandboxed — Effect: Keeps OS-level sandbox containment around ~/.ssh and network)," "Project: default-cli-project (Auto-Allowed — Effect: No manual Project setup needed; sibling repos pass via settings below)," "Non-Workspace Access: On (Auto-Allowed — Effect: Lifts the Workspace boundary so external folders can be accessed)," and "Tool Permission: Always proceed (Auto-Allowed — Effect: Auto-approves all commands and external file IO including /private/tmp and SDKs)." Below that, "/permissions" shows "permissions.allow (Auto-Allowed — Effect: Auto-approves trusted MCP calls; file paths already pass above)." At the bottom, the flow lands on a green "Runs Unrestricted Everywhere" card.](./figure-4-recipe-2-unrestricted-flow.png "Recipe 2: Always Proceed Everywhere")

Here is how the core settings in both recipes interact:

* **Keep Agent Mode (`"agentMode"`) set to `"auto"`:** Although Agent Mode offers Default, Plan, Auto, and Accept Edits (cycled with Shift + Tab), `"auto"` is the standard choice for daily work and approves file reads and writes inside your current Workspace (note that Antigravity's permission rules only define `read_file` and `write_file`—there is no separate `edit_file` permission action).
* **Turn on Sandbox Mode (`"enableTerminalSandbox": true`):** By default, agy runs outside the Sandbox. Enabling Sandbox Mode isolates terminal commands using Apple Seatbelt (`sandbox-exec`) on macOS or `bwrap` namespaces on Linux, blocking unauthorized network access and host secrets (such as `~/.ssh`) while unlocking Proceed in sandbox.
* **Under Recipe 1, keep Non-Workspace Access (`"allowNonWorkspaceAccess"`) set to `false` to avoid the "prompts on reads, silent on writes" trap:** When `"allowNonWorkspaceAccess"` is `false`, any access outside the Workspace pops up a three-option menu whose second option permanently enables Non-Workspace Access. Many users select that second option hoping to stop repeat prompts, **which triggers a counterintuitive trap in Auto mode**: because Auto mode auto-approves file edits while `read_file` falls back to Ask (Allowed in workspace), flipping `"allowNonWorkspaceAccess"` to `true` under `"proceed-in-sandbox"` causes Antigravity to **still prompt when reading an unwhitelisted external file, yet silently create or overwrite any file outside your Workspace (`write_file`) without a single prompt**! Conversely, **`permissions.allow` rules take precedence over `"allowNonWorkspaceAccess": false`**: in Recipe 1, keeping `"allowNonWorkspaceAccess"` set to `false` and adding your trusted external paths to `permissions.allow` lets those whitelisted paths pass with zero prompts while blocking both unwhitelisted external reads and unwhitelisted external writes.
* **Set Tool Permission (`"toolPermission"`) to select your recipe:** The default Request review setting prompts before every `git status`, `npm test`, or `ls -la`. Switching to `"proceed-in-sandbox"` (**Recipe 1**) auto-approves everything inside the Workspace, Sandbox, and `permissions.allow` list while prompting outside it; switching to `"always-proceed"` (**Recipe 2**) auto-approves file reads, writes, and commands both inside and outside the Workspace.

### Fix Permission Prompts Caused by the Wrong npx skills Install Directory

Global skills installed with `npx skills` fail to load at startup and trigger permission prompts when read because **`npx skills` installs them into the wrong directory**. Running `npx skills add <owner/repo> -g` places skill files in `~/.agents/skills/` instead of agy's actual global skills directory (`~/.gemini/antigravity-cli/skills/`). Because `~/.agents/skills/` sits outside agy's skills directory and outside your active Workspace, reading a skill's `SKILL.md` or helper scripts triggers an external file access prompt.

Fix this by linking `~/.agents/skills` back to `~/.gemini/antigravity-cli/skills/` with a symbolic link (`ln -s`, or a macOS Finder alias):

```bash
mkdir -p ~/.gemini/antigravity-cli/skills

# Move any existing global skills into the right directory first
mv ~/.agents/skills/* ~/.gemini/antigravity-cli/skills/ 2>/dev/null || true
rm -rf ~/.agents/skills

# Symlink ~/.agents/skills back to ~/.gemini/antigravity-cli/skills
ln -s ~/.gemini/antigravity-cli/skills ~/.agents/skills
```

* **Subsequent `npx skills` installs land in the right directory:** Every `npx skills add <owner/repo> -g` command now writes straight into `~/.gemini/antigravity-cli/skills/`, so agy discovers your skills at startup and reads them without prompting.

## Customize the UI, Observability, and Privacy

By default, agy collects usage telemetry, exposes your personal account information in the top bar, cycles through usage tips at the bottom, and collapses execution details and session history. The next four settings lock down your privacy and clean up the interface.

### Turn Off Telemetry

Antigravity enables **Enable Telemetry** by default to collect usage data. If you care about Workspace and session privacy, turn it off right away.

There is one catch: when you sign in with a Google account, **Enable Telemetry** is stored as a cloud-synced account preference rather than read from your local `settings.json`, whereas API-key sessions read `"enableTelemetry": false` from `~/.gemini/antigravity-cli/settings.json` (or the `--disable_telemetry` flag). Turn off both so you are covered in every mode:

1. Inside an agy session, run `/settings` (or `/config`), type telemetry to filter the list, and toggle **Enable Telemetry** to **off**.
2. Add `"enableTelemetry": false` to `~/.gemini/antigravity-cli/settings.json`:

```json
{
  "enableTelemetry": false
}
```

* **Toggling Enable Telemetry to off in `/settings` updates your account-level setting:** Once disabled, sessions signed into your Google account stop sending usage telemetry.
* **Setting `"enableTelemetry": false` in `settings.json` covers local and API-key sessions:** It ensures CLI-level telemetry stays off even when you run agy without a Google account login.

### Hide Account Info and the Startup Logo

At launch, agy prints a colored pixel-art ASCII logo on the left of the terminal header and displays your signed-in Google account email right beside it (top window below). If you livestream your coding sessions, record video demos, or share terminal screenshots, that header exposes your personal email address to viewers.

Add two environment variables to `~/.zshrc` (or `~/.bashrc`) to hide them in every session (bottom window below):

```bash
export AGY_CLI_HIDE_ACCOUNT_INFO=1
export AGY_CLI_HIDE_LOGO=1
```

![A vertical comparison of two terminal windows titled "Hiding Account Info and the Startup Logo." The top window, "Default Launch (agy)," shows the colored pixel-art "A" startup logo on the left alongside "Antigravity CLI 1.5.10," "your.name@domain.com," "Gemini 4 Carbon (Medium)," and the workspace path on the right. The bottom window, "With AGY_CLI_HIDE_ACCOUNT_INFO=1 and AGY_CLI_HIDE_LOGO=1," removes both the pixel-art logo and the email line, leaving a compact three-line header with "Antigravity CLI 1.5.10," "Gemini 4 Carbon (Medium)," and the workspace path.](./figure-5-hide-account-and-logo.png "Hiding Account Info and the Startup Logo")

If you want to keep the default header during solo work and hide it only when livestreaming or recording your screen, wrap them in a shell `alias` instead:

```bash
alias agy-live='AGY_CLI_HIDE_ACCOUNT_INFO=1 AGY_CLI_HIDE_LOGO=1 agy'
```

* **`AGY_CLI_HIDE_ACCOUNT_INFO=1` hides your account email for streams and screenshots:** It removes your signed-in email line from the header so you can stream or record the terminal safely.
* **`AGY_CLI_HIDE_LOGO=1` hides the ASCII startup logo:** It removes the multi-line pixel-art logo to keep the header compact in narrow split panes and `tmux` windows.

### Turn Off Rotating Usage Tips

While Gemini 4 generates a response, agy displays rotating usage tips below the spinner. Once you know the shortcuts, those changing lines are just visual distraction.

Turn them off in `~/.gemini/antigravity-cli/settings.json` (or switch **Show Tips** off via `/settings`):

```json
{
  "showTips": false
}
```

### Set Verbosity to High and Group the Conversation Picker by Workspace

To get full observability into what the agent is doing and keep your `/resume` history organized across projects, enable two options in `/settings` (or `~/.gemini/antigravity-cli/settings.json`):

```json
{
  "verbosity": "high",
  "pickerGrouping": "grouped"
}
```

* **`"verbosity": "high"` (Verbosity) gives you full observability:** The default `"medium"` setting folds related tool calls and thoughts into summaries. Setting `"verbosity"` to `"high"` renders every tool call, background command, and thought process in full detail.
* **`"pickerGrouping": "grouped"` (Conversation Picker Grouping) groups `/resume` by Workspace:** The default `"none"` setting dumps all past conversations into one flat list sorted by time. Setting `"pickerGrouping"` to `"grouped"` organizes the `/resume` picker by Workspace (you can also press Ctrl+F inside `/resume` to toggle grouping on the fly).

## Adapt to the Non-Standard Keyboard Shortcuts

### Use Double Esc to Clear Input and Slash Commands to Rewind

If you come to agy from Claude Code or Codex, the prompt box shortcuts feel broken at first. According to the official CLI reference, this behavior is by design because agy binds Esc and Ctrl+C to a protected `cli.escape` action with different rules:

| Action | Claude Code / Codex | Antigravity CLI (agy) |
| :--- | :--- | :--- |
| **Clear typed text in the prompt box** | Ctrl+C or single Esc | Press **Esc twice (Esc Esc)** while idle |
| **Rewind conversation to an earlier turn** | Press Esc twice (Esc Esc) on an empty prompt | Type **`/rewind`** (or **`/undo`**) |
| **Stop an active generation stream** | Esc or Ctrl+C | Press **Esc once** or **Ctrl+C once** |
| **Exit the CLI session** | Ctrl+D or Ctrl+C twice | Press **Ctrl+D** (on an empty prompt) or **Ctrl+C twice** while idle |

* **A single Esc or Ctrl+C will not clear your input text:** When no response stream is running, pressing Esc once does nothing to typed text, and pressing Ctrl+C twice exits the agy session altogether.
* **Esc Esc clears the prompt box instead of rewinding:** Because agy uses double Esc to wipe the input box, pressing Esc twice never opens the rewind menu.
* **Use `/rewind` (or `/undo`) to roll back history:** You must type `/rewind` or its shorter alias `/undo` explicitly to return the conversation to a previous message.

## Full Copy-Paste Configuration

Pick one of the two recipes below and merge it into `~/.gemini/antigravity-cli/settings.json` (and remember to open `/settings` inside agy once, search telemetry, and set **Enable Telemetry** to off for your account):

### Recipe 1: Auto-Allow Inside the Sandbox Boundary

```json
{
  "agentMode": "auto",
  "enableTerminalSandbox": true,
  "allowNonWorkspaceAccess": false,
  "toolPermission": "proceed-in-sandbox",
  "enableTelemetry": false,
  "verbosity": "high",
  "pickerGrouping": "grouped",
  "showTips": false,
  "permissions": {
    "allow": [
      "mcp(playwright/*)",
      "mcp(chrome-devtools/*)",
      "mcp(cua/*)",
      "mcp(github/*)",
      "mcp(context7/*)",
      "write_file(/private/tmp)",
      "read_file(/Library/Developer/CommandLineTools/SDKs/)",
      "read_file(/Applications/Xcode.app/Contents/Developer/Platforms/)",
      "read_file(/path/to/shared-dir/)"
    ]
  }
}
```

### Recipe 2: Always Proceed Everywhere

```json
{
  "agentMode": "auto",
  "enableTerminalSandbox": true,
  "allowNonWorkspaceAccess": true,
  "toolPermission": "always-proceed",
  "enableTelemetry": false,
  "verbosity": "high",
  "pickerGrouping": "grouped",
  "showTips": false,
  "permissions": {
    "allow": [
      "mcp(playwright/*)",
      "mcp(chrome-devtools/*)",
      "mcp(cua/*)",
      "mcp(github/*)",
      "mcp(context7/*)"
    ]
  }
}
```

Add the privacy environment variables to `~/.zshrc`:

```bash
export AGY_CLI_HIDE_ACCOUNT_INFO=1
export AGY_CLI_HIDE_LOGO=1
```

Then link the global skills directory once in your terminal:

```bash
mkdir -p ~/.gemini/antigravity-cli/skills
mv ~/.agents/skills/* ~/.gemini/antigravity-cli/skills/ 2>/dev/null || true
rm -rf ~/.agents/skills
ln -s ~/.gemini/antigravity-cli/skills ~/.agents/skills
```
