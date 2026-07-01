"""
Dialogue engine — the "brain" of the voice agent.

CTO note: This wraps a locally-hosted open-source LLM (via Ollama) with a
compliance guardrail. The design principle is that the model handles NATURAL
CONVERSATION, but a deterministic layer around it enforces the rules. We never
trust the model alone to remember a legal boundary — we structure the prompt
from the audited config, and we run an escalation check on every recipient turn.

Open-source stack, self-hosted, no third-party API calls with client data:
  - LLM: any open-weight chat model served by Ollama (https://ollama.com),
    e.g. "llama3.1:8b" or "qwen2.5:7b". Pull it once with
    `ollama pull llama3.1:8b`, then `ollama serve` runs the local HTTP API
    this module talks to. No API key, no data leaving the bank's network.

Flow of one turn:
  1. Recipient says something (text now; transcribed speech later).
  2. Escalation check: does this turn trip a compliance trigger? If yes -> hand off.
  3. If safe, the model generates the next line, constrained by the system
     prompt built from the approved script skeleton.
  4. Return the agent's line (text now; sent to TTS later).
"""

import json

import requests

from config.settings import (
    OLLAMA_HOST, OLLAMA_MODEL, ACTIVE_LANGUAGE, COMPLIANCE,
)
from config.scripts import SCRIPTS


class EscalationRequired(Exception):
    """Raised when the conversation must be handed to a human agent."""
    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(f"Escalation: {reason} — {detail}")


class DialogueEngine:
    def __init__(self, flow: str, call_context: dict):
        """
        flow: "collections" or "sales"
        call_context: the per-call variables that fill the script, e.g.
            {
              "bank_name": "...", "client_name": "...", "amount": "...",
              "due_date": "...", "product_name": "...", ...
            }
        Only the bank supplies real client data. The agent never invents it.
        """
        self.flow = flow
        self.ctx = call_context
        self.script = SCRIPTS[flow][ACTIVE_LANGUAGE]
        if self.script is None:
            raise ValueError(
                f"No script for flow='{flow}' language='{ACTIVE_LANGUAGE}'. "
                f"Add and compliance-review the translation first."
            )
        self.history = []   # list of {"role": "user"/"assistant", "content": ...}

    # ------------------------------------------------------------------ #
    # OLLAMA CALL — thin wrapper around the local /api/chat endpoint.
    # ------------------------------------------------------------------ #
    def _chat(self, messages: list) -> str:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "").strip()

    # ------------------------------------------------------------------ #
    # SYSTEM PROMPT — built from the audited config, not free-written.
    # ------------------------------------------------------------------ #
    def _system_prompt(self) -> str:
        s = self.script
        # Fill script fields with call context where present.
        def fill(text):
            try:
                return text.format(**self.ctx)
            except KeyError:
                return text  # leave placeholders if context missing; safer than crashing

        allowed = "\n".join(f"  - {fill(t)}" for t in s["allowed_topics"])
        forbidden = "\n".join(f"  - {fill(t)}" for t in s["forbidden"])

        return f"""You are a professional, calm, and respectful automated voice assistant making an outbound phone call on behalf of a bank. You speak naturally, like a courteous human agent — never robotic, never aggressive, never pushy.

REQUIRED OPENING (say this at the start, naturally):
{fill(s['opening_disclosure'])}

YOUR OBJECTIVE:
{fill(s['objective'])}

YOU MAY discuss ONLY these topics:
{allowed}

YOU MUST NEVER do the following:
{forbidden}

CRITICAL RULES:
- Keep responses SHORT and conversational — this is a phone call, not an essay. One or two sentences per turn.
- Only state facts (amounts, dates, product terms) that appear in this prompt or that the person confirms. Never invent financial figures, rates, or terms.
- If the person disputes anything, claims hardship, asks for a human, complains, threatens legal action, seems distressed, or says they are not the right person — do NOT try to handle it. Respond briefly and indicate you'll connect them to a specialist.
- Be warm and human. Listen to what they actually say and respond to it.

CLOSING (when the objective is met, say naturally):
{fill(s['closing'])}
"""

    # ------------------------------------------------------------------ #
    # ESCALATION CHECK — runs on every recipient turn.
    # Uses the same local model as a fast classifier against the audited
    # trigger list. Smaller open-weight models are less reliable at strict
    # JSON formatting than a frontier hosted model, so the fail-safe parse
    # fallback below matters even more here.
    # ------------------------------------------------------------------ #
    def _check_escalation(self, recipient_text: str):
        triggers = ", ".join(COMPLIANCE.escalation_triggers)
        prompt = f"""You are a compliance classifier for a bank collections/sales call.
Analyze this statement from the call recipient and decide if it trips any escalation trigger that requires handing the call to a human agent.

Triggers to detect: {triggers}

Recipient said: "{recipient_text}"

Respond with ONLY a JSON object, no other text:
{{"escalate": true/false, "trigger": "<trigger name or empty>", "reason": "<brief explanation>"}}"""

        raw = self._chat([{"role": "user", "content": prompt}])
        raw = raw.replace("```json", "").replace("```", "").strip()
        try:
            verdict = json.loads(raw)
        except json.JSONDecodeError:
            # Fail SAFE: if we can't parse the classifier, escalate to a human.
            raise EscalationRequired("classifier_error", raw)

        if verdict.get("escalate"):
            raise EscalationRequired(
                verdict.get("trigger", "unknown"),
                verdict.get("reason", ""),
            )

    # ------------------------------------------------------------------ #
    # MAIN TURN
    # ------------------------------------------------------------------ #
    def opening_line(self) -> str:
        """The agent speaks first. Generate the compliant opening."""
        messages = [
            {"role": "system", "content": self._system_prompt()},
            {"role": "user",
             "content": "[CALL CONNECTED] Begin the call now with your required opening."},
        ]
        line = self._chat(messages)
        self.history.append({"role": "user", "content": "[CALL CONNECTED]"})
        self.history.append({"role": "assistant", "content": line})
        return line

    def respond_to(self, recipient_text: str) -> str:
        """
        Process one recipient utterance and return the agent's reply.
        Raises EscalationRequired if the call must go to a human.
        """
        # 1. Compliance gate BEFORE generating any reply.
        self._check_escalation(recipient_text)

        # 2. Safe — generate the next line in context.
        self.history.append({"role": "user", "content": recipient_text})
        messages = [{"role": "system", "content": self._system_prompt()}] + self.history
        line = self._chat(messages)
        self.history.append({"role": "assistant", "content": line})
        return line
