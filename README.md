# SDR Morning Briefing, ElevenLabs Voice Agent Demo

A voice-first SDR “morning standup” assistant.

The point of the demo is simple: give a rep the right 2 to 3 facts before each meeting, hands-free, with one follow-up action (draft a Slack DM) when a cross-call pattern shows up.

## Live demo

- **Landing page (Vercel)**: `https://elevenlabs-voice-assistant.vercel.app/`
  - `/try-agent`: `https://elevenlabs-voice-assistant.vercel.app/try-agent`
- **Backend (FastAPI)**: `https://sdr-briefing-api.fly.dev`
- **Voice agent (ElevenLabs ConvAI)**: `agent_0701kp8zca3sfyb986q071k7xv25`

## What it does

- Reads today’s meetings (mock calendar)
- Briefs each account conversationally (not field-by-field)
- Pulls context from mocked “systems”: Salesforce, Gong, Slack, Outreach, internal wiki
- Detects cross-call patterns (example: competitor “Gemini” appears in multiple calls)
- Drafts a Slack DM (copy-only UI on the landing page)

## Mock data and demo “scripts”

This repo is intentionally self-contained. All “CRM/call/Slack/Outreach/wiki” info is mocked in code so the demo is deterministic.

- **Company data (source of truth)**: `api/data/companies.py`
  - Each company record unifies:
    - `sf_profile` (Salesforce-like account object)
    - `gong_last_call` (call summary, objections, next steps, competitive mentions)
    - `slack_mentions` (teammate intel)
    - `outreach` (sequence engagement)
    - `wiki_playbook` (talk track, competitive responses)
  - **Today’s meeting set** is driven by `TODAY_MEETINGS` in the same file.
- **Cross-call patterns**: `api/data/patterns.py` (computed from `TODAY_MEETINGS`)
- **Mock calendar response**: `api/routers/calendar.py`

If you want the demo to “tell a different story”, edit:

- `api/data/companies.py` (change objections, next steps, competitor mentions, Slack quotes)
- `api/routers/calendar.py` (change the day’s meeting list + times)

### Example mock responses (live backend)

`GET /calendar/today`:

```json
{
  "date": "2026-04-16",
  "meetings": [
    { "time": "10:00", "company": "Notion", "contact": "Maya Chen", "title": "Head of Engineering", "type": "discovery" },
    { "time": "13:00", "company": "Deutsche Telekom", "contact": "Klaus Weber", "title": "VP of Digital Products", "type": "follow-up" },
    { "time": "15:30", "company": "Linear", "contact": "Karri Saarinen", "title": "CEO", "type": "demo" }
  ]
}
```

`GET /account/Notion` (shape):

```json
{
  "company": "Notion",
  "arr": 28000,
  "arr_formatted": "$28,000",
  "plan": "Business",
  "stage": "Discovery",
  "outreach_summary": { "sequence": "SMB Inbound — Technical Buyer", "last_touch": "2026-04-10" },
  "recent_slack_activity": [{ "from": "Sarah Kim", "channel": "#deals-smb", "text": "FYI — I saw Notion is also talking to Gemini's API team...", "ts": "2026-04-14T18:05:00Z" }]
}
```

`GET /patterns/today` (shape):

```json
{
  "date": "today",
  "meetings_analyzed": ["notion", "deutsche telekom", "linear"],
  "competitive_patterns": [{ "competitor": "Gemini", "accounts": ["notion", "deutsche telekom", "linear"], "count": 3, "signal": "high" }],
  "recommended_actions": [{ "type": "competitive_positioning_note", "competitor": "Gemini" }]
}
```

`POST /slack/mentions` (request + response):

Notes:

- This endpoint is **demo-token gated** by `DEMO_TOKEN`.
- Preferred auth is `X-DEMO-TOKEN` header, but the demo agent/tooling can also send `demo_token` in the JSON body.

Request:

```json
{ "company": "Notion", "demo_token": "demo123" }
```

Response:

