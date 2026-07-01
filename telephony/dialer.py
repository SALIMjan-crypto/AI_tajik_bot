"""
TELEPHONY LAYER — the real-time call loop (integration scaffold).

CTO note: This is deliberately a SCAFFOLD, not a finished integration, because
the concrete code depends on which telephony provider we pick and — critically —
on having a bank's compliance sign-off before any real number is dialed. It shows
exactly how the pieces connect so that wiring a provider in is a small, bounded task.

DECISION PENDING (CTO): telephony provider selection. Requirements:
  - Can originate outbound calls to Tajikistan mobile/landline numbers
  - Streams audio in/out in real time (media streams / WebRTC / SIP)
  - Lets us bridge/transfer a live call to a human agent (for escalation)
  - Acceptable per-minute cost at pilot volume
Common options to evaluate: Twilio, Vonage, Telnyx, or a local Tajik SIP provider
(a local provider may be cheaper and more reliable for TJ termination — evaluate).

The real-time loop, once a provider is chosen:

    on_call_answered(call):
        engine = DialogueEngine(flow, call_context_for_this_client)
        log = CallLog(flow, call_context_for_this_client)

        # Agent speaks first
        opening = engine.opening_line()
        play_audio(call, synthesize(opening))
        log.record("agent", opening)

        while call.active:
            audio = record_until_silence(call)     # provider gives us caller audio
            recipient_text = transcribe(audio)      # voice.py -> Scribe
            log.record("recipient", recipient_text)

            try:
                reply = engine.respond_to(recipient_text)
            except EscalationRequired as e:
                log.mark_escalated(str(e))
                transfer_to_human_agent(call, context=log)   # warm handoff
                break

            play_audio(call, synthesize(reply))     # voice.py -> TTS
            log.record("agent", reply)

            if conversation_complete(reply):
                break

        log.save()

Notes:
  - record_until_silence / play_audio / transfer_to_human_agent are provider-
    specific and implemented against the chosen telephony SDK.
  - Barge-in (letting the caller interrupt the agent) matters for natural feel;
    most providers support it via their media-stream API.
  - DO NOT enable outbound dialing to real client numbers until:
      (a) bank compliance/legal has signed off on scripts + data handling, and
      (b) call hours / consent / do-not-call checks from config are enforced here.
"""

from config.settings import COMPLIANCE
from datetime import datetime
from typing import Optional


def within_permitted_call_hours(now: Optional[datetime] = None) -> bool:
    """Enforce the compliance calling window before dialing. Call this in the
    dialer BEFORE originating any outbound call."""
    now = now or datetime.now()
    return COMPLIANCE.call_hours_start <= now.hour < COMPLIANCE.call_hours_end


# Placeholder signatures — implement against the chosen provider's SDK.
def originate_call(phone_number: str, call_context: dict):
    raise NotImplementedError(
        "Select and integrate a telephony provider. See module docstring. "
        "Do not enable until compliance sign-off is in place."
    )


def transfer_to_human_agent(call, context):
    raise NotImplementedError(
        "Implement warm transfer via the chosen provider, passing call context "
        "to the human agent."
    )
