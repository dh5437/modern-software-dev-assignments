---
name: execute-tasks-and-writeup
description: Execute tasks listed in /docs/TASKS.md and document how the automation was used in writeup.md.
---

You are an automation agent responsible for executing structured project tasks and documenting the automation’s impact.

This skill is **repository-specific** and must follow all repository guidance files (especially AGENTS.md).

## Objective

1. Read and understand `/docs/TASKS.md`.
2. Execute each task listed there, one by one, in a careful and minimal manner.
3. Document how this automation was used to enhance the starter application by updating `writeup.md`.

## Constraints (Very Important)

- Follow all rules defined in AGENTS.md.
- Do not modify files outside the allowed scope.
- Do not invent tasks or reinterpret their intent.
- Execute tasks in the order they appear in `/docs/TASKS.md`.
- Keep code changes minimal and intentional.
- If a task is ambiguous, make a reasonable assumption and document it explicitly.

## Step-by-step Execution Plan

### Step 1 — Read and decompose tasks

- Open `/docs/TASKS.md`.
- Extract each task as an explicit, actionable item.
- If a task contains multiple sub-requirements, break it into sub-steps internally.
- Briefly summarize the task list before executing anything.

### Step 2 — Execute tasks

For each task:

- Identify the relevant files and components.
- Apply the required changes carefully.
- Verify that the change satisfies the task’s intent.
- Avoid unnecessary refactors or formatting changes.
- Ensure the application remains runnable after each task.

Tasks must be completed sequentially. Do not skip ahead.

### Step 3 — Update writeup.md

After completing all tasks:

- Open `writeup.md`.
- Locate the section titled:
  **“How you used the automation to enhance the starter application”**
- Update only this section.
- Describe:
  - That this skill was used to read and execute `/docs/TASKS.md`
  - How the automation structured the work (task decomposition, sequential execution)
  - How it reduced manual effort or errors
  - What concrete improvements were made to the starter application as a result
- Write in clear, concise, reflective prose.
- Do not modify other sections of `writeup.md`.

## Output Expectations

When this skill completes:

- All tasks in `/docs/TASKS.md` are implemented.
- `writeup.md` accurately reflects how this automation was used.
- The repository remains clean and consistent with its original structure.

## Quality Bar

- Prefer correctness and traceability over speed.
- Automation usage should be clearly visible in both the code changes and the writeup.
- A reviewer should be able to understand **what was automated, why it mattered, and what changed**.
