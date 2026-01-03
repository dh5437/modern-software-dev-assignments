# Action Item Extractor

A FastAPI-based web application that extracts actionable items from free-form text notes. The application supports both heuristic-based and LLM-powered extraction methods, allowing users to convert unstructured meeting notes, task lists, and other text into organized action items.

## Overview

This application provides a RESTful API and web interface for:

- **Extracting action items** from unstructured text using pattern-based heuristics
- **LLM-powered extraction** using Ollama for more intelligent action item identification
- **Storing notes and action items** in a SQLite database
- **Managing action items** with completion tracking

The application is built with modern Python practices, including type safety with Pydantic, comprehensive error handling, and well-defined API contracts.

## Technology Stack

- **Framework**: FastAPI 0.111.0+
- **Database**: SQLite with custom database layer
- **Language**: Python 3.10+
- **LLM Integration**: Ollama (for LLM-powered extraction)
- **Validation**: Pydantic 2.0+
- **Testing**: pytest 7.0+
- **Package Management**: Poetry

## Project Structure

```
week2/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and lifecycle management
│   ├── config.py            # Application configuration and settings
│   ├── db.py                # Database layer with error handling
│   ├── exceptions.py        # Custom exception classes
│   ├── schemas.py           # Pydantic models for API contracts
│   ├── routers/
│   │   ├── action_items.py  # Action items API endpoints
│   │   └── notes.py         # Notes API endpoints
│   └── services/
│       └── extract.py       # Action item extraction logic
├── data/
│   └── app.db              # SQLite database (auto-created)
├── frontend/
│   └── index.html          # Web interface
├── tests/
│   └── test_extract.py     # Unit tests
└── README.md               # This file
```

## Setup and Installation

### Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- Ollama (optional, for LLM-powered extraction)

### Installation Steps

1. **Install dependencies using Poetry:**

   ```bash
   poetry install
   ```

2. **Set up Ollama (optional, for LLM extraction):**

   ```bash
   # Install Ollama from https://ollama.com
   # Pull the required model
   ollama pull llama3.1:8b
   ```

3. **Configure environment variables (optional):**
   Create a `.env` file in the project root:
   ```env
   OLLAMA_MODEL=llama3.1:8b
   OLLAMA_BASE_URL=http://localhost:11434
   DEBUG=false
   ```

## Running the Application

### Start the Development Server

From the project root directory:

```bash
poetry run uvicorn week2.app.main:app --reload
```

The application will be available at:

- **Web Interface**: http://127.0.0.1:8000/
- **API Documentation**: http://127.0.0.1:8000/docs
- **Alternative API Docs**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

### Database Initialization

The database is automatically initialized on application startup. The SQLite database file will be created in `week2/data/app.db` if it doesn't exist.

## API Endpoints

### Health Check

- **GET** `/health`
  - Returns application health status and version
  - Response: `{"status": "healthy", "version": "1.0.0"}`

### Notes Endpoints

#### Create a Note

- **POST** `/notes`
  - Creates a new note
  - Request Body:
    ```json
    {
      "content": "Meeting notes: - Review code changes - Update documentation"
    }
    ```
  - Response: `NoteResponse` with `id`, `content`, and `created_at`

#### Get a Note

- **GET** `/notes/{note_id}`
  - Retrieves a specific note by ID
  - Response: `NoteResponse`

#### List All Notes

- **GET** `/notes`
  - Retrieves all notes
  - Response: Array of `NoteResponse`

### Action Items Endpoints

#### Extract Action Items

- **POST** `/action-items/extract`
  - Extracts action items from text using heuristic-based extraction
  - Request Body:
    ```json
    {
      "text": "Meeting notes:\n- [ ] Set up database\n* implement API endpoint",
      "save_note": false
    }
    ```
  - Response: `ExtractActionItemsResponse` with `note_id` (if saved) and `items` array

#### List Action Items

- **GET** `/action-items?note_id={note_id}`
  - Lists all action items, optionally filtered by note ID
  - Query Parameters:
    - `note_id` (optional): Filter action items by note ID
  - Response: Array of `ActionItemResponse`

#### Mark Action Item as Done

- **POST** `/action-items/{action_item_id}/done`
  - Updates the completion status of an action item
  - Request Body:
    ```json
    {
      "done": true
    }
    ```
  - Response: `MarkDoneResponse` with `id` and `done` status

## API Response Models

### NoteResponse

```json
{
  "id": 1,
  "content": "Meeting notes...",
  "created_at": "2024-01-01 12:00:00"
}
```

### ActionItemResponse

```json
{
  "id": 1,
  "note_id": 1,
  "text": "Set up database",
  "done": false,
  "created_at": "2024-01-01 12:00:00"
}
```

### ExtractActionItemsResponse

```json
{
  "note_id": null,
  "items": [
    {
      "id": 1,
      "note_id": null,
      "text": "Set up database",
      "done": false,
      "created_at": "2024-01-01 12:00:00"
    }
  ]
}
```

## Action Item Extraction

The application supports two extraction methods:

### 1. Heuristic-Based Extraction (`extract_action_items`)

Uses pattern matching to identify action items:

- Bullet points (`-`, `*`, numbered lists)
- Keyword prefixes (`todo:`, `action:`, `next:`)
- Checkbox markers (`[ ]`, `[todo]`)
- Imperative sentences (fallback)

### 2. LLM-Powered Extraction (`extract_action_items_llm`)

Uses Ollama with structured outputs to intelligently extract action items:

- Requires Ollama server running
- Uses Pydantic models for structured JSON output
- More flexible and context-aware extraction

## Running Tests

### Run All Tests

From the project root directory:

```bash
poetry run pytest week2/tests/ -v
```

### Run Specific Test File

```bash
poetry run pytest week2/tests/test_extract.py -v
```

### Run Tests with Coverage

```bash
poetry run pytest week2/tests/ --cov=week2.app --cov-report=html
```

### Test Structure

Tests are located in `week2/tests/` and include:

- Unit tests for action item extraction functions
- Tests for both heuristic and LLM-based extraction
- Edge cases (empty input, various formats, deduplication)

**Note**: LLM-based extraction tests require Ollama to be running with the configured model installed.

## Error Handling

The application implements comprehensive error handling:

- **400 Bad Request**: Validation errors or invalid input
- **404 Not Found**: Resource not found (e.g., note or action item)
- **422 Unprocessable Entity**: Request validation errors
- **500 Internal Server Error**: Database or unexpected errors

All errors return JSON responses with a `detail` field containing the error message.

## Configuration

Application settings can be configured via environment variables:

- `OLLAMA_MODEL`: Ollama model to use (default: `llama3.1:8b`)
- `OLLAMA_BASE_URL`: Ollama server URL (optional)
- `DEBUG`: Enable debug mode (default: `false`)

Settings are loaded from `.env` file or environment variables.

## Development

### Code Quality

The project uses:

- **Black** for code formatting
- **Ruff** for linting
- **Pydantic** for type validation
- **Type hints** throughout the codebase

### Project Features

- ✅ Type-safe API contracts with Pydantic
- ✅ Comprehensive error handling
- ✅ Database layer with transaction management
- ✅ Application lifecycle management (startup/shutdown)
- ✅ Structured logging
- ✅ Health check endpoint
- ✅ Interactive API documentation (Swagger UI)

## License

This project is part of a course assignment and is for educational purposes.
