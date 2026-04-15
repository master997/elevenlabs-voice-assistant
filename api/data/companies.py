"""
Mock company data — indistinguishable from real CRM exports.

Each record unifies 5 sources:
  sf_profile       → Salesforce account object
  gong_last_call   → Gong call transcript summary
  slack_mentions   → Internal Slack mentions from teammates
  outreach         → Outreach.io sequence engagement
  wiki_playbook    → Internal sales wiki (talk track, competitive responses)

Today's meetings: Notion (10:00), Deutsche Telekom (13:00), Linear (15:30)
"""

from __future__ import annotations

COMPANIES: dict[str, dict] = {
    "notion": {
        "sf_profile": {
            "company": "Notion",
            "arr": 28_000,
            "plan": "Business",
            "stage": "Discovery",
            "next_renewal": "2026-09-01",
            "owner": "Alex Rivera",
            "industry": "Productivity Software",
            "employees": 700,
            "hq": "San Francisco, CA",
            "website": "notion.so",
            "notes": "Inbound lead from ElevenLabs blog post on voice-to-doc workflows. "
                     "Currently using AssemblyAI for internal meeting transcription. "
                     "Evaluating ElevenLabs for customer-facing voice features in their API product.",
        },
        "gong_last_call": {
            "date": "2026-04-08",
            "duration_minutes": 32,
            "participants": ["Maya Chen (Notion)", "Alex Rivera (ElevenLabs)"],
            "summary": "Maya walked through their current transcription pipeline. "
                       "They process ~400K minutes/month of internal Notion AI calls. "
                       "Main interest is Scribe for automated meeting notes in Notion docs. "
                       "Strong technical depth — she had already read our API docs.",
            "objections": [
                {
                    "text": "We hit API rate limits on the Scribe endpoint during peak hours — "
                            "around 9-11 AM PST when our US team is syncing. "
                            "We need a guaranteed throughput SLA before we can commit.",
                    "category": "technical",
                    "severity": "high",
                },
                {
                    "text": "Our eng team is already stretched. "
                            "If the integration takes more than a sprint to stand up, "
                            "it won't get prioritized until Q3.",
                    "category": "implementation",
                    "severity": "medium",
                },
            ],
            "next_steps": [
                "Send the enterprise rate limit addendum by EOW (Alex)",
                "Share the Scribe SDK quickstart — Maya wants to run a spike in week 2",
                "Loop in their backend lead (Tom Park) for the technical deep-dive",
            ],
            "competitive_mentions": ["Gemini"],
            "talk_time_ratio": {"rep": 0.38, "prospect": 0.62},
            "sentiment": "positive",
        },
        "slack_mentions": [
            {
                "from": "Alex Rivera",
                "channel": "#deals-smb",
                "text": "Notion discovery is tomorrow at 10. Maya is sharp — "
                        "already asked about our concurrency model. "
                        "Make sure we have the rate limit doc ready.",
                "ts": "2026-04-14T17:42:00Z",
            },
            {
                "from": "Sarah Kim",
                "channel": "#deals-smb",
                "text": "FYI — I saw Notion is also talking to Gemini's API team. "
                        "Tom Park posted about it on LinkedIn last week. "
                        "Worth bringing up our latency benchmarks proactively.",
                "ts": "2026-04-14T18:05:00Z",
            },
        ],
        "outreach": {
            "sequence": "SMB Inbound — Technical Buyer",
            "emails_sent": 3,
            "open_rate": 1.0,
            "reply_rate": 0.67,
            "last_touch": "2026-04-10",
            "last_touch_type": "email reply — confirmed discovery call",
            "next_step_in_sequence": "Post-discovery follow-up (auto-sends 24h after call)",
        },
        "wiki_playbook": {
            "segment": "SMB",
            "talk_track": (
                "Lead with the Scribe SDK quickstart — it's a one-afternoon integration "
                "for a backend engineer. Frame the rate limit question as a solved problem: "
                "our enterprise tier includes a dedicated concurrency pool. "
                "If they push back on timeline, offer a 30-day pilot on Business plan "
                "with an upgrade path baked in."
            ),
            "competitive_responses": {
                "Gemini": (
                    "Gemini's speech-to-text is solid for general transcription, "
                    "but it's not built for voice UX — no streaming, no word-level timestamps, "
                    "no multilingual speaker diarization out of the box. "
                    "If Notion wants to ship voice features that feel like a product "
                    "and not a research experiment, ElevenLabs is the only real option. "
                    "Point to Figma's use case as a reference — similar company profile."
                ),
                "AssemblyAI": (
                    "They're already on AssemblyAI — that's a replacement motion, not greenfield. "
                    "Focus on what AssemblyAI can't do: voice cloning, TTS, the conversational AI layer. "
                    "The Scribe endpoint alone isn't the pitch — it's the platform story."
                ),
            },
            "discovery_questions": [
                "What does your current meeting transcription workflow look like end-to-end?",
                "Where does the transcript go after it's generated — Notion doc, Slack, somewhere else?",
                "Who owns the voice feature roadmap — eng or product?",
                "What would a successful pilot look like in 30 days?",
            ],
        },
    },

    "deutsche telekom": {
        "sf_profile": {
            "company": "Deutsche Telekom",
            "arr": 180_000,
            "plan": "Enterprise",
            "stage": "Negotiation",
            "next_renewal": "2026-07-15",
            "owner": "Marcus Webb",
            "industry": "Telecommunications",
            "employees": 216_000,
            "hq": "Bonn, Germany",
            "website": "telekom.com",
            "notes": "Strategic account. DT is building a voice-first customer service layer "
                     "for their B2B product (T-Systems). "
                     "Legal and InfoSec are the main blockers — not budget, not technical fit. "
                     "Executive sponsor is Klaus Weber (VP Digital Products). "
                     "Procurement is involved; expect a 6-8 week contract cycle.",
        },
        "gong_last_call": {
            "date": "2026-04-02",
            "duration_minutes": 58,
            "participants": [
                "Klaus Weber (DT)", "Anna Schmidt (DT InfoSec)", "Marcus Webb (ElevenLabs)"
            ],
            "summary": "Strong alignment on product fit. DT wants to use Conversational AI "
                       "for tier-1 customer support across 5 languages. "
                       "Anna Schmidt (InfoSec) raised hard blockers on data residency. "
                       "Klaus is internally selling to the CTO — he needs our compliance docs "
                       "to make the business case. ARR at $180K is below their internal threshold "
                       "for strategic vendor status; Marcus flagged we may need to bundle "
                       "the voice cloning add-on to cross $200K.",
            "objections": [
                {
                    "text": "We need SOC 2 Type II and ISO 27001 before this goes to procurement. "
                            "Our InfoSec team will not approve a vendor without both.",
                    "category": "compliance",
                    "severity": "critical",
                },
                {
                    "text": "GDPR requires that German customer voice data never leaves the EU. "
                            "We need written confirmation that your EU data residency option "
                            "is available on our contract tier.",
                    "category": "legal",
                    "severity": "critical",
                },
                {
                    "text": "Our procurement team needs a minimum 90-day payment term. "
                            "Standard net-30 won't clear their AP process.",
                    "category": "commercial",
                    "severity": "medium",
                },
            ],
            "next_steps": [
                "Send SOC 2 Type II report and ISO 27001 cert to Anna Schmidt by EOW (Marcus)",
                "Confirm EU data residency availability for Enterprise tier — check with legal",
                "Draft a bundled quote including voice cloning add-on to cross $200K threshold",
                "Klaus to present to CTO in the April 22 leadership review",
            ],
            "competitive_mentions": ["Gemini"],
            "talk_time_ratio": {"rep": 0.44, "prospect": 0.56},
            "sentiment": "cautiously_positive",
        },
        "slack_mentions": [
            {
                "from": "Marcus Webb",
                "channel": "#deals-enterprise",
                "text": "DT follow-up is today at 1pm. Klaus needs the SOC 2 doc "
                        "before the April 22 CTO review. If we miss that window, "
                        "this slips to Q3. I've got the doc — just need legal to clear "
                        "the EU residency language.",
                "ts": "2026-04-15T08:12:00Z",
            },
            {
                "from": "Jamie Osei",
                "channel": "#deals-enterprise",
                "text": "Heads up — Gemini's enterprise team just announced a EU data center "
                        "in Frankfurt. DT's InfoSec team almost certainly knows. "
                        "We should get ahead of it.",
                "ts": "2026-04-14T16:30:00Z",
            },
        ],
        "outreach": {
            "sequence": "Enterprise — Legal & Compliance Track",
            "emails_sent": 7,
            "open_rate": 1.0,
            "reply_rate": 0.86,
            "last_touch": "2026-04-10",
            "last_touch_type": "email — sent draft EU data residency addendum for review",
            "next_step_in_sequence": "Manual — following up on addendum review status",
        },
        "wiki_playbook": {
            "segment": "Enterprise",
            "talk_track": (
                "DT is not a technical sale — it's a compliance and trust sale. "
                "Klaus is already sold. Your job today is to unblock Anna Schmidt. "
                "Lead with the SOC 2 report, then the EU residency confirmation. "
                "If the EU residency language isn't cleared by legal yet, do not wing it — "
                "escalate to Marcus before the call. "
                "On the $200K threshold: frame the voice cloning add-on as a capability "
                "they'll need in phase 2 anyway (multilingual brand voice). "
                "Net-90 payment terms — check with finance, this is usually approvable."
            ),
            "competitive_responses": {
                "Gemini": (
                    "Gemini's Frankfurt data center is real, but they don't have an enterprise "
                    "voice product — it's a research API. No SLA, no dedicated support, "
                    "no conversational AI layer. "
                    "DT is building a customer-facing product, not a prototype. "
                    "Ask Anna: what's the SLA guarantee from Gemini? Who's their TAM? "
                    "ElevenLabs offers a dedicated enterprise success team and 99.9% uptime SLA. "
                    "Gemini can't say that."
                ),
            },
            "discovery_questions": [
                "Has Anna had a chance to review the EU data residency addendum we sent?",
                "What's the CTO's biggest concern going into the April 22 review?",
                "If we clear compliance this week, what's the realistic procurement timeline?",
            ],
        },
    },

    "linear": {
        "sf_profile": {
            "company": "Linear",
            "arr": 72_000,
            "plan": "Business",
            "stage": "Demo",
            "next_renewal": "2026-10-01",
            "owner": "Alex Rivera",
            "industry": "Developer Tools",
            "employees": 80,
            "hq": "San Francisco, CA",
            "website": "linear.app",
            "notes": "Product-led growth motion. Karri (CEO) is technical and will ask hard questions. "
                     "They want to add voice commands to Linear — think 'create issue for this bug' "
                     "from a voice interface. Small team, fast decisions. "
                     "If the demo lands, could close in 2 weeks.",
        },
        "gong_last_call": {
            "date": "2026-04-01",
            "duration_minutes": 24,
            "participants": ["Karri Saarinen (Linear)", "Alex Rivera (ElevenLabs)"],
            "summary": "Quick discovery call. Karri wants voice commands as a first-class feature "
                       "in Linear's desktop app. They're thinking push-to-talk for issue creation, "
                       "status updates, and meeting summaries. "
                       "Their users are in EU and US — latency is critical for a desktop interaction. "
                       "Karri mentioned they looked at Whisper and found it too slow for real-time.",
            "objections": [
                {
                    "text": "We tested the streaming endpoint from our EU servers and saw "
                            "140-160ms P95 latency. For a keyboard-replacement interaction, "
                            "anything over 100ms feels broken. "
                            "Can you get us under 100ms from EU?",
                    "category": "technical",
                    "severity": "high",
                },
                {
                    "text": "We're 80 people. We don't have a dedicated ML team to manage "
                            "a complex integration. It needs to be a clean SDK, not a research paper.",
                    "category": "implementation",
                    "severity": "medium",
                },
            ],
            "next_steps": [
                "Run latency benchmark from eu-west-1 — share results with Karri before demo",
                "Show the streaming SDK demo with the new low-latency endpoint",
                "Have pricing sheet for Business plan with volume discount at 500K min/mo",
            ],
            "competitive_mentions": ["Gemini", "Whisper"],
            "talk_time_ratio": {"rep": 0.41, "prospect": 0.59},
            "sentiment": "positive",
        },
        "slack_mentions": [
            {
                "from": "Alex Rivera",
                "channel": "#deals-midmarket",
                "text": "Linear demo is at 3:30. Karri's whole thing is latency — "
                        "he's going to ask about EU P95. Make sure I have the new "
                        "eu-west-1 benchmark numbers from infra before I get on.",
                "ts": "2026-04-15T09:00:00Z",
            },
            {
                "from": "Priya Nair",
                "channel": "#deals-midmarket",
                "text": "Just saw Linear's job board — they posted a 'Voice Features Engineer' "
                        "role yesterday. They're serious about this. "
                        "Also, Gemini's streaming API is in their tech stack already "
                        "(they use it for their AI assistant). Worth knowing.",
                "ts": "2026-04-14T14:22:00Z",
            },
        ],
        "outreach": {
            "sequence": "Mid-Market — PLG Technical Buyer",
            "emails_sent": 4,
            "open_rate": 1.0,
            "reply_rate": 0.75,
            "last_touch": "2026-04-12",
            "last_touch_type": "email — shared eu-west-1 latency benchmark doc",
            "next_step_in_sequence": "Post-demo follow-up (manual)",
        },
        "wiki_playbook": {
            "segment": "Mid-Market",
            "talk_track": (
                "Karri is a founder-CEO who ships fast. Don't over-pitch. "
                "Lead with the latency benchmark — if the numbers are good, you're 80% there. "
                "Show the streaming SDK in a live demo, not slides. "
                "If he asks about the Whisper comparison: Whisper is batch, not streaming. "
                "Our streaming endpoint is purpose-built for real-time interaction. "
                "Close ask: 30-day pilot, Business plan, they integrate and you co-own the latency target."
            ),
            "competitive_responses": {
                "Gemini": (
                    "Linear already uses Gemini for their AI assistant — this isn't a replacement, "
                    "it's an addition. Gemini's speech API is batch-oriented and not optimized "
                    "for <100ms streaming. We're not competing with Gemini here; "
                    "we're doing something they don't do. "
                    "Frame it as: Gemini for text intelligence, ElevenLabs for voice interaction."
                ),
                "Whisper": (
                    "Whisper is a model, not a product. "
                    "Self-hosting Whisper means managing infra, latency, and model updates. "
                    "ElevenLabs is a managed endpoint with an SLA. "
                    "For an 80-person team without an ML team, that's the whole argument."
                ),
            },
            "discovery_questions": [
                "What's the target interaction — always-on mic or push-to-talk?",
                "Where does the voice command output go — directly to Linear API or through your backend?",
                "What's your rollout plan — internal dogfood first, or straight to users?",
            ],
        },
    },

    "figma": {
        "sf_profile": {
            "company": "Figma",
            "arr": 95_000,
            "plan": "Business",
            "stage": "Evaluation",
            "next_renewal": "2026-11-15",
            "owner": "Sarah Kim",
            "industry": "Design Tools",
            "employees": 1_200,
            "hq": "San Francisco, CA",
            "website": "figma.com",
            "notes": "Figma wants to add voice annotation to their design review workflow. "
                     "Think: designer records a voice note on a component, "
                     "transcript appears inline in the comment thread. "
                     "Currently evaluating us vs. building on Whisper internally. "
                     "The 'build vs. buy' question is the main blocker.",
        },
        "gong_last_call": {
            "date": "2026-04-07",
            "duration_minutes": 41,
            "participants": [
                "Dan Vogt (Figma Platform)", "Rachel Torres (Figma PM)", "Sarah Kim (ElevenLabs)"
            ],
            "summary": "Figma platform team is evaluating voice annotation for FigJam. "
                       "They have an internal Whisper integration built by a contractor "
                       "but it's unmaintained and breaks on non-English input. "
                       "Rachel wants multilingual support (their user base is 40% non-English). "
                       "Dan is worried about integration complexity with their design tokens pipeline "
                       "— they have a custom component ID system that needs to map to transcript segments.",
            "objections": [
                {
                    "text": "Our design tokens pipeline has a custom component tagging system. "
                            "We need transcript segments to reference component IDs, not just timestamps. "
                            "Does your API support custom metadata per audio segment?",
                    "category": "technical",
                    "severity": "high",
                },
                {
                    "text": "We already have an internal Whisper integration. "
                            "The cost of migrating our annotation data format "
                            "might outweigh the benefits unless the quality gap is significant.",
                    "category": "switching_cost",
                    "severity": "medium",
                },
            ],
            "next_steps": [
                "Send word-level timestamp + custom metadata docs to Dan Vogt",
                "Set up a multilingual accuracy comparison — EN, DE, JP, FR (their top 4 locales)",
                "Sarah to propose a co-build: ElevenLabs handles transcription, "
                "Figma owns the component tagging layer via our custom segment metadata",
            ],
            "competitive_mentions": ["Gemini", "Whisper"],
            "talk_time_ratio": {"rep": 0.36, "prospect": 0.64},
            "sentiment": "engaged",
        },
        "slack_mentions": [
            {
                "from": "Sarah Kim",
                "channel": "#deals-midmarket",
                "text": "Figma follow-up is next week but Dan asked a follow-up question "
                        "about segment metadata. Sent the docs — waiting on their response.",
                "ts": "2026-04-12T11:30:00Z",
            },
        ],
        "outreach": {
            "sequence": "Mid-Market — Platform/Technical",
            "emails_sent": 5,
            "open_rate": 0.8,
            "reply_rate": 0.6,
            "last_touch": "2026-04-12",
            "last_touch_type": "email — sent word-level timestamp + metadata API docs",
            "next_step_in_sequence": "Technical deep-dive scheduled 2026-04-22",
        },
        "wiki_playbook": {
            "segment": "Mid-Market",
            "talk_track": (
                "The Figma deal is a build-vs-buy battle. "
                "Their internal Whisper integration is fragile and non-English support is broken — "
                "that's your opening. Lead with the multilingual accuracy comparison. "
                "On the component tagging question: our custom segment metadata field "
                "solves this exactly — show the docs, don't describe them. "
                "The co-build framing is the right close: "
                "'You own the Figma layer, we own the voice layer.' "
                "Keeps their platform team in control, reduces switching anxiety."
            ),
            "competitive_responses": {
                "Gemini": (
                    "Gemini Speech-to-Text doesn't have word-level timestamps or "
                    "custom segment metadata. For Figma's use case — "
                    "pinning transcript segments to component IDs — "
                    "they'd have to build that layer themselves. "
                    "ElevenLabs gives them that out of the box."
                ),
                "Whisper": (
                    "Their Whisper integration is already broken on non-English. "
                    "That's not a Whisper problem, it's a maintenance problem — "
                    "self-hosted models need a team to run. "
                    "ElevenLabs is a managed endpoint. No model updates to chase, "
                    "no infra to manage, no contractor dependency."
                ),
            },
            "discovery_questions": [
                "How often do non-English voice annotations break in your current system?",
                "What's the annotation data format today — can we see a sample?",
                "Who would own the ElevenLabs integration on the Figma platform team?",
            ],
        },
    },

    "vercel": {
        "sf_profile": {
            "company": "Vercel",
            "arr": 45_000,
            "plan": "Business",
            "stage": "Proposal",
            "next_renewal": "2026-08-01",
            "owner": "Alex Rivera",
            "industry": "Developer Infrastructure",
            "employees": 350,
            "hq": "San Francisco, CA",
            "website": "vercel.com",
            "notes": "Vercel wants to add voice input to their AI SDK. "
                     "Use case: developers building voice-enabled Next.js apps "
                     "get a drop-in `useVoice()` hook backed by ElevenLabs. "
                     "Price is the main concern — they want to resell to their users "
                     "and the unit economics need to work at scale.",
        },
        "gong_last_call": {
            "date": "2026-04-09",
            "duration_minutes": 35,
            "participants": ["Leah Park (Vercel AI SDK)", "Alex Rivera (ElevenLabs)"],
            "summary": "Leah runs the Vercel AI SDK team. They want to ship a `useVoice()` hook "
                       "for Next.js developers in their v4 release (target: June). "
                       "The integration is technically straightforward — "
                       "they just wrap our streaming endpoint. "
                       "The blocker is pricing: at 10M+ audio minutes/month "
                       "(their projected scale from SDK adoption), "
                       "the per-minute rate makes the unit economics tight for their free tier.",
            "objections": [
                {
                    "text": "Our free tier users generate a lot of audio minutes — "
                            "mostly short interactions under 30 seconds. "
                            "At scale that's 10-15M minutes/month. "
                            "The per-minute pricing at that volume would cost us "
                            "more than we charge our Pro users. We need a flat-rate or reseller model.",
                    "category": "pricing",
                    "severity": "high",
                },
                {
                    "text": "We need the hook to work offline for edge deployments. "
                            "Is there a way to cache or pre-generate common responses?",
                    "category": "technical",
                    "severity": "low",
                },
            ],
            "next_steps": [
                "Bring in partnerships team to discuss reseller/OEM pricing model",
                "Send Leah the edge caching architecture doc — "
                "pre-generation is supported for static responses",
                "Get a draft reseller agreement to Leah by April 18",
            ],
            "competitive_mentions": ["Gemini"],
            "talk_time_ratio": {"rep": 0.43, "prospect": 0.57},
            "sentiment": "positive",
        },
        "slack_mentions": [
            {
                "from": "Alex Rivera",
                "channel": "#deals-smb",
                "text": "Vercel proposal is pending partnerships signing off on reseller terms. "
                        "Leah's June deadline is real — they're cutting the AI SDK v4 release plan "
                        "next week and need to know if we're in it.",
                "ts": "2026-04-13T15:00:00Z",
            },
        ],
        "outreach": {
            "sequence": "SMB — Developer Platform / Partnership Track",
            "emails_sent": 6,
            "open_rate": 1.0,
            "reply_rate": 0.83,
            "last_touch": "2026-04-13",
            "last_touch_type": "email — sent draft reseller agreement for review",
            "next_step_in_sequence": "Awaiting partnerships team sign-off on reseller terms",
        },
        "wiki_playbook": {
            "segment": "SMB",
            "talk_track": (
                "Vercel is a partnerships deal, not a straight software sale. "
                "Per-minute pricing doesn't work at SDK-adoption scale. "
                "The right frame is OEM: Vercel bundles ElevenLabs, "
                "we give them a flat monthly rate, they handle user billing. "
                "Everyone wins: we get distribution, they get a voice story for v4. "
                "June is a hard deadline — if this slips past May, they'll ship without us "
                "and we lose the SDK slot for 12 months."
            ),
            "competitive_responses": {
                "Gemini": (
                    "Google has a preferred vendor relationship with Vercel for AI features. "
                    "The risk is real. Counter: ElevenLabs is voice-native — "
                    "Google's speech API is general-purpose. "
                    "For a `useVoice()` hook that developers actually want to use, "
                    "the quality gap is audible in a 10-second demo. "
                    "Offer to co-present a side-by-side demo to their SDK team."
                ),
            },
            "discovery_questions": [
                "What's the projected monthly active users for the AI SDK v4 at launch?",
                "Is the free tier voice usage subsidized by Vercel or passed to the user?",
                "Who on your team owns the vendor contracts for the AI SDK dependencies?",
            ],
        },
    },
}


def get_company(name: str) -> dict | None:
    """Case-insensitive company lookup."""
    return COMPANIES.get(name.lower())


def list_companies() -> list[str]:
    return list(COMPANIES.keys())


# Which companies have meetings today
TODAY_MEETINGS = ["notion", "deutsche telekom", "linear"]
