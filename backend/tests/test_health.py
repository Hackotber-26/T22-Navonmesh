import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "ScamShield India API"
        assert data["status"] == "online"


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"
        assert "versions" in data
        assert data["versions"]["rules_version"] == "v1.0.0"


@pytest.mark.asyncio
async def test_payload_limit_middleware():
    transport = ASGITransport(app=app)
    # Huge payload above MAX_INPUT_CHARS * 4
    huge_body = "A" * 25000
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/health",
            content=huge_body,
            headers={"Content-Length": str(len(huge_body))}
        )
        assert response.status_code == 413
