from fastapi import APIRouter, HTTPException

from api.data.companies import get_company, list_companies

router = APIRouter(prefix="/gong", tags=["gong"])


@router.get("/{company}")
def get_gong(company: str):
    """
    Last Gong call data: summary, objections, next steps, competitive mentions.
    Agent uses this to brief the rep on what happened last time and what to expect.
    """
    data = get_company(company)
    if not data:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Company '{company}' not found",
                "valid_companies": list_companies(),
            },
        )

    call = data["gong_last_call"]
    return {
        "company": data["sf_profile"]["company"],
        "last_call_date": call["date"],
        "duration_minutes": call["duration_minutes"],
        "participants": call["participants"],
        "summary": call["summary"],
        "objections": call["objections"],
        "next_steps": call["next_steps"],
        "competitive_mentions": call["competitive_mentions"],
        "talk_time_ratio": call["talk_time_ratio"],
        "sentiment": call["sentiment"],
    }
