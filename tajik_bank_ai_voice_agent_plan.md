# AI Voice Agent for Bank Collections & Sales (Tajikistan)
### Startup Plan — Built on Claude + ElevenLabs

---

## 1. Executive Summary

The business: an AI voice agent that places outbound phone calls to bank clients in Tajik, handling two distinct use cases —

1. **Collections** — reminding, negotiating, and securing payment promises from delinquent borrowers.
2. **Sales / cross-sell** — offering existing customers new products (cards, loans, insurance, savings accounts) to grow the bank's product-per-client ratio.

Built on: **ElevenLabs** (speech-to-text via Scribe, text-to-speech for the voice), **Claude** (conversation logic, reasoning, script adherence), and a telephony layer to actually place/receive calls.

**Core risk to solve first:** whether Tajik voice quality (especially TTS/voice generation) is natural enough for a regulated, trust-sensitive conversation like debt collection. This should be validated before any further investment.

---

## 2. Technical Feasibility Notes (from research)

- **Speech-to-text (Scribe):** Tajik is supported at a "Good" accuracy tier (roughly 10–25% word error rate). This is workable but not top-tier — expect more errors on numbers, names, and noisy phone-line audio than you'd get with a high-resource language. Budget time for testing on real financial vocabulary (amounts, dates, account terms).
- **Text-to-speech:** Tajik was not confirmed among ElevenLabs' core high-quality voice-generation languages. Two fallback paths if native Tajik TTS quality is weak:
  - Use a **custom/cloned voice** trained on Tajik speech samples (requires sourcing a voice actor and consent/licensing).
  - Pilot in **Russian** first, which is widely used and well understood in Tajik banking/finance contexts, while continuing to develop Tajik voice quality in parallel.
- **Recommendation:** Do not commit to a full build until you've run a real proof-of-concept call end-to-end and had native speakers rate it (see Phase 1 below).

---

## 3. Regulatory & Compliance Foundation (do this first)

This is the highest-risk part of the business, not the technology. Address before any client data touches the system.

- Engage a local lawyer or compliance consultant to confirm, for **collections calls**:
  - Required opening disclosures (who is calling, on whose behalf, purpose of the call)
  - Permitted calling hours/frequency and rules against harassment
  - Recording and consent requirements
  - How disputes and hardship claims must be handled (must escalate to a human — an AI should never unilaterally negotiate final settlement terms without human sign-off, depending on local rules)
- For **sales calls**:
  - Opt-out / do-not-call handling
  - Rules against misrepresenting product terms (rates, fees, conditions)
  - Data protection requirements for using client financial data in outbound sales
- Draft **compliance-approved script skeletons** for both use cases before writing any AI prompts. These become hard guardrails the AI must never deviate from — not just guidance, but the literal boundary of what the AI is allowed to say.
- Define **human-escalation triggers** up front: hardship claims, disputes, requests for a human, complaints, mentions of self-harm or crisis, and any negotiation beyond pre-approved parameters.

---

## 4. Phase 1 — Proof of Concept (2–3 weeks)

Goal: prove the voice quality and conversation logic work before building anything permanent.

1. Record or role-play 5–10 minutes of realistic Tajik collections and sales conversations.
2. Run audio through ElevenLabs Scribe → evaluate transcription accuracy specifically on financial vocabulary (amounts, dates, account numbers, names).
3. Feed transcripts to Claude with a draft system prompt (persona, tone, escalation rules, compliance script skeleton) → generate candidate responses.
4. Convert responses to speech via ElevenLabs → assess naturalness.
5. Have 3–5 native Tajik speakers — ideally including a contact from your target banks — rate: naturalness, clarity, and whether the tone feels appropriate for a debt conversation specifically (this matters more than for sales; a robotic or overly aggressive collections tone creates real reputational and legal risk).

**Decision gate:** If Tajik TTS quality is insufficient, pilot in Russian first while solving Tajik voice quality in parallel, rather than delaying launch entirely.

---

## 5. Phase 2 — MVP Architecture

**Core pipeline:**

```
Telephony (SIP / PBX / telephony API)
    → ElevenLabs Scribe (speech-to-text)
    → Claude (dialogue logic, script adherence, escalation detection)
    → ElevenLabs (text-to-speech)
    → back to caller
```

**Key components:**

- **Guardrail layer:** a structured prompt / state machine that constrains Claude to the compliance-approved script — it should never freelance on interest rates, settlement terms, or legally sensitive language. This is what makes the system compliant, not just fluent.
- **Call logging & transcript storage:** full audit trail of every call, required for bank compliance sign-off and dispute resolution.
- **Live-agent handoff:** warm transfer to a human agent with call context passed along, triggered automatically by the escalation rules defined in Phase 0.
- **Dashboard:** call outcomes, promises-to-pay, escalation rate, sales conversions — built incrementally, only once there's real call volume to show.

**Build sequence (solo-friendly):**
1. Single-call CLI prototype (no telephony yet — test the AI pipeline in isolation)
2. Phone-connected pilot with one bank contact / test line
3. Dashboard and reporting layer once real call data exists

---

## 6. Phase 3 — Pilot

- Convert existing informal bank interest into a **small, low-risk pilot**: 50–100 outbound calls on a low-stakes segment first — e.g., early-stage delinquency reminders (not hard collections), or cross-sell to already-satisfied customers (not complex new products).
- Get the bank's compliance/legal team to sign off on scripts before any real client is called.
- Track from day one: contact rate, promise-to-pay rate, escalation/handoff rate, call abandonment, customer complaints, and (for sales) conversion rate. Banks will want ROI evidence, not a demo.

---

## 7. Business Model

- **Pricing options:** per-successful-call, per-minute, or outcome-based (fee per recovered payment / per product sold). Outcome-based pricing is the easiest first sale — it de-risks the bank's spend and aligns incentives.
- **Positioning:** frame the product as augmenting human agents — handling high-volume, low-complexity calls and freeing staff for complex/sensitive cases — rather than replacing them. This is both more accurate and reduces internal resistance at the bank.

---

## 8. Immediate Next Steps

1. This week: run the Phase 1 proof-of-concept — this determines whether the entire approach is viable.
2. In parallel: get a compliance consultation started (even a few hours) so script guardrails are ready before the technical MVP needs them.
3. Once voice quality is validated: draft the two compliance-approved script skeletons (collections, sales).
4. Approach your existing bank contact with a concrete, small-scope pilot proposal (50–100 calls, low-stakes segment) rather than a broad pitch.

---

*Prepared as a planning document — compliance details should be confirmed with a Tajikistan-qualified lawyer before deployment with real client data.*
