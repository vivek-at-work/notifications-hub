from __future__ import annotations

from fastapi import APIRouter

from app.version import get_version

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/version")
async def app_version() -> dict[str, str]:
    return {"name": "api", "version": get_version()}
