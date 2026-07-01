"""
Central configuration for the AI Voice Agent.

CTO note: Everything that a compliance officer or a non-engineer might need to
review or change lives here — call hours, escalation triggers, disclosures,
negotiation limits. Keep business rules OUT of the model prompt and IN this file
so they can be audited and changed without touching AI behavior.
"""

import os
from dataclasses import dataclass, field
from typing import List

# ---------------------------------------------------------------------------
# API KEYS — loaded from environment. Never hardcode. Never commit real keys.
#   export ANTHROPIC_API_KEY="sk-ant-..."
#   export ELEVENLABS_API_KEY="..."
# ---------------------------------------------------------------------------
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

# Model selection
CLAUDE_MODEL = "claude-sonnet-4-6"   # fast + capable; good for real-time dialogue

# ---------------------------------------------------------------------------
# LANGUAGE
#   Swap this to run the same logic in a different language.
#   "en" for logic validation, "ru" for the validated fallback, "tg" for Tajik.
# ---------------------------------------------------------------------------
ACTIVE_LANGUAGE = "en"   # options: "en", "ru", "tg"

# ---------------------------------------------------------------------------
# COMPLIANCE RULES  — REVIEW WITH LEGAL COUNSEL BEFORE PRODUCTION
#   These are placeholders based on typical collections-conduct norms.
#   A Tajikistan-qualified advisor must confirm/replace these values.
# ---------------------------------------------------------------------------
@dataclass
class ComplianceConfig:
    # Permitted calling window (24h local time). Outside this => do not call.
    call_hours_start: int = 9      # 09:00
    call_hours_end: int = 20       # 20:00

    # Max contact attempts per client per week (anti-harassment)
    max_weekly_contacts: int = 3

    # The agent must NEVER negotiate below this % of the outstanding balance
    # without human sign-off. Set to 100 = agent cannot discount at all.
    min_settlement_pct: int = 100

    # Every call must open by identifying caller, principal, and purpose.
    require_opening_disclosure: bool = True

    # Every call is recorded; recipient must be informed.
    require_recording_notice: bool = True

    # Phrases/intents that force an immediate handoff to a human agent.
    # Detection is handled semantically by Claude, but these anchor the intent.
    escalation_triggers: List[str] = field(default_factory=lambda: [
        "dispute",                 # recipient disputes the debt is valid/theirs
        "hardship",                # financial hardship / cannot pay / lost job
        "request_human",           # explicitly asks for a person
        "complaint",               # complaint about the bank or the call
        "legal_threat",            # mentions lawyer / legal action
        "distress",                # signs of crisis / emotional distress
        "identity_uncertain",      # wrong person / not the account holder
        "out_of_scope_negotiation" # asks for terms beyond pre-approved limits
    ])

COMPLIANCE = ComplianceConfig()

# ---------------------------------------------------------------------------
# CALL FLOW TYPES
# ---------------------------------------------------------------------------
FLOW_COLLECTIONS = "collections"
FLOW_SALES = "sales"
