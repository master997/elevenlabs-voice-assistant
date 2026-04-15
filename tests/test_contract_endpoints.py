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

