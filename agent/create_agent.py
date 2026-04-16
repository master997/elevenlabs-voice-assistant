#!/usr/bin/env python3
"""
Creates (or updates) the ElevenLabs Conversational AI agent.

Usage:
  python agent/create_agent.py

Reads from:
  - agent/system_prompt.md    — the agent's system prompt
  - agent/tools.json          — tool definitions with {API_BASE_URL} placeholder

Reads env from .env:
  - ELEVENLABS_API_KEY        — required
  - API_BASE_URL              — required (Fly.io URL or ngrok for local testing)
  - ELEVENLABS_AGENT_ID       — if set, updates existing agent instead of creating new

Writes to:
  - agent/agent_config.json   — full config snapshot (for open-source repo)
  - .env                      — adds/updates ELEVENLABS_AGENT_ID
"""

import json
import os
import re
import sys
from pathlib import Path

import httpx
from dotenv import dotenv_values, load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://sdr-briefing-api.fly.dev")
EXISTING_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")

# Rachel — warm, professional, not narrator-bot
RACHEL_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"


def load_system_prompt() -> str:
    prompt_path = ROOT / "agent" / "system_prompt.md"
    raw = prompt_path.read_text()
    # Strip the markdown header block (lines before the first ---)
    lines = raw.split("\n")
    in_header = True
    result = []
    for line in lines:
        if in_header and line.strip() == "---":
            in_header = False
            continue
        if not in_header:
            result.append(line)
    return "\n".join(result).strip()


def load_tools(api_base_url: str) -> list:
    tools_path = ROOT / "agent" / "tools.json"
    raw = tools_path.read_text()
    # Substitute {API_BASE_URL} placeholder everywhere in the file
    raw = raw.replace("{API_BASE_URL}", api_base_url.rstrip("/"))
    return json.loads(raw)


def build_agent_payload(system_prompt: str, tools: list) -> dict:
    return {
        "name": "SDR Morning Briefing",
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": system_prompt,
                    "llm": "claude-3-5-sonnet",
                    "temperature": 0.4,
                    "tools": tools,
                },
                "first_message": (
                    "Good morning. Let me pull up your schedule for today."
                ),
                "language": "en",
            },
            "tts": {
                "voice_id": RACHEL_VOICE_ID,
                "model_id": "eleven_turbo_v2",
                "optimize_streaming_latency": 3,
            },
            "turn": {
                "turn_timeout": 10,
                "silence_end_of_speech_threshold": 0.5,
            },
        },
        "platform_settings": {
            "auth": {
                "enable_auth": False,
            },
        },
    }


def upsert_agent(payload: dict) -> dict:
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=30) as client:
        if EXISTING_AGENT_ID:
            print(f"Updating existing agent: {EXISTING_AGENT_ID}")
            resp = client.patch(
                f"https://api.elevenlabs.io/v1/convai/agents/{EXISTING_AGENT_ID}",
                headers=headers,
                json=payload,
            )
        else:
            print("Creating new agent...")
            resp = client.post(
                "https://api.elevenlabs.io/v1/convai/agents/create",
                headers=headers,
                json=payload,
            )

    if resp.status_code not in (200, 201):
        print(f"ERROR {resp.status_code}: {resp.text}")
        sys.exit(1)

    return resp.json()


def update_env_agent_id(agent_id: str):
    env_path = ROOT / ".env"
    if env_path.exists():
        content = env_path.read_text()
        if "ELEVENLABS_AGENT_ID=" in content:
            content = re.sub(
                r"ELEVENLABS_AGENT_ID=.*",
                f"ELEVENLABS_AGENT_ID={agent_id}",
                content,
            )
        else:
            content += f"\nELEVENLABS_AGENT_ID={agent_id}\n"
        env_path.write_text(content)
    else:
        env_path.write_text(f"ELEVENLABS_AGENT_ID={agent_id}\n")


def save_config_snapshot(payload: dict, agent_id: str):
    snapshot = {
        "agent_id": agent_id,
        "api_base_url": API_BASE_URL,
        **payload,
    }
    out_path = ROOT / "agent" / "agent_config.json"
    out_path.write_text(json.dumps(snapshot, indent=2))
    print(f"Config snapshot saved to agent/agent_config.json")


def main():
    if not ELEVENLABS_API_KEY:
        print("ERROR: ELEVENLABS_API_KEY not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    DEMO_TOKEN = os.getenv("DEMO_TOKEN")
    if not DEMO_TOKEN:
        print(
            "ERROR: DEMO_TOKEN not set.\n"
            "Set DEMO_TOKEN in your environment or .env (same value you used for Fly secrets)\n"
            "so the agent can auth the Slack demo webhook tool."
        )
        sys.exit(1)

    print(f"API base URL: {API_BASE_URL}")
    print(f"Voice: Rachel ({RACHEL_VOICE_ID})")

    system_prompt = load_system_prompt()
    system_prompt = system_prompt.replace("{DEMO_TOKEN}", DEMO_TOKEN)
    tools = load_tools(API_BASE_URL)
    payload = build_agent_payload(system_prompt, tools)

    print(f"Tools loaded: {[t['name'] for t in tools]}")

    result = upsert_agent(payload)
    agent_id = result.get("agent_id") or EXISTING_AGENT_ID

    print(f"\nAgent ID: {agent_id}")
    print(f"Share URL: https://elevenlabs.io/convai/agent/{agent_id}")
    print(f"\nEmbed widget snippet:")
    print(f'<elevenlabs-convai agent-id="{agent_id}"></elevenlabs-convai>')
    print(f'<script src="https://elevenlabs.io/convai-widget/index.js" async></script>')

    update_env_agent_id(agent_id)
    # Never commit real demo tokens into agent config snapshots.
    payload_snapshot = json.loads(json.dumps(payload))
    prompt = (
        payload_snapshot.get("conversation_config", {})
        .get("agent", {})
        .get("prompt", {})
        .get("prompt")
    )
    if isinstance(prompt, str):
        payload_snapshot["conversation_config"]["agent"]["prompt"]["prompt"] = prompt.replace(
            DEMO_TOKEN, "{DEMO_TOKEN}"
        )

    save_config_snapshot(payload_snapshot, agent_id)
    print(f"\nDone. ELEVENLABS_AGENT_ID written to .env")


if __name__ == "__main__":
    main()
