from fastapi import APIRouter, HTTPException

from api.data.companies import get_company, list_companies

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/{company}")
def get_account(company: str):
    """
    Unified account view across Salesforce, Slack, and Outreach.
    This is the first call the agent makes when a rep asks about an account.
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

    sf = data["sf_profile"]
    outreach = data["outreach"]
    slack = data["slack_mentions"]

    return {
        "company": sf["company"],
        "arr": sf["arr"],
        "arr_formatted": f"${sf['arr']:,}",
        "plan": sf["plan"],
        "stage": sf["stage"],
        "next_renewal": sf["next_renewal"],
        "owner": sf["owner"],
        "industry": sf["industry"],
        "employees": sf["employees"],
        "hq": sf["hq"],
        "account_notes": sf["notes"],
        "outreach_summary": {
            "sequence": outreach["sequence"],
            "last_touch": outreach["last_touch"],
            "last_touch_type": outreach["last_touch_type"],
            "open_rate": outreach["open_rate"],
            "reply_rate": outreach["reply_rate"],
        },
        "recent_slack_activity": slack,
    }
