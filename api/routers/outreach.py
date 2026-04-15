from fastapi import APIRouter, HTTPException

from api.data.companies import get_company, list_companies

router = APIRouter(prefix="/outreach", tags=["outreach"])


@router.get("/{company}")
def get_outreach(company: str):
    """
    Outreach.io sequence engagement: open rates, reply rates, last touch.
    Tells the rep whether the prospect has been engaged or going cold.
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

    o = data["outreach"]
    return {
        "company": data["sf_profile"]["company"],
        "sequence": o["sequence"],
        "emails_sent": o["emails_sent"],
        "open_rate": o["open_rate"],
        "open_rate_pct": f"{int(o['open_rate'] * 100)}%",
        "reply_rate": o["reply_rate"],
        "reply_rate_pct": f"{int(o['reply_rate'] * 100)}%",
        "last_touch": o["last_touch"],
        "last_touch_type": o["last_touch_type"],
        "next_step_in_sequence": o["next_step_in_sequence"],
    }
