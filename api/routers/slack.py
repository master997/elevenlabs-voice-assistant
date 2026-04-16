import os
import re

import httpx
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from api.data.companies import get_company, list_companies

router = APIRouter(prefix="/slack", tags=["slack"])

_MASS_MENTION_RE = re.compile(r"<!(channel|here|everyone)>", flags=re.IGNORECASE)


class PostNextStepsBody(BaseModel):
    company: str
    draft_text: str
    demo_token: str | None = None


class PostSlackMentionsBody(BaseModel):
    company: str
    demo_token: str | None = None


def _sanitize_slack_text(text: str) -> str:
    return _MASS_MENTION_RE.sub("[mention removed]", text)


def _error_detail(*, code: str, message: str, fix: str, draft_text: str | None):
    return {
        "ok": False,
        "error": {"code": code, "message": message, "fix": fix},
        "fallback": {"draft_text": draft_text},
    }


@router.post("/post-next-steps")
def post_next_steps(
    body: PostNextStepsBody,
    x_demo_token: str | None = Header(default=None, alias="X-DEMO-TOKEN"),
):
    demo_token = os.getenv("DEMO_TOKEN")
    presented_token = x_demo_token or body.demo_token
    if not presented_token or not demo_token or presented_token != demo_token:
        raise HTTPException(
            status_code=403,
            detail=_error_detail(
                code="forbidden",
                message="Missing or invalid X-DEMO-TOKEN.",
                fix="Send X-DEMO-TOKEN header matching the DEMO_TOKEN env var (preferred), or include demo_token in the request body.",
                draft_text=body.draft_text,
            ),
        )

    # Keep demo inputs predictable: require a known company.
    if not get_company(body.company):
        raise HTTPException(
            status_code=404,
            detail={
                "ok": False,
                "error": {
                    "code": "company_not_found",
                    "message": f"Company '{body.company}' not found.",
                    "fix": "Use one of the valid companies.",
                },
                "context": {"valid_companies": list_companies()},
                "fallback": {"draft_text": body.draft_text},
            },
        )

    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        raise HTTPException(
            status_code=500,
            detail=_error_detail(
                code="missing_env",
                message="Server is missing SLACK_WEBHOOK_URL.",
                fix="Set SLACK_WEBHOOK_URL to a Slack Incoming Webhook URL.",
                draft_text=body.draft_text,
            ),
        )

    sanitized_text = _sanitize_slack_text(body.draft_text)
    payload = {"text": f"*Next steps — {body.company}*\n{sanitized_text}"}

    try:
        resp = httpx.post(webhook_url, json=payload, timeout=5.0)
    except (httpx.TimeoutException, httpx.RequestError) as e:
        raise HTTPException(
            status_code=502,
            detail=_error_detail(
                code="slack_unreachable",
                message=f"Failed to reach Slack webhook: {e.__class__.__name__}.",
                fix="Verify SLACK_WEBHOOK_URL and network egress; retry.",
                draft_text=body.draft_text,
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=_error_detail(
                code="internal_error",
                message=f"Unexpected error posting to Slack: {e.__class__.__name__}.",
                fix="Check server logs and retry.",
                draft_text=body.draft_text,
            ),
        )

    if resp.status_code < 200 or resp.status_code >= 300:
        raise HTTPException(
            status_code=502,
            detail=_error_detail(
                code="slack_bad_response",
                message=f"Slack webhook returned HTTP {resp.status_code}.",
                fix="Verify the Slack Incoming Webhook URL is valid and enabled.",
                draft_text=body.draft_text,
            ),
        )

    return {
        "ok": True,
        "posted": {"ok": True},
        # Return the sanitized version too, so clients never end up copy-pasting pings.
        "fallback": {"draft_text": sanitized_text},
    }


@router.post("/mentions")
def get_slack_mentions(
    body: PostSlackMentionsBody,
    x_demo_token: str | None = Header(default=None, alias="X-DEMO-TOKEN"),
):
    """
    Internal Slack mentions of this company from the rep's teammates.
    Surfaces intel that doesn't live in Salesforce — e.g., a competitor spotted
    on LinkedIn, a warm intro from another team member.
    """
    demo_token = os.getenv("DEMO_TOKEN")
    presented_token = x_demo_token or body.demo_token
    if not presented_token or not demo_token or presented_token != demo_token:
        raise HTTPException(
            status_code=403,
            detail=_error_detail(
                code="forbidden",
                message="Missing or invalid X-DEMO-TOKEN.",
                fix="Send X-DEMO-TOKEN header matching the DEMO_TOKEN env var (preferred), or include demo_token in the request body.",
                draft_text=None,
            ),
        )

    # Keep demo inputs predictable: require a known company.
    data = get_company(body.company)
    if not data:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Company '{body.company}' not found",
                "valid_companies": list_companies(),
            },
        )

    mentions = data["slack_mentions"]
    return {
        "company": data["sf_profile"]["company"],
        "mention_count": len(mentions),
        "mentions": mentions,
    }
