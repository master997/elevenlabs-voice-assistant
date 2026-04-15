"""
Cross-call pattern detection.

Scans today's meetings and surfaces shared themes the agent should
proactively mention to the rep — e.g., the same competitor coming up
in every call, or the same objection category across accounts.
"""

from __future__ import annotations

from api.data.companies import COMPANIES, TODAY_MEETINGS


def get_patterns_today() -> dict:
    """
    Analyze today's meetings for cross-call patterns.
    Returns structured patterns the agent can surface proactively.
    """
    today_data = [
        {"company": name, **COMPANIES[name]}
        for name in TODAY_MEETINGS
        if name in COMPANIES
    ]

    # --- Competitive mentions ---
    competitor_map: dict[str, list[str]] = {}
    for account in today_data:
        mentions = account["gong_last_call"].get("competitive_mentions", [])
        for competitor in mentions:
            competitor_map.setdefault(competitor, []).append(account["company"])

    competitive_patterns = [
        {
            "competitor": competitor,
            "accounts": accounts,
            "count": len(accounts),
            "signal": "high" if len(accounts) >= 3 else "medium" if len(accounts) == 2 else "low",
        }
        for competitor, accounts in competitor_map.items()
        if len(accounts) >= 2  # only surface if 2+ calls mention the same competitor
    ]

    # --- Objection category patterns ---
    objection_map: dict[str, list[str]] = {}
    for account in today_data:
        for obj in account["gong_last_call"].get("objections", []):
            category = obj["category"]
            objection_map.setdefault(category, []).append(account["company"])

    objection_patterns = [
        {
            "category": category,
            "accounts": accounts,
            "count": len(accounts),
        }
        for category, accounts in objection_map.items()
        if len(accounts) >= 2
    ]

    # --- Recommended actions ---
    actions = []

    for pattern in competitive_patterns:
        if pattern["signal"] == "high":
            actions.append({
                "type": "competitive_positioning_note",
                "competitor": pattern["competitor"],
                "accounts": pattern["accounts"],
                "suggested_action": (
                    f"Draft a {pattern['competitor']} competitive positioning note "
                    f"and send to Slack DMs — it came up in all {pattern['count']} calls today."
                ),
            })
        elif pattern["signal"] == "medium":
            actions.append({
                "type": "competitive_prep",
                "competitor": pattern["competitor"],
                "accounts": pattern["accounts"],
                "suggested_action": (
                    f"{pattern['competitor']} came up in {pattern['count']} of your calls today "
                    f"({', '.join(pattern['accounts'])}). Worth reviewing the battle card before your next call."
                ),
            })

    return {
        "date": "today",
        "meetings_analyzed": [a["company"] for a in today_data],
        "competitive_patterns": competitive_patterns,
        "objection_patterns": objection_patterns,
        "recommended_actions": actions,
        "summary": _build_summary(competitive_patterns, objection_patterns),
    }


def _build_summary(competitive_patterns: list, objection_patterns: list) -> str:
    parts = []

    for p in competitive_patterns:
        if p["signal"] == "high":
            accounts_str = ", ".join(p["accounts"][:-1]) + f" and {p['accounts'][-1]}"
            parts.append(
                f"{p['competitor']} came up in all {p['count']} of your calls today "
                f"({accounts_str})."
            )
        elif p["signal"] == "medium":
            accounts_str = " and ".join(p["accounts"])
            parts.append(
                f"{p['competitor']} came up in both {accounts_str}."
            )

    for p in objection_patterns:
        accounts_str = " and ".join(p["accounts"])
        parts.append(
            f"Both {accounts_str} raised {p['category'].replace('_', ' ')} concerns."
        )

    if not parts:
        return "No significant cross-call patterns detected for today."

    return " ".join(parts)
