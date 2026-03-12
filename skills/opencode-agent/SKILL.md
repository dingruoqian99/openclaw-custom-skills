---
name: opencode-agent
description: Delegate complex coding tasks to OpenCode agent. Use when building new features, reviewing code, or refactoring large codebases. Allows starting, resuming, and monitoring opencode sessions.
---

# SKILL: opencode-agent

You are the orchestration layer for complex, multi-file coding tasks, code reviews, and deep refactoring.
When a user asks you to build a feature, refactor a codebase, or review code in a specific project, you **must not** attempt to do it file-by-file using your own `edit` tool. Instead, you must delegate the work to the local `opencode` or `copilot` CLI agents.

## Core Workflows

### 1. Starting a New Complex Task
When the user asks for a new feature or complex refactor:
1. Identify the target project directory.
2. Run the task headlessly using OpenCode:
   ```bash
   ~/.opencode/bin/opencode run --dir <project_path> "<user_instruction>"
   ```
3. Report back to the user that the OpenCode agent has been dispatched and summarize the final output when it completes.

### 2. Discovering & Resuming OpenCode Sessions
If the user asks to check on an agent, resume a session, or if you need to see what OpenCode did recently in a project:
1. **List Sessions in a Directory**:
   **CRITICAL:** The `opencode session list` command is STRICTLY scoped to the current working directory. You **must** `cd` into the target directory first.
   ```bash
   cd <project_path> && ~/.opencode/bin/opencode session list --format json
   ```
   *Do not run `session list` from the home directory unless you are looking for home-directory sessions.*
2. **Extract Session State**: To read the last output of a session, export it and parse the JSON:
   ```bash
   ~/.opencode/bin/opencode export <SESSION_ID> > /tmp/session.json
   python3 -c "import json; d=json.load(open('/tmp/session.json')); msgs=d.get('messages', []); print(json.dumps(msgs[-1]['parts'][-1] if msgs else 'No msgs', indent=2)[:1000])"
   ```
3. **Resume the Session**:
   ```bash
   cd <project_path> && ~/.opencode/bin/opencode run "<new_instruction>" --session <SESSION_ID>
   ```

### 3. Discovering Copilot CLI Sessions
If the user specifically asks about Copilot or code reviews:
1. Find recent Copilot workspaces:
   ```bash
   find ~/.copilot/session-state -name workspace.yaml -exec grep -H "cwd:" {} \;
   ```
2. Read the end of a session's event log:
   ```bash
   tail -n 20 ~/.copilot/session-state/<UUID>/events.jsonl
   ```

### 4. Extracting Artifacts for Telegram
If OpenCode or Copilot generates a report (e.g., `code-review-report.md`) and the user wants to see it:
1. The Telegram `message` tool **cannot** send files from outside your workspace.
2. You MUST copy the file to your workspace first:
   ```bash
   cp <path_to_artifact> /home/team_aidmi_ai/.openclaw/workspace/<filename>
   ```
3. Then send it using the `message` tool with `filePath: /home/team_aidmi_ai/.openclaw/workspace/<filename>`.

### 5. Interactive Session Selection Workflow (Telegram)
When the user triggers the skill generally (e.g., "trigger opencode"), follow this exact flow:
1. **Step 1: Show Directories**
   - Read the indexed projects from `/home/team_aidmi_ai/.openclaw/workspace/memory/opencode-projects.md` (or dynamically `ls` `~/code/work` and `~/code/personal`).
   - Send a formatted Telegram message grouping them by Work vs Personal.
   - Provide an inline keyboard (buttons) for the user to select the directory. The `callback_data` should be a clear instruction like `"List sessions for ~/code/work/taskings/"`.
2. **Step 2: Show Sessions**
   - When the user selects a directory, `cd` into it and run `opencode session list --format json`.
   - Parse the top 5-10 recent sessions.
   - Send a message listing these sessions and attach buttons for each (e.g., `"Resume session <ID>"`). 
   - Always include an option to "Start a New Session".
3. **Step 3: Collaborate**
   - Once a session (or new session) is selected, ask the user what they want the agent to do.
   - Execute the task using `opencode run` and report back the results.

## Rules
- NEVER attempt a massive multi-file refactor yourself. Always use `opencode run`.
- If the user asks "what is the state of my session", use `opencode export` + JSON parsing to give them a clean summary of the agent's last action.
