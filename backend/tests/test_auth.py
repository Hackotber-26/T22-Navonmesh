import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_google_auth_and_admin_role():
    """Verify Google sign-in creates users, issues JWT, and detects admin role from ADMIN_EMAILS."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Normal user login
        res1 = await client.post(
            "/api/auth/google",
            json={"id_token": "dev-test-token:sub-101:user@example.com:Ramesh Kumar"}
        )
        assert res1.status_code == 200
        data1 = res1.json()
        assert "access_token" in data1
        assert data1["user"]["role"] == "user"
        user_token = data1["access_token"]

        # 2. Admin user login (matching ADMIN_EMAILS default admin@scamshield.org)
        res2 = await client.post(
            "/api/auth/google",
            json={"id_token": "dev-test-token:sub-admin-1:admin@scamshield.org:Admin Team"}
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["user"]["role"] == "admin"
        admin_token = data2["access_token"]

        # 3. Verify GET /api/users/me with JWT
        me_res = await client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_guest_mode_and_authenticated_scan_history():
    """Verify guests can scan without login, and authenticated users can view their history (metadata only)."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Guest scan (No auth header)
        guest_res = await client.post(
            "/api/analyze",
            json={
                "input_type": "text",
                "content": "Check this out",
                "language": "en"
            }
        )
        assert guest_res.status_code == 200

        # 2. Sign in user
        login_res = await client.post(
            "/api/auth/google",
            json={"id_token": "dev-test-token:sub-history-test:history_user@example.com:Sunita Devi"}
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 3. Authenticated scan
        auth_scan = await client.post(
            "/api/analyze",
            json={
                "input_type": "text",
                "content": "Aapka account block hoga, update KYC at sbi-kyc-update.xyz",
                "language": "hi"
            },
            headers=auth_headers
        )
        assert auth_scan.status_code == 200
        inc_id = auth_scan.json()["incident_id"]

        # 4. Fetch scan history
        hist_res = await client.get("/api/users/me/history", headers=auth_headers)
        assert hist_res.status_code == 200
        history = hist_res.json()
        assert len(history) >= 1
        assert history[0]["id"] == inc_id
        assert history[0]["category"] == "FAKE_KYC"
        # Confirm no raw text exists in returned history
        assert "content" not in history[0]

        # 5. Test Right to Erasure (DPDP Act)
        del_res = await client.delete("/api/users/me/history", headers=auth_headers)
        assert del_res.status_code == 200

        # Verify history is now empty
        empty_hist = await client.get("/api/users/me/history", headers=auth_headers)
        assert empty_hist.status_code == 200
        assert len(empty_hist.json()) == 0
