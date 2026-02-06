from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import apply_seed_if_needed, engine
from .models import Base
from .routers import action_items as action_items_router
from .routers import notes as notes_router

app = FastAPI(title="Modern Software Dev Starter (Week 7)", version="0.1.0")

# Ensure data dir exists
Path("data").mkdir(parents=True, exist_ok=True)

# Mount static frontend if present (tests may run without frontend assets)
frontend_dir = Path("frontend")
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory="frontend"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compatibility with FastAPI lifespan events; keep on_event for simplicity here
@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    apply_seed_if_needed()


@app.get("/")
async def root() -> FileResponse:
    if not frontend_dir.exists():
        raise HTTPException(status_code=404, detail="Frontend not available")
    return FileResponse("frontend/index.html")


# Routers
app.include_router(notes_router.router)
app.include_router(action_items_router.router)

