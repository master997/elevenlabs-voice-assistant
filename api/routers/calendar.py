from datetime import date

from fastapi import APIRouter

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/today")
def get_today():
    """Returns today's scheduled sales meetings."""
    return {
        "date": str(date.today()),
        "meetings": [
            {
                "time": "10:00",
                "company": "Notion",
                "contact": "Maya Chen",
                "title": "Head of Engineering",
                "type": "discovery",
            },
            {
                "time": "13:00",
                "company": "Deutsche Telekom",
                "contact": "Klaus Weber",
                "title": "VP of Digital Products",
                "type": "follow-up",
            },
            {
                "time": "15:30",
                "company": "Linear",
                "contact": "Karri Saarinen",
                "title": "CEO",
                "type": "demo",
            },
        ],
    }
