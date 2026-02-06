# Week 6 Write-up

Tip: To preview this markdown file

- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do.

## Brief findings overview

> Fixed SQL injection risk in notes unsafe search by binding the LIKE pattern parameter; `action_items` uses ORM filters (no dynamic SQL).

## Fix #1

a. File and line(s)

> `week6/backend/app/routers/notes.py:69-82`

b. Rule/category Semgrep flagged

> SQL Injection with FastAPI

c. Brief risk description

> User input was interpolated into raw SQL via f-string, allowing SQL injection through the `q` parameter.

d. Your change (short code diff or explanation, AI coding tool usage)

> Replaced string interpolation with a bound parameter: `WHERE title LIKE :pattern OR content LIKE :pattern` and passed `{"pattern": f"%{q}%"}` to `db.execute`.

e. Why this mitigates the issue

> Parameter binding keeps user input out of SQL syntax, preventing injection while preserving search behavior.

## Fix #2

a. File and line(s)

> `week6/backend/app/routers/notes.py:103-111`

b. Rule/category Semgrep flagged

> Code Injection with FastAPI

c. Brief risk description

> `eval()` executed user-supplied input, allowing arbitrary code execution.

d. Your change (short code diff or explanation, AI coding tool usage)

> Replaced `eval()` with `ast.literal_eval()` and return 400 for invalid expressions.

e. Why this mitigates the issue

> `literal_eval` only parses Python literals, preventing execution of arbitrary code.

## Fix #3

a. File and line(s)

> `week6/backend/app/routers/notes.py:69-75`

b. Rule/category Semgrep flagged

> SQL Injection with SQLAlchemy

c. Brief risk description

> Raw SQL was used for search, which Semgrep flags as potential injection risk.

d. Your change (short code diff or explanation, AI coding tool usage)

> Replaced raw SQL `text()` query with SQLAlchemy ORM query and filters.

e. Why this mitigates the issue

> ORM constructs parameterized queries, avoiding dynamic SQL string construction.