```json
{
  "company": "Notion",
  "mention_count": 2,
  "mentions": [
    {
      "from": "Alex Rivera",
      "channel": "#deals-smb",
      "text": "Notion discovery is tomorrow at 10. Maya is sharp — already asked about our concurrency model. Make sure we have the rate limit doc ready.",
      "ts": "2026-04-14T17:42:00Z"
    },
    {
      "from": "Sarah Kim",
      "channel": "#deals-smb",
      "text": "FYI — I saw Notion is also talking to Gemini's API team. Tom Park posted about it on LinkedIn last week. Worth bringing up our latency benchmarks proactively.",
      "ts": "2026-04-14T18:05:00Z"
    }
  ]
}
```

If the token is missing or wrong, you get a `403` with a structured `detail`:

```json
{
  "detail": {
    "ok": false,
    "error": {
      "code": "forbidden",
      "message": "Missing or invalid X-DEMO-TOKEN.",
      "fix": "Send X-DEMO-TOKEN header matching the DEMO_TOKEN env var (preferred), or include demo_token in the request body."
    },
    "fallback": { "draft_text": null }
  }
}
```

## Demo script (90 seconds)

1. Click **Start My Morning**
2. Say: “Start my morning”
3. Say: “Notion first”
4. Say: “Give me the top objection responses”
5. Say: “Deutsche Telekom”
6. When it offers to draft a Slack DM, say: “Yes”

## Troubleshooting (widget + mic)

- **Mic blocked**: allow microphone access for the site, then reload. On iOS Safari, also check Settings → Safari → Microphone.
- **Widget won’t connect**: most common cause is the ElevenLabs agent not being public. Switch it to public, or implement a signed-URL/token flow.
- **CORS errors (local dev)**: add your frontend origin to the `allow_origins` list (or set a safe `allow_origin_regex`) in `api/main.py`.

## API contract (backend)

The agent calls your HTTP API at `API_BASE_URL`. Responses are JSON.

Quick curls (live backend):

```bash
BASE="https://sdr-briefing-api.fly.dev"
curl -s "$BASE/"
curl -s "$BASE/health"
curl -s "$BASE/calendar/today"
curl -s "$BASE/patterns/today"
curl -s "$BASE/account/Deutsche%20Telekom"
curl -s -X POST "$BASE/followup/draft" -H "Content-Type: application/json" \
  -d '{"company":"Deutsche Telekom","action_type":"next_steps_summary"}'
```

Endpoints:

- `GET /` (service info, links to `/health` and `/docs`)
- `GET /health`
- `GET /calendar/today`
- `GET /account/{company}`
- `GET /gong/{company}`
- `GET /outreach/{company}`
- `GET /wiki/playbook/company/{company}`
- `GET /patterns/today`
- `POST /followup/draft` `{ company, action_type }`
- `POST /slack/mentions` `{ company, demo_token }`
  - For the demo, this endpoint is token-gated by `DEMO_TOKEN` (prefer `X-DEMO-TOKEN`, body token is also accepted).

## Local development

### 1) Create a venv and install deps

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2) Run the API locally

```bash
. .venv/bin/activate
uvicorn api.main:app --reload --port 8080
```

Visit:

- `http://localhost:8080/`
- `http://localhost:8080/health`
- `http://localhost:8080/docs`

### 3) Run tests

```bash
. .venv/bin/activate
pytest -q
```

## Updating the ElevenLabs agent

Source of truth:

- Prompt: `agent/system_prompt.md`
- Tools: `agent/tools.json`
- Push script: `agent/create_agent.py`

Steps:

1. Copy `.env.example` → `.env` and set:
   - `ELEVENLABS_API_KEY=...`
   - `API_BASE_URL=https://sdr-briefing-api.fly.dev` (or your local/ngrok URL)
2. Run:

```bash
. .venv/bin/activate
python agent/create_agent.py
```

This updates the existing agent (if `ELEVENLABS_AGENT_ID` is set) and writes a snapshot to `agent/agent_config.json`.

## Deployment notes

- **Fly.io backend**: `fly.toml` and `Dockerfile` are included.
- **Vercel frontend**: `vercel.json` routes:
  - `/` → `index.html`
  - `/try-agent` → `try-agent.html`

## Extra

- Outreach copy: `docs/OUTREACH.md`

