from fastapi import APIRouter

from api.data.patterns import get_patterns_today

router = APIRouter(prefix="/patterns", tags=["patterns"])


@router.get("/today")
def patterns_today():
    """
    Cross-call patterns for today's meetings.
    Agent uses this to proactively surface themes the rep should know about
    before the first call — e.g., the same competitor coming up in every call.
    """
    return get_patterns_today()
