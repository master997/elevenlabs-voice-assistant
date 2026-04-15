# SDR Morning Briefing — ElevenLabs Voice Agent Demo

Live demo stack:

- **Backend (FastAPI)**: `https://sdr-briefing-api.fly.dev`
- **Voice agent (ElevenLabs ConvAI)**: `agent_0701kp8zca3sfyb986q071k7xv25`

This project is a voice-first SDR morning briefing assistant. It pulls context from multiple “systems” (mocked): Salesforce, Gong, Slack, Outreach, and an internal sales wiki. It then briefs the rep conversationally and surfaces cross-call patterns (e.g., “Gemini came up in all 3 calls today”), and can draft a Slack DM.

## What to try (90-second script)

1. “Start my morning”
2. “Notion first”
3. “Give me the top objection responses”
4. “Deutsche Telekom”
5. “Yes”

## API endpoints (all live)

- `GET /calendar/today`
- `GET /account/{company}`
- `GET /gong/{company}`
- `GET /slack/mentions/{company}`
- `GET /outreach/{company}`
- `GET /wiki/playbook/company/{company}`
- `GET /patterns/today`
- `POST /followup/draft` `{ company, action_type }`

## Local setup

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

Visit `http://localhost:8080/health`.

## Updating the ElevenLabs agent

The agent is created/updated programmatically.

- **Prompt source of truth**: `agent/system_prompt.md`
- **Tool definitions**: `agent/tools.json`
- **Push script**: `agent/create_agent.py`

### Steps

1) Copy `.env.example` → `.env` and set:

- `ELEVENLABS_API_KEY=...`
- `API_BASE_URL=https://sdr-briefing-api.fly.dev` (or your local/ngrok URL)

2) Run:

```bash
. .venv/bin/activate
python agent/create_agent.py
```

This updates the existing agent (if `ELEVENLABS_AGENT_ID` is present) and writes a fresh config snapshot to `agent/agent_config.json`.

## Security notes

- `.env` is gitignored; don’t commit keys.
- If an API key is ever pasted into chat/logs, rotate it immediately in ElevenLabs.
- When creating an ElevenLabs key for this repo, scope it to the minimum (typically **ElevenAgents: Write** is sufficient for agent updates).

## Deployment

### Fly.io backend

`fly.toml` and `Dockerfile` are included. Once deployed, you can enable auto-deploy on pushes to `main` via GitHub Actions by adding a `FLY_API_TOKEN` secret.

## Why voice (short)

SDRs are mobile between meetings. Voice reduces tab-switching and lets the rep get “just enough” context (2–3 points) with natural follow-ups.

