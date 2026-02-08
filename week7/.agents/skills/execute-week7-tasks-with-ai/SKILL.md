---
name: execute-week7-tasks-with-ai
description: Implement tasks from week7/docs/TASKS.md using an AI coding tool, creating a separate branch and pull request for each task, documenting testing, tradeoffs, and AI-assisted review results in writeup.md.
---

# Skill: Execute Week 7 Tasks with AI Assistance

You are an automation agent operating inside a specific repository.  
This skill is **repository-specific** and must follow all repository guidance files (especially `AGENTS.md`).

---

## Objective

1. Read and understand the tasks defined in `week7/docs/TASKS.md`.
2. For **each task**, use an AI coding tool with a **single, one-shot prompt** to implement the required changes.
3. Create a **separate Git branch and Pull Request** for each task.
4. Manually review and refine the AI-generated changes.
5. Document the results of each task and PR in `writeup.md`.

---

## Hard Constraints (Very Important)

- Follow all rules defined in `AGENTS.md`.
- Do not modify files outside the scope required by the task.
- Execute tasks **one by one**, in the order they appear in `week7/docs/TASKS.md`.
- Each task must:
  - use a **single AI prompt** for the initial implementation
  - be implemented on a **separate branch**
  - have its **own Pull Request**
- Avoid unnecessary refactors or formatting-only changes.
- All changes must be manually reviewed and corrected if needed.
- The application must remain runnable after each task.

---

## Step 1 — Read and Decompose Tasks

1. Open `week7/docs/TASKS.md`.
2. Extract each task as an explicit, actionable unit of work.
3. If a task contains multiple requirements, decompose them internally.
4. Briefly summarize the full task list before starting implementation.

---

## Step 2 — Implement Each Task Using AI (Sequentially)

For **each task**, perform the following steps in order.

### 2.1 Create a Branch

- Create a new branch scoped to the task:

  ```bash
  git checkout -b task-<short-description>
  ```

### 2.2 Generate Code Using a One-Shot AI Prompt

- Use an AI coding tool (e.g. Cursor, Copilot, Claude).
- Provide a single, complete prompt describing the task.
- Do not iteratively refine the prompt.
- Apply the AI-generated changes.

### 2.3 Manual Review and Fixes

- Review all changes line by line.
- Fix:
  - incorrect logic
  - missing edge cases
  - style or clarity issues
- Add explanatory commit messages where helpful.
- Optionally pair with a classmate to review changes instead of self-review.

### 2.4 Testing

- Run relevant tests or commands.
- Add or update tests if appropriate.
- Record:
  - commands run
  - results (pass/fail)

### 2.5 Open a Pull Request

For each task, open a Pull Request that includes:

- Problem description and implementation approach.
- Summary of testing performed, including commands and results.
- Notable tradeoffs, limitations, or follow-up work.

### 2.6 AI-Assisted Code Review

- Use Graphite Diamond to generate an AI-assisted code review on the PR.
- Review the feedback and address issues where appropriate.

## Step 3 — Update writeup.md

After completing each Pull Request:

1. Open writeup.md.
2. Document the task and PR results, including:
   - the task objective
   - how AI was used (one-shot prompt)
   - what changes were made
   - testing performed
   - notable tradeoffs or limitations
   - insights from the Graphite Diamond review

3. Keep the writing clear, concise, and reflective.

## Output Expectations

When this skill completes:

- All tasks in week7/docs/TASKS.md are implemented.
- Each task has:
  - its own branch
  - its own Pull Request
  - manual review and testing
  - an AI-assisted review via Graphite Diamond
- writeup.md accurately documents the process and outcomes.
- The repository remains clean and consistent with its original structure.
