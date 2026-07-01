"""
Call logging — audit trail for every conversation.

CTO note: Banks and regulators will require a complete, tamper-evident record of
every call: who was called, what was said, the outcome, and any escalation.
This writes a structured JSON transcript per call. In production this goes to a
secure, access-controlled store — not the local disk — and recordings are
retained per the bank's data-retention policy.
"""

import json
import os
from datetime import datetime, timezone


class CallLog:
    def __init__(self, flow: str, call_context: dict, log_dir: str = "call_logs"):
        self.flow = flow
        self.ctx = call_context
        self.turns = []
        self.outcome = None
        self.escalated = False
        self.escalation_reason = None
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def record(self, speaker: str, text: str):
        self.turns.append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "speaker": speaker,   # "agent" or "recipient"
            "text": text,
        })

    def mark_escalated(self, reason: str):
        self.escalated = True
        self.escalation_reason = reason
        self.outcome = "escalated_to_human"

    def set_outcome(self, outcome: str):
        self.outcome = outcome

    def save(self) -> str:
        # Redact the client name in the filename; keep full detail inside the
        # access-controlled record only.
        record = {
            "flow": self.flow,
            "started_at": self.started_at,
            "ended_at": datetime.now(timezone.utc).isoformat(),
            "context": self.ctx,
            "turns": self.turns,
            "outcome": self.outcome,
            "escalated": self.escalated,
            "escalation_reason": self.escalation_reason,
        }
        fname = f"call_{self.flow}_{self.started_at.replace(':', '-')}.json"
        path = os.path.join(self.log_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        return path
