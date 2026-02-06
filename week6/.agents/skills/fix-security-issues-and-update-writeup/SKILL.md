---
name: fix-security-issues-and-update-writeup
description: When the user provides security vulnerability findings, execute code-level fixes in the repository and update writeup.md to document what was fixed and how the automation was used.
---

# Skill: Fix Provided Semgrep Security Issues and Update Writeup

You are an automation agent operating inside a specific repository.  
This skill is **repository-specific** and must strictly follow all repository guidance files, especially `AGENTS.md`.

---

## Objective

1. Review **Semgrep security findings provided by the user, one by one**.
2. Determine an appropriate and minimal fix for each finding.
3. Apply the fixes while preserving existing behavior.
4. Update `writeup.md` to document what was fixed and how the automation was used.

---

## Hard Constraints (Very Important)

- Read and follow **all rules in `AGENTS.md`** before making any changes.
- Do **not** modify files outside the allowed scope.
- Do **not** invent tasks beyond the Semgrep issues explicitly provided by the user.
- Process Semgrep issues **strictly in the order they are given**.
- Keep all code changes **minimal (small diffs)** and directly related to the security issue.
- Avoid refactors, formatting-only changes, or renaming unless required for security.
- The application must remain runnable after each fix.
- If a finding is ambiguous:
  - Make one reasonable assumption.
  - Clearly document that assumption in `writeup.md`.

---

## Step 1 — Review Semgrep Finding

For each Semgrep issue provided by the user:

1. Read the Semgrep rule name and message carefully.
2. Inspect the reported file, line range, and code snippet.
3. Identify:
   - the security risk being reported
   - whether it is a real vulnerability or a false positive

Do not apply any fixes until the issue is fully understood.

---

## Step 2 — Apply Security Fix (Sequentially)

Fix each Semgrep issue **in the order provided by the user**.

For **each issue**, perform the following:

- (a) Briefly explain the root cause (1–2 sentences).
- (b) Decide on a minimal, safe remediation strategy.
- (c) Apply the code change.
- (d) Perform a lightweight verification (reason about execution path, tests, or runtime safety).

### Semgrep Issue Template

- File / line:
- Semgrep rule / message:
- Problematic code snippet:

---

### Important Notes

- Do **not** silence findings using comments such as `# nosemgrep` unless the issue is a verified false positive.
- If the issue is a false positive:
  - Clearly explain why it is safe.
  - Prefer a small code-level clarification over suppression when possible.
- Security fixes must preserve existing functionality and interfaces.

---

## Step 3 — Update `writeup.md` (Specific Section Only)

After all provided Semgrep issues have been addressed:

1. Open `writeup.md`.
2. Locate the section titled:

   **“How you used the automation to enhance the starter application”**

3. Update **only this section**. Do not modify any other content.

Include the following:

- That this automation was used to analyze and fix Semgrep-reported security issues.
- How the automation structured the work:
  - issue-by-issue analysis
  - sequential execution
  - minimal-diff enforcement
- A concise summary of each security fix:
  - what was changed
  - why it improves security
- Any assumptions made due to ambiguity.

Write clearly, concisely, and reflectively.

---

## Output Expectations

When this skill completes:

- All user-provided Semgrep security issues are addressed.
- Code changes are minimal, targeted, and safe.
- `writeup.md` accurately reflects what was fixed and how.
- The repository remains clean and consistent with its original structure.

At the end, provide:

- A short list of modified files.
- A brief confirmation that minimal-diff principles were followed.
