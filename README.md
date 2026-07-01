# AI Voice Agent for Bank Collections & Sales

Conversational AI voice agent for banks: places outbound calls for **collections**
(overdue payment reminders) and **sales** (cross-sell to existing customers), in
Tajik / Russian / English.

Built entirely on **open-source, self-hosted components** — an open-weight LLM
served by **Ollama**, **faster-whisper** for speech-to-text, and **Piper** for
text-to-speech — with a compliance guardrail layer between the AI and the caller.
No per-call API key, and no client conversation data leaves the bank's own
infrastructure.

---

## Status

| Component | State |
|---|---|
| Conversation engine (local LLM via Ollama) | Built & tested |
| Compliance guardrail layer | Built & tested |
| Escalation → human handoff logic | Built & tested |
| Call logging / audit trail | Built |
| Text prototype (no calls) | **Runnable now** (needs Ollama running locally) |
| Voice layer (faster-whisper STT + Piper TTS) | Written — needs voice models downloaded to run |
| Telephony (outbound calling) | Scaffold — needs provider + compliance sign-off |

The self-test (`_selftest.py`) passes with **no LLM, no network call, and no
extra packages installed at all** — it proves the config/scripts/logging/
escalation logic is wired correctly. To have an actual conversation you need
Ollama running with a model pulled.

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
                 │ transcribe() faster-whisper · synthesize() Piper │
                 └───────────────┬─────────────────────────┘
                                 │ text
                                 ▼
   ┌──────────────────────────────────────────────────────────────┐
   │                 DIALOGUE ENGINE (dialogue_engine.py)          │
   │                                                              │
   │   1. Escalation check on EVERY recipient turn (fail-safe)    │
   │   2. Local LLM (via Ollama) generates reply, constrained by..│
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

**Why open-source, self-hosted?** Client financial data and call transcripts
never leave the bank's own servers — nothing is sent to a third-party API.
Also zero marginal per-call cost, and full control over model updates.

---

## Project layout

```
voiceagent/
├── main.py                    # runnable text prototype
├── _selftest.py               # offline logic test (no LLM/model install needed)
├── config/
│   ├── settings.py            # Ollama/Whisper/Piper config, COMPLIANCE RULES ← review w/ legal
│   └── scripts.py             # approved script skeletons per flow/language ← review w/ legal
├── core/
│   ├── dialogue_engine.py     # local LLM (Ollama) + guardrails + escalation
│   ├── voice.py               # faster-whisper STT + Piper TTS
│   └── call_log.py            # audit trail
└── telephony/
    └── dialer.py              # outbound calling scaffold (provider TBD)
```

---

## Quick start (text prototype)

1. Install and start [Ollama](https://ollama.com), then pull a model:

   ```bash
   ollama pull llama3.1:8b
   ollama serve
   ```

2. Install Python deps and run the prototype:

   ```bash
   pip install -r requirements.txt   # only 'requests' is needed for the text prototype
   cd voiceagent
   python main.py
   ```

Choose a flow, then talk to the agent as if you were the bank client. Try saying
"I lost my job" or "this isn't my debt" to see the escalation handoff fire.
Transcripts are written to `call_logs/`.

To verify the logic without Ollama running or any extra packages installed:

```bash
python _selftest.py
```

### Using a different model or host

```bash
export OLLAMA_MODEL="qwen2.5:7b"
export OLLAMA_HOST="http://gpu-box.internal:11434"   # e.g. a shared GPU server
```

---

## Voice layer setup (optional, for real audio)

```bash
pip install faster-whisper piper-tts
```

- **faster-whisper** downloads its model automatically on first use (cached
  locally after that; no audio is sent anywhere at inference time).
- **Piper** needs a voice model per language: download the `.onnx` +
  `.onnx.json` pair for each language from
  [huggingface.co/rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices)
  and point to them via environment variables:

  ```bash
  export PIPER_VOICE_EN=/path/to/en_US-lessac-medium.onnx
  export PIPER_VOICE_RU=/path/to/ru_RU-irina-medium.onnx
  ```

  Piper does not currently ship a native Tajik voice — see the Tajik note
  below for the fallback plan.

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

1. **Validate logic** in the text prototype (done — you can run it now with Ollama).
2. **Set up the voice layer**: download Piper voices and let faster-whisper cache
   its model, test STT/TTS quality on real phone audio. If Tajik TTS quality is
   weak (no native voice ships yet), set `ACTIVE_LANGUAGE="ru"` and pilot in
   Russian while fine-tuning/cloning a Tajik Piper voice from local audio.
3. **Compliance sign-off**: get the bank's legal team to approve `scripts.py` and
   data handling.
4. **Pick a telephony provider** — open-source options include self-hosted
   Asterisk or FreeSWITCH (full control, more ops work) or a managed SIP
   provider — implement the three provider-specific functions in `dialer.py`,
   enforce `within_permitted_call_hours()` before dialing.
5. **Controlled pilot**: 50–100 calls on a low-stakes segment, full logging on.
6. Review metrics, iterate, then scale. Consider a larger/better-tuned open
   model (or a dedicated GPU box) if response quality or latency needs improving.

**Hard gate:** outbound dialing to real client numbers stays disabled until
steps 2–3 are complete. This is intentional and enforced in `dialer.py`.

---

## Security notes

- No third-party API keys are required for the core conversation loop — the
  LLM, STT, and TTS all run on infrastructure the bank controls.
- Call logs contain sensitive financial personal data. In production, write them
  to a secure, access-controlled store (not local disk) with retention per the
  bank's policy, and encrypt at rest and in transit.
- Recordings and transcripts are subject to consent and data-protection rules —
  confirm requirements with counsel.
- Self-hosting shifts responsibility for model security/updates to the bank's
  infra team: keep Ollama, faster-whisper, and Piper patched, and restrict
  network access to the Ollama port (11434) to trusted internal hosts only.
