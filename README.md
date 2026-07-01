# AI Voice Agent for Bank Collections & Sales

Conversational AI voice agent for banks: places outbound calls for **collections**
(overdue payment reminders) and **sales** (cross-sell to existing customers), in
Tajik / Russian / English.

Built on **Claude** (conversation + reasoning) and **ElevenLabs** (speech-to-text
and text-to-speech), with a compliance guardrail layer between the AI and the caller.

---

## Status

| Component | State |
|---|---|
| Conversation engine (Claude) | Built & tested |
| Compliance guardrail layer | Built & tested |
| Escalation → human handoff logic | Built & tested |
| Call logging / audit trail | Built |
| Text prototype (no calls) | **Runnable now** |
| Voice layer (ElevenLabs STT/TTS) | Written — needs API key to run |
| Telephony (outbound calling) | Scaffold — needs provider + compliance sign-off |

The self-test (`_selftest.py`) passes with no API key, proving the logic is wired
correctly. To run the real thing you add your keys.

---

## Architecture

```
                 ┌─────────────────────────────────────────┐
                 │            TELEPHONY LAYER                │  (dialer.py — scaffold)
                 │   originate call · stream audio · transfer│
                 └───────────────┬─────────────────────────┘
                                 │ caller audio
                                 ▼
                 ┌─────────────────────────────────────────┐
                 │          VOICE LAYER (voice.py)           │
                 │   transcribe() Scribe  ·  synthesize() TTS│
                 └───────────────┬─────────────────────────┘
                                 │ text
                                 ▼
   ┌──────────────────────────────────────────────────────────────┐
   │                 DIALOGUE ENGINE (dialogue_engine.py)          │
   │                                                              │
   │   1. Escalation check on EVERY recipient turn (fail-safe)    │
   │   2. Claude generates reply, constrained by ...              │
   │            ▲                                                 │
   │            │ built from                                      │
   │   ┌────────┴─────────┐        ┌──────────────────────────┐   │
   │   │ scripts.py       │        │ settings.py              │   │
   │   │ approved script  │        │ compliance rules:        │   │
   │   │ skeletons        │        │ call hours, triggers,    │   │
   │   │ (per language)   │        │ settlement limits, etc.  │   │
   │   └──────────────────┘        └──────────────────────────┘   │
   └──────────────────────────────┬───────────────────────────────┘
                                  │ every turn logged
                                  ▼
                        ┌───────────────────┐
                        │  call_log.py      │  audit transcript per call
                        └───────────────────┘
```

**Design principle:** the AI handles natural conversation; a deterministic layer
built from an *auditable config* enforces the rules. Business/legal rules live in
`config/`, never inside the model's head. Compliance staff can review and change
them without touching AI code.

---

## Project layout

```
voiceagent/
├── main.py                    # runnable text prototype
├── _selftest.py               # offline logic test (no API key needed)
├── config/
│   ├── settings.py            # API keys, language, COMPLIANCE RULES  ← review w/ legal
│   └── scripts.py             # approved script skeletons per flow/language ← review w/ legal
├── core/
│   ├── dialogue_engine.py     # Claude + guardrails + escalation
│   ├── voice.py               # ElevenLabs STT + TTS
│   └── call_log.py            # audit trail
└── telephony/
    └── dialer.py              # outbound calling scaffold (provider TBD)
```

---

## Quick start (text prototype)

```bash
pip install anthropic requests
export ANTHROPIC_API_KEY="sk-ant-..."

cd voiceagent
python main.py
```

Choose a flow, then talk to the agent as if you were the bank client. Try saying
"I lost my job" or "this isn't my debt" to see the escalation handoff fire.
Transcripts are written to `call_logs/`.

To verify the logic without any key:

```bash
python _selftest.py
```

---

## Configuration you must review before production

Everything a compliance officer needs is in two files:

- **`config/settings.py`** → `COMPLIANCE`: calling hours, max weekly contacts,
  minimum settlement %, escalation triggers, required disclosures.
- **`config/scripts.py`** → the approved opening disclosure, allowed topics,
  forbidden actions, and closing — per flow and per language.

> ⚠️ The compliance values and script language shipped here are **placeholders
> based on typical norms**. A Tajikistan-qualified legal/compliance advisor must
> confirm or replace them before any real client is called.

---

## Path from prototype to live pilot

1. **Validate logic** in the text prototype (done — you can run it now).
2. **Add ElevenLabs key**, plug `voice.py` in, test Tajik STT/TTS quality on real
   phone audio. If Tajik TTS is weak, set `ACTIVE_LANGUAGE="ru"` and pilot in
   Russian while sourcing a cloned Tajik voice.
3. **Compliance sign-off**: get the bank's legal team to approve `scripts.py` and
   data handling.
4. **Pick a telephony provider**, implement the three provider-specific functions
   in `dialer.py`, enforce `within_permitted_call_hours()` before dialing.
5. **Controlled pilot**: 50–100 calls on a low-stakes segment, full logging on.
6. Review metrics, iterate, then scale.

**Hard gate:** outbound dialing to real client numbers stays disabled until
steps 2–3 are complete. This is intentional and enforced in `dialer.py`.

---

## Security notes

- API keys via environment variables only — never commit them.
- Call logs contain sensitive financial personal data. In production, write them
  to a secure, access-controlled store (not local disk) with retention per the
  bank's policy, and encrypt at rest and in transit.
- Recordings and transcripts are subject to consent and data-protection rules —
  confirm requirements with counsel.
