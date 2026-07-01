"""
Offline self-test — proves the logic is wired correctly WITHOUT an API key.

This does not call Claude or ElevenLabs. It checks the parts that don't need
a network call: config loads, script skeletons render for every supported
language/flow, compliance triggers are intact, call logging writes a valid
transcript, and the call-hours gate in the telephony scaffold behaves.

Run:
    python _selftest.py
"""

import os
import shutil
import sys


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    ok = True

    from config.settings import COMPLIANCE, FLOW_COLLECTIONS, FLOW_SALES
    from config.scripts import SCRIPTS

    # --- compliance config sanity ---------------------------------------
    ok &= check(
        "compliance call-hours window is sane",
        0 <= COMPLIANCE.call_hours_start < COMPLIANCE.call_hours_end <= 24,
    )
    ok &= check(
        "escalation triggers are configured",
        len(COMPLIANCE.escalation_triggers) > 0,
    )

    # --- script skeletons render for every implemented language ---------
    sample_ctx = {
        "bank_name": "Example Bank",
        "client_name": "Mr. Rahimov",
        "amount": "1,200 somoni",
        "due_date": "15 June",
        "promise_date": "20 June",
        "product_name": "a premium savings account",
        "followup_line": "A specialist will contact you.",
    }
    for flow in (FLOW_COLLECTIONS, FLOW_SALES):
        for lang, script in SCRIPTS[flow].items():
            if script is None:
                continue  # not yet translated/reviewed (e.g. "tg") — expected
            try:
                script["opening_disclosure"].format(**sample_ctx)
                script["objective"].format(**sample_ctx)
                script["closing"].format(**sample_ctx)
                for t in script["allowed_topics"] + script["forbidden"]:
                    t.format(**sample_ctx)
                rendered = True
            except (KeyError, IndexError):
                rendered = False
            ok &= check(f"script renders: flow={flow} lang={lang}", rendered)

    # --- call logging writes a valid transcript --------------------------
    from core.call_log import CallLog

    tmp_dir = "_selftest_call_logs"
    log = CallLog(flow=FLOW_COLLECTIONS, call_context=sample_ctx, log_dir=tmp_dir)
    log.record("agent", "Hello, this is a test call.")
    log.record("recipient", "Who is this?")
    log.set_outcome("ended_by_tester")
    path = log.save()
    ok &= check("call log file was written", os.path.isfile(path))

    import json
    with open(path, encoding="utf-8") as f:
        saved = json.load(f)
    ok &= check("call log has expected turns", len(saved.get("turns", [])) == 2)
    shutil.rmtree(tmp_dir, ignore_errors=True)

    # --- escalation exception shape ---------------------------------------
    from core.dialogue_engine import EscalationRequired

    try:
        raise EscalationRequired("hardship", "recipient said they lost their job")
    except EscalationRequired as e:
        ok &= check("EscalationRequired carries reason/detail", e.reason == "hardship" and bool(e.detail))

    # --- telephony call-hours gate -----------------------------------------
    from datetime import datetime
    from telephony.dialer import within_permitted_call_hours

    inside = datetime(2026, 1, 1, COMPLIANCE.call_hours_start + 1)
    outside = datetime(2026, 1, 1, (COMPLIANCE.call_hours_end + 1) % 24)
    ok &= check("call-hours gate allows inside window", within_permitted_call_hours(inside))
    ok &= check("call-hours gate blocks outside window", not within_permitted_call_hours(outside))

    print()
    if ok:
        print("ALL CHECKS PASSED — logic is wired correctly. Add API keys to run for real.")
        return 0
    else:
        print("SOME CHECKS FAILED — see above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
