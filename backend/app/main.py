import pathlib
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from app.api import feed
from app.config import settings

app = FastAPI(
    title="Core Dispatch",
    description="This Week in Python",
    docs_url=None,
    redoc_url=None,
)

set_meter_provider(
    MeterProvider(metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())])
)
FastAPIInstrumentor.instrument_app(app)

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

    def static_endpoint(
        file_path: pathlib.Path,
    ) -> Callable[[], Coroutine[Any, Any, FileResponse]]:
        async def serve_static_file() -> FileResponse:
            return FileResponse(file_path)

        return serve_static_file

    # Register the finite Astro build output as exact routes. OpenTelemetry
    # records the matched route template, so a catch-all here would collapse
    # every page into /{path:path} in HTTP metrics.
    for file_path in STATIC_DIR.rglob("*"):
        if not file_path.is_file() or "_astro" in file_path.parts:
            continue

        relative_path = file_path.relative_to(STATIC_DIR)
        if relative_path.name == "index.html":
            parent = relative_path.parent.as_posix()
            route_path = "/" if parent == "." else f"/{parent}"
        else:
            route_path = f"/{relative_path.as_posix()}"

        app.add_api_route(
            route_path,
            static_endpoint(file_path),
            methods=["GET", "HEAD"],
            include_in_schema=False,
            name=f"static:{relative_path.as_posix()}",
        )

    not_found = STATIC_DIR / "404.html"
    if not_found.is_file():

        @app.exception_handler(404)
        async def static_not_found(*_args: Any) -> FileResponse:
            return FileResponse(not_found, status_code=404)
