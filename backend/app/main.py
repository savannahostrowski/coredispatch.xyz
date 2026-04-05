import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.api import feed
from app.config import settings

app = FastAPI(
    title="Core Dispatch",
    description="This Week in Python",
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feed.router, prefix="/api/feed", tags=["feed"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# --- Static file serving (frontend) ---
STATIC_DIR = pathlib.Path(__file__).parent / "static"

if STATIC_DIR.exists():
    # Serve Astro static assets
    astro_static = STATIC_DIR / "_astro"
    if astro_static.exists():
        app.mount(
            "/_astro", StaticFiles(directory=str(astro_static)), name="astro_static"
        )

    # Catch-all: serve static files for known Astro routes only
    @app.api_route("/{path:path}", methods=["GET", "HEAD"])
    async def spa_fallback(path: str):
        file_path = (STATIC_DIR / path).resolve()
        if file_path.is_relative_to(STATIC_DIR) and file_path.is_file():
            return FileResponse(file_path)
        # Try path/index.html for Astro static routes
        index_path = (STATIC_DIR / path / "index.html").resolve()
        if index_path.is_relative_to(STATIC_DIR) and index_path.is_file():
            return FileResponse(index_path)
        not_found = STATIC_DIR / "404.html"
        if not_found.is_file():
            return FileResponse(not_found, status_code=404)
        return Response(status_code=404, content="Not found")
