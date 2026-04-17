from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import calendar, account, gong, slack, outreach, wiki, patterns, followup

app = FastAPI(
    title="SDR Morning Briefing API",
    description=(
        "Voice-first sales briefing assistant — unifies Salesforce, Gong, "
        "Slack, Outreach, and internal wiki into a single conversational interface."
    ),
    version="0.2.0",
)


@app.get("/")
def root():
    return {
        "service": "SDR Morning Briefing API",
        "version": app.version,
        "links": {"health": "/health", "docs": "/docs"},
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:8080",
        "https://localhost:3000",
    ],
    allow_origin_regex=r"^https://.*\\.vercel\\.app$",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calendar.router)
app.include_router(account.router)
app.include_router(gong.router)
app.include_router(slack.router)
app.include_router(outreach.router)
app.include_router(wiki.router)
app.include_router(patterns.router)
app.include_router(followup.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.2.0"}
