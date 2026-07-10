"""Smoke test for the health endpoint (no external deps required)."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.routes import health
from fastapi import FastAPI


@pytest.fixture
def app() -> FastAPI:
    api = FastAPI()
    api.include_router(health.router, prefix="/api")
    return api


@pytest.mark.asyncio
async def test_health_ok(app: FastAPI):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
