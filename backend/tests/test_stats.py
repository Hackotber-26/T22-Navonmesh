import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_stats_pipeline_with_incidents():
    """Verify that scanning incidents updates stats accurately and keeps low-risk separate."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Scan a high-risk fraud message
        res1 = await client.post(
            "/api/analyze",
            json={
                "input_type": "text",
                "content": "Your SBI account is suspended. Update KYC at sbi-kyc-update.xyz immediately",
                "language": "hi",
                "user_action_state": "clicked"
            }
        )
        assert res1.status_code == 200
        inc_id1 = res1.json()["incident_id"]

        # 2. Scan a legitimate safe bank transaction alert
        res2 = await client.post(
            "/api/analyze",
            json={
                "input_type": "text",
                "content": "Dear Customer, your A/C XX1290 has been credited with Rs 500.00. SBI",
                "language": "en",
                "user_action_state": "not_acted"
            }
        )
        assert res2.status_code == 200

        # 3. Test GET /api/stats/summary
        sum_res = await client.get("/api/stats/summary")
        assert sum_res.status_code == 200
        summary = sum_res.json()

        assert "total_scans" in summary
        assert "total_flagged" in summary
        assert "by_risk_level" in summary
        assert summary["total_scans"] >= 2
        assert summary["total_flagged"] >= 1
        assert summary["by_risk_level"]["low"] >= 1
        # Crucial check: low-risk scans must NOT be counted in total_flagged
        assert summary["total_flagged"] < summary["total_scans"]

        # 4. Test GET /api/stats/categories
        cat_res = await client.get("/api/stats/categories")
        assert cat_res.status_code == 200
        categories = cat_res.json()
        assert isinstance(categories, list)
        assert any(c["category"] == "FAKE_KYC" for c in categories)

        # 5. Test GET /api/stats/timeline?days=7
        time_res = await client.get("/api/stats/timeline?days=7")
        assert time_res.status_code == 200
        timeline = time_res.json()
        assert len(timeline) == 7
        assert "date" in timeline[0]
        assert "flagged" in timeline[0]
        assert "safe" in timeline[0]

        # 6. Test GET /api/stats/by-language
        lang_res = await client.get("/api/stats/by-language")
        assert lang_res.status_code == 200
        langs = lang_res.json()
        assert any(l["language"] in ["hi", "en"] for l in langs)

        # 7. Test GET /api/stats/actions
        act_res = await client.get("/api/stats/actions")
        assert act_res.status_code == 200
        actions = act_res.json()
        assert isinstance(actions, list)
