# Week 4 Starter App

## Project Overview
This is a small FastAPI + SQLite starter application with a static HTML/JS frontend. It supports creating and searching notes, managing action items, and extracting action items from note content.

## Features
- Notes: create, list, search (case-insensitive), update, delete
- Action items: create, list, complete
- Extraction: parse note content for action items and tags
- Static frontend served by the backend

## Project Structure
- `backend/`: FastAPI app, routes, schemas, models, services
- `frontend/`: static HTML/CSS/JS UI
- `data/`: SQLite DB file and seed SQL
- `docs/`: API summary (`API.md`)

## Setup / Installation
This project is part of a larger repository; Python dependencies are defined at the repo root. Ensure you have a Python environment with FastAPI, SQLAlchemy, and Uvicorn installed.

## Running the Application
From the `week4/` directory:

```bash
make run
```

This starts the API and serves the frontend at `http://127.0.0.1:8000/`.

## Configuration
- `DATABASE_PATH`: override the SQLite DB path (default: `./data/app.db`).

## API Overview (High-Level)
- Notes: `GET /notes/`, `POST /notes/`, `GET /notes/search/`, `GET /notes/{id}`, `PUT /notes/{id}`, `DELETE /notes/{id}`, `POST /notes/{id}/extract`
- Action items: `GET /action-items/`, `POST /action-items/`, `PUT /action-items/{id}/complete`

For full details, see `docs/API.md`.

## Tests
From the `week4/` directory:

```bash
make test
```
