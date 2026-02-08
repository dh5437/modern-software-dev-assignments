# Week 7 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Jake Kim** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## Task 1: Add more endpoints and validations
a. Links to relevant commits/issues
> Commit: d85e0e8 (task-add-endpoints-validation)

b. PR Description
> Added GET/DELETE endpoints for action items and notes, added input validation (lengths, empty payloads), and stricter sort/pagination validation. Updated tests for new endpoints and validation errors. No PR created per instruction; changes are on branch `task-add-endpoints-validation`.

c. Graphite Diamond generated code review
> Not run (no PR created per instruction).

## Task 2: Extend extraction logic
a. Links to relevant commits/issues
> Commit: c454a71 (task-extend-extraction)

b. PR Description
> Expanded action item extraction to support checkboxes, more prefixes (TODO/ACTION/FIXME/NEXT), and imperative phrasing, with updated tests. No PR created per instruction; changes are on branch `task-extend-extraction`.

c. Graphite Diamond generated code review
> Not run (no PR created per instruction).

## Task 3: Try adding a new model and relationships
a. Links to relevant commits/issues
> Commit: 0283772 (task-add-model-relationships)

b. PR Description
> Added a `Project` model with relationships to notes and action items, plus a projects API. Notes and action items can now be linked to projects and filtered by `project_id`, with tests for linking and validation. No PR created per instruction; changes are on branch `task-add-model-relationships`.

c. Graphite Diamond generated code review
> Not run (no PR created per instruction).

## Task 4: Improve tests for pagination and sorting
a. Links to relevant commits/issues
> Commit: c10d861 (task-test-pagination-sorting)

b. PR Description
> Added deterministic pagination and sorting tests for notes and action items using title/description ordering. No PR created per instruction; changes are on branch `task-test-pagination-sorting`.

c. Graphite Diamond generated code review
> Not run (no PR created per instruction).

## Brief Reflection 
a. The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
> TODO 

b. A comparison of **your** comments vs. **Graphite’s** AI-generated comments for each PR.
> TODO

c. When the AI reviews were better/worse than yours (cite specific examples)
> TODO

d. Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
>TODO 

