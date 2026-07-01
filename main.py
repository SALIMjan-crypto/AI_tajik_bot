"""
RUNNABLE PROTOTYPE — text version of the voice agent.

CTO note: This is the safe way to validate conversation logic and compliance
guardrails WITHOUT calling anyone. You type the recipient's side; the agent
responds exactly as it would on a real call. Once we're happy with the behavior
here, the same DialogueEngine drops straight into the telephony pipeline —
we only swap "typed text" for "transcribed speech" and "printed text" for
"spoken audio".

Run:
    export ANTHROPIC_API_KEY="sk-ant-..."
    cd voiceagent
    python main.py

Then choose a flow and have a conversation as if you were the bank client.
Type 'quit' to end.
"""

import sys

from config.settings import FLOW_COLLECTIONS, FLOW_SALES, ACTIVE_LANGUAGE
from core.dialogue_engine import DialogueEngine, EscalationRequired
from core.call_log import CallLog


# Sample call context. In production, the bank's system supplies these per call.
SAMPLE_CONTEXT = {
    FLOW_COLLECTIONS: {
        "bank_name": "Example Bank",
        "client_name": "Mr. Rahimov",
        "amount": "1,200 somoni",
        "due_date": "15 June",
        "promise_date": "[to be captured]",
    },
    FLOW_SALES: {
        "bank_name": "Example Bank",
        "client_name": "Mr. Rahimov",
        "product_name": "a premium savings account with a higher interest rate",
        "followup_line": "A specialist will contact you with the details.",
    },
}


def run():
    print("=" * 60)
    print(" AI VOICE AGENT — TEXT PROTOTYPE")
    print(f" Language: {ACTIVE_LANGUAGE}")
    print("=" * 60)
    print(" 1) Collections (overdue payment reminder)")
    print(" 2) Sales (cross-sell to existing customer)")
    choice = input(" Choose flow [1/2]: ").strip()

    flow = FLOW_COLLECTIONS if choice == "1" else FLOW_SALES
    ctx = SAMPLE_CONTEXT[flow]

    engine = DialogueEngine(flow=flow, call_context=ctx)
    log = CallLog(flow=flow, call_context=ctx)

    print("\n--- CALL STARTED ---\n")

    # Agent speaks first.
    opening = engine.opening_line()
    print(f"AGENT: {opening}\n")
    log.record("agent", opening)

    # Conversation loop.
    while True:
        recipient = input("YOU (recipient): ").strip()
        if recipient.lower() in ("quit", "exit"):
            log.set_outcome("ended_by_tester")
            break

        log.record("recipient", recipient)

        try:
            reply = engine.respond_to(recipient)
            print(f"\nAGENT: {reply}\n")
            log.record("agent", reply)
        except EscalationRequired as e:
            print(f"\n[!] ESCALATION TRIGGERED: {e.reason} — {e.detail}")
            print("[!] In a real call, the recipient would now be warm-transferred")
            print("    to a human agent with full context. Ending AI portion.\n")
            log.mark_escalated(f"{e.reason}: {e.detail}")
            break

    path = log.save()
    print("--- CALL ENDED ---")
    print(f"Transcript saved: {path}")
    if log.escalated:
        print(f"Outcome: escalated ({log.escalation_reason})")
    else:
        print(f"Outcome: {log.outcome}")


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)
