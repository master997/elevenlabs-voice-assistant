from fastapi import APIRouter, HTTPException

from api.data.companies import get_company, list_companies

router = APIRouter(prefix="/slack", tags=["slack"])


@router.get("/mentions/{company}")
def get_slack_mentions(company: str):
    """
    Internal Slack mentions of this company from the rep's teammates.
    Surfaces intel that doesn't live in Salesforce — e.g., a competitor spotted
    on LinkedIn, a warm intro from another team member.
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

    mentions = data["slack_mentions"]
    return {
        "company": data["sf_profile"]["company"],
        "mention_count": len(mentions),
        "mentions": mentions,
    }
