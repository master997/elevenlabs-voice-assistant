from fastapi import APIRouter, HTTPException

from api.data.companies import COMPANIES, get_company, list_companies

router = APIRouter(prefix="/wiki", tags=["wiki"])

# Map segment names to companies that use that playbook
SEGMENT_ALIASES = {
    "smb": "smb",
    "small business": "smb",
    "mid-market": "mid-market",
    "midmarket": "mid-market",
    "mid market": "mid-market",
    "enterprise": "enterprise",
}


@router.get("/playbook/{segment}")
def get_playbook(segment: str):
    """
    Internal wiki talk track for a given segment (SMB, Mid-Market, Enterprise).
    Includes full talk track, competitive responses, and discovery questions.
    """
    normalized = SEGMENT_ALIASES.get(segment.lower())
    if not normalized:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Segment '{segment}' not found",
                "valid_segments": ["smb", "mid-market", "enterprise"],
            },
        )

    # Find a representative company for this segment to pull the playbook
    representative = next(
        (
            name
            for name, data in COMPANIES.items()
            if data["wiki_playbook"]["segment"].lower() == normalized
        ),
        None,
    )

    if not representative:
        raise HTTPException(status_code=404, detail={"error": f"No playbook found for segment '{segment}'"})

    playbook = COMPANIES[representative]["wiki_playbook"]
    return {
        "segment": normalized,
        "talk_track": playbook["talk_track"],
        "competitive_responses": playbook["competitive_responses"],
        "discovery_questions": playbook["discovery_questions"],
    }


@router.get("/playbook/company/{company}")
def get_playbook_for_company(company: str):
    """
    Returns the wiki playbook specific to a company's segment.
    More useful than the generic segment playbook — tailored talk track for this account.
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

    playbook = data["wiki_playbook"]
    return {
        "company": data["sf_profile"]["company"],
        "segment": playbook["segment"],
        "talk_track": playbook["talk_track"],
        "competitive_responses": playbook["competitive_responses"],
        "discovery_questions": playbook["discovery_questions"],
    }
