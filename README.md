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

