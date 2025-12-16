"""FastAPI entrypoint for topo editor.

Exposes an API at /api/v1/topox and serves static assets from the sibling
public/ directory.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Topo Editor API")


def mount_static(app: FastAPI) -> None:
    """Mount the static files directory if it exists."""

    public_dir = Path(__file__).parent / "public"
    if not public_dir.exists():
        logger.warning("Public directory %s not found; static files will not be served.", public_dir)
        return

    app.mount("/", StaticFiles(directory=str(public_dir), html=True), name="public")
    logger.info("Serving static files from %s", public_dir)


@app.get("/api/v1/topox")
async def get_topox() -> JSONResponse:
    logger.info("GET /api/v1/topox received")
    return JSONResponse(content={"status": "ok"}, status_code=200)


@app.post("/api/v1/topox")
async def post_topox(request: Request) -> JSONResponse:
    payload: Dict[str, Any] = await request.json()
    logger.info("POST /api/v1/topox payload: %s", json.dumps(payload, ensure_ascii=False))
    return JSONResponse(content={"received": True}, status_code=200)


@app.get("/healthz")
async def healthz() -> PlainTextResponse:
    logger.info("GET /healthz")
    return PlainTextResponse(content="OK", status_code=200)


mount_static(app)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=False)
