from datetime import date

from api.data.companies import list_companies


def test_health_contract(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body == {"status": "ok", "version": "0.2.0"}


def test_calendar_today_contract(client):
    r = client.get("/calendar/today")
    assert r.status_code == 200
    body = r.json()

    assert body["date"] == str(date.today())
    assert isinstance(body["meetings"], list)
    assert len(body["meetings"]) >= 1

    first = body["meetings"][0]
    assert {"time", "company", "contact", "title", "type"} <= set(first.keys())
    assert isinstance(first["company"], str)


def test_account_company_200_contract(client):
    r = client.get("/account/notion")
    assert r.status_code == 200
    body = r.json()

    assert body["company"] == "Notion"
    assert isinstance(body["arr"], int)
    assert isinstance(body["arr_formatted"], str)
    assert isinstance(body["outreach_summary"], dict)
    assert isinstance(body["recent_slack_activity"], list)


def test_account_company_404_contract(client):
    r = client.get("/account/does-not-exist")
    assert r.status_code == 404
    body = r.json()

    assert "detail" in body
    detail = body["detail"]
    assert isinstance(detail, dict)
    assert "error" in detail
    assert "valid_companies" in detail
    assert isinstance(detail["valid_companies"], list)


def test_patterns_today_contract(client):
    r = client.get("/patterns/today")
    assert r.status_code == 200
    body = r.json()

    assert body["date"] == "today"
    assert isinstance(body["meetings_analyzed"], list)
    assert {"notion", "deutsche telekom", "linear"}.issubset(set(body["meetings_analyzed"]))
    assert isinstance(body["competitive_patterns"], list)
    assert isinstance(body["objection_patterns"], list)
    assert isinstance(body["recommended_actions"], list)
    assert isinstance(body["summary"], str)


def test_followup_draft_200_contract(client):
    payload = {"company": "notion", "action_type": "next_steps_summary"}
    r = client.post("/followup/draft", json=payload)
    assert r.status_code == 200
    body = r.json()

    assert body["company"] == "Notion"
    assert body["action_type"] == "next_steps_summary"
    assert body["destination"] == "Slack DM"
    assert isinstance(body["draft"], str)
    assert len(body["draft"]) > 0


def test_followup_draft_invalid_action_400_contract(client):
    payload = {"company": "notion", "action_type": "totally_invalid"}
    r = client.post("/followup/draft", json=payload)
    assert r.status_code == 400
    body = r.json()

    assert "detail" in body
    detail = body["detail"]
    assert detail["error"].startswith("Unknown action_type")
    assert set(detail["valid_action_types"]) == {
        "competitive_positioning_note",
        "next_steps_summary",
        "intro_request",
    }


def test_followup_draft_unknown_company_404_contract(client):
    payload = {"company": "does-not-exist", "action_type": "next_steps_summary"}
    r = client.post("/followup/draft", json=payload)
    assert r.status_code == 404
    body = r.json()

    assert "detail" in body
    detail = body["detail"]
    assert "error" in detail
    assert detail["valid_companies"] == list_companies()


def test_slack_post_next_steps_200_contract(client, monkeypatch):
    import api.routers.slack as slack_router

    monkeypatch.setenv("DEMO_TOKEN", "test-token")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/test")

    def fake_post(url, json, timeout):  # noqa: ANN001
        class Resp:
            status_code = 200

        assert url == "https://hooks.slack.com/services/test"
        assert "text" in json
        assert timeout == 5.0
        return Resp()

    monkeypatch.setattr(slack_router.httpx, "post", fake_post)

    payload = {"company": "notion", "draft_text": "hello <!channel>"}
    r = client.post(
        "/slack/post-next-steps",
        json=payload,
        headers={"X-DEMO-TOKEN": "test-token"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["posted"] == {"ok": True}
    assert body["fallback"]["draft_text"] == "hello <!channel>"


def test_slack_post_next_steps_missing_token_403_contract(client, monkeypatch):
    monkeypatch.setenv("DEMO_TOKEN", "test-token")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/test")
    r = client.post("/slack/post-next-steps", json={"company": "notion", "draft_text": "hi"})
    assert r.status_code == 403
    body = r.json()
    assert body["detail"]["ok"] is False


def test_slack_post_next_steps_wrong_token_403_contract(client, monkeypatch):
    monkeypatch.setenv("DEMO_TOKEN", "test-token")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/test")
    r = client.post(
        "/slack/post-next-steps",
        json={"company": "notion", "draft_text": "hi"},
        headers={"X-DEMO-TOKEN": "wrong"},
    )
    assert r.status_code == 403
    body = r.json()
    assert body["detail"]["ok"] is False


def test_slack_post_next_steps_missing_webhook_500_contract(client, monkeypatch):
    import api.routers.slack as slack_router

    monkeypatch.setenv("DEMO_TOKEN", "test-token")
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    monkeypatch.setattr(slack_router.httpx, "post", lambda *args, **kwargs: None)

    r = client.post(
        "/slack/post-next-steps",
        json={"company": "notion", "draft_text": "hi"},
        headers={"X-DEMO-TOKEN": "test-token"},
    )
    assert r.status_code == 500
    body = r.json()
    assert body["detail"]["ok"] is False


def test_slack_post_next_steps_success_contract(client, monkeypatch):
    monkeypatch.setenv("DEMO_TOKEN", "demo123")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/T000/B000/XXX")

    import api.routers.slack as slack_router

    calls = {}

    class DummyResp:
        status_code = 200

    def fake_post(url, json, timeout):
        calls["url"] = url
        calls["json"] = json
        calls["timeout"] = timeout
        return DummyResp()

    monkeypatch.setattr(slack_router.httpx, "post", fake_post)

    payload = {"company": "Notion", "draft_text": "Hello <!channel> world"}
    r = client.post("/slack/post-next-steps", json=payload, headers={"X-DEMO-TOKEN": "demo123"})
    assert r.status_code == 200
    body = r.json()

    assert body == {"ok": True, "posted": {"ok": True}, "fallback": {"draft_text": payload["draft_text"]}}
    assert calls["url"] == "https://hooks.slack.com/services/T000/B000/XXX"
    assert calls["timeout"] == 5.0
    assert "[mention removed]" in calls["json"]["text"]
    assert "<!channel>" not in calls["json"]["text"]


def test_slack_post_next_steps_missing_token_403_contract(client, monkeypatch):
    monkeypatch.setenv("DEMO_TOKEN", "demo123")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/T000/B000/XXX")

    payload = {"company": "Notion", "draft_text": "Draft"}
    r = client.post("/slack/post-next-steps", json=payload)
    assert r.status_code == 403
    detail = r.json()["detail"]
    assert detail["ok"] is False
    assert detail["fallback"]["draft_text"] == "Draft"


def test_slack_post_next_steps_wrong_token_403_contract(client, monkeypatch):
    monkeypatch.setenv("DEMO_TOKEN", "demo123")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/T000/B000/XXX")

    payload = {"company": "Notion", "draft_text": "Draft"}
    r = client.post("/slack/post-next-steps", json=payload, headers={"X-DEMO-TOKEN": "nope"})
    assert r.status_code == 403
    detail = r.json()["detail"]
    assert detail["ok"] is False
    assert detail["fallback"]["draft_text"] == "Draft"


def test_slack_post_next_steps_missing_webhook_url_500_contract(client, monkeypatch):
    monkeypatch.setenv("DEMO_TOKEN", "demo123")
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)

    payload = {"company": "Notion", "draft_text": "Draft"}
    r = client.post("/slack/post-next-steps", json=payload, headers={"X-DEMO-TOKEN": "demo123"})
    assert r.status_code == 500
    detail = r.json()["detail"]
    assert detail["ok"] is False
    assert detail["fallback"]["draft_text"] == "Draft"

