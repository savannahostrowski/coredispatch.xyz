import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import feed, subscribers
from app.config import settings

app = FastAPI(title="Core Dispatch", description="This Week in Python")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(subscribers.router, prefix="/api/subscribers", tags=["subscribers"])
app.include_router(feed.router, prefix="/api/feed", tags=["feed"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# --- Static file serving (frontend) ---
STATIC_DIR = pathlib.Path(__file__).parent / "static"

if STATIC_DIR.exists():
    # Serve Next.js static assets
    next_static = STATIC_DIR / "_next"
    if next_static.exists():
        app.mount("/_next", StaticFiles(directory=str(next_static)), name="next_static")

    # SPA catch-all: serve static files, fall back to index.html
    @app.get("/{path:path}")
    async def spa_fallback(path: str):
        file_path = (STATIC_DIR / path).resolve()
        if file_path.is_relative_to(STATIC_DIR) and file_path.is_file():
            return FileResponse(file_path)
        # Try path/index.html for Next.js static routes (e.g. /issues -> /issues/index.html)
        index_path = (STATIC_DIR / path / "index.html").resolve()
        if index_path.is_relative_to(STATIC_DIR) and index_path.is_file():
            return FileResponse(index_path)
        return FileResponse(STATIC_DIR / "index.html")
