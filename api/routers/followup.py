from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.data.companies import get_company, list_companies

router = APIRouter(prefix="/followup", tags=["followup"])


class FollowUpRequest(BaseModel):
    company: str
    action_type: str  # "competitive_positioning_note" | "next_steps_summary" | "intro_request"


@router.post("/draft")
def draft_followup(req: FollowUpRequest):
    """
    Drafts a mock Slack DM the rep can send based on a post-briefing action.
    Supported action types:
      - competitive_positioning_note: Gemini battle card DM to the team
      - next_steps_summary: recap of next steps to send to the prospect
      - intro_request: warm intro request to a contact in the account
    """
    data = get_company(req.company)
    if not data:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Company '{req.company}' not found",
                "valid_companies": list_companies(),
            },
        )

    sf = data["sf_profile"]
    call = data["gong_last_call"]
    company_name = sf["company"]

    drafts = {
        "competitive_positioning_note": _draft_competitive_note(company_name, call),
        "next_steps_summary": _draft_next_steps(company_name, call, sf),
        "intro_request": _draft_intro_request(company_name, sf),
    }

    draft = drafts.get(req.action_type)
    if not draft:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Unknown action_type '{req.action_type}'",
                "valid_action_types": list(drafts.keys()),
            },
        )

    return {
        "company": company_name,
        "action_type": req.action_type,
        "draft": draft,
        "destination": "Slack DM",
    }


def _draft_competitive_note(company: str, call: dict) -> str:
    competitors = call.get("competitive_mentions", [])
    if not competitors:
        return f"Heads up — no competitive mentions in the last {company} call."

    competitor = competitors[0]
    return (
        f"Hey team — heads up on {competitor} for today's calls. "
        f"Came up in {company} last week and it's showing up across all 3 accounts today. "
        f"Key talking points:\n"
        f"• {competitor}'s speech API is general-purpose, not voice-UX native — "
        f"no streaming, no word-level timestamps.\n"
        f"• For customer-facing voice features, the quality gap is audible in a 10-second demo.\n"
        f"• We can offer a side-by-side demo if any account wants to compare directly.\n"
        f"Ping me if you need the full battle card."
    )


def _draft_next_steps(company: str, call: dict, sf: dict) -> str:
    steps = call.get("next_steps", [])
    owner = sf.get("owner", "the team")
    if not steps:
        return f"No next steps recorded from the last {company} call."

    steps_formatted = "\n".join(f"• {s}" for s in steps)
    return (
        f"Hi — quick recap from our last call. Here's what we committed to:\n\n"
        f"{steps_formatted}\n\n"
        f"I'll have these over to you shortly. Let me know if anything's changed on your end."
    )


def _draft_intro_request(company: str, sf: dict) -> str:
    return (
        f"Hey — working the {company} account and would love a warm intro "
        f"if you have any connections there. "
        f"They're a {sf.get('plan', 'Business')} prospect in {sf.get('industry', 'tech')}, "
        f"based in {sf.get('hq', 'SF')}. "
        f"Happy to share more context — just let me know."
    )
