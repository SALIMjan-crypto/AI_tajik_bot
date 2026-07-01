# AI Voice Agent for Bank Collections & Sales — Build Roadmap & Product Passport

---

# PART 1 — BUILD ROADMAP

Timeline assumes a solo builder working with informal bank contacts, moving toward a signed pilot. Adjust pace to your availability — this is sequenced by dependency, not calendar weeks, so don't rush a phase before its gate is cleared.

## Month 1 — Foundation & Feasibility

| Week | Focus | Deliverable | Gate to pass |
|---|---|---|---|
| 1 | Compliance groundwork | Initial consultation with lawyer/compliance advisor; list of hard rules for collections & sales calls | Written summary of legal constraints |
| 1–2 | Voice proof-of-concept | End-to-end test call: Scribe (STT) → Claude → ElevenLabs (TTS) | Native speakers rate output "usable" |
| 2 | Voice quality decision | Choose: native Tajik voice, cloned/custom voice, or Russian-first pilot | Documented decision + fallback plan |
| 3–4 | Compliance script skeletons | Draft compliant scripts for collections (delinquency reminder tier) and sales (cross-sell to existing customers) | Scripts reviewed by compliance advisor |

**Exit criterion for Month 1:** you know, with evidence, whether the voice is good enough and what you're legally allowed to have it say.

## Month 2 — MVP Build

| Week | Focus | Deliverable |
|---|---|---|
| 5 | Core pipeline (no telephony yet) | CLI prototype: text/audio in → Claude logic → audio out |
| 6 | Guardrail layer | Prompt/state-machine constraining Claude to script boundaries; escalation-trigger detection |
| 7 | Telephony integration | Outbound calling connected via SIP/telephony API to a test number |
| 8 | Logging & handoff | Call recording, transcript storage, live-agent warm-transfer mechanism |

**Exit criterion for Month 2:** you can place one real outbound call, on script, with a working human-handoff path, and a saved transcript.

## Month 3 — Controlled Pilot

| Week | Focus | Deliverable |
|---|---|---|
| 9 | Bank sign-off | Compliance/legal approval of scripts and data-handling from pilot bank |
| 9–10 | Small batch pilot | 50–100 calls on low-stakes segment (early delinquency reminders or cross-sell to satisfied customers) |
| 11 | Metrics review | Contact rate, promise-to-pay rate, escalation rate, complaints, conversion rate |
| 12 | Iterate | Refine scripts, prompt, escalation thresholds based on pilot data |

**Exit criterion for Month 3:** a documented pilot result you can show a second bank — real numbers, not projections.

## Month 4+ — Scale Decision

- If pilot metrics are strong: negotiate a paid contract (outcome-based pricing recommended for first paid deal), build the reporting dashboard, expand call volume.
- If pilot metrics are weak: diagnose whether the gap is voice quality, script design, or targeting — don't scale a broken conversation.
- Begin evaluating a second bank client once the first has a signed, paying relationship — proof with one real client is your strongest sales asset.

---

# PART 2 — PRODUCT PASSPORT

*A formal reference document summarizing the product for internal use, investor/partner review, or regulatory submission.*

| Field | Detail |
|---|---|
| **Product name** | AI Voice Agent for Bank Collections & Sales (working title) |
| **Product type** | Conversational AI voice service (outbound calling) |
| **Core technology stack** | ElevenLabs (Scribe — speech-to-text; TTS — speech generation), Claude (Anthropic) — conversational reasoning and script logic, telephony/SIP layer for call delivery |
| **Primary market** | Commercial banks and microfinance institutions in Tajikistan |
| **Use case 1** | Debt collections — automated outbound calls to delinquent borrowers for reminders, negotiation within pre-approved parameters, and payment-promise capture |
| **Use case 2** | Product sales / cross-sell — automated outbound calls offering existing bank customers additional products (cards, loans, insurance, savings) |
| **Primary language** | Tajik (with Russian as a validated fallback pending Tajik voice-quality confirmation) |
| **Target users (client-side)** | Bank collections departments, bank sales/marketing departments |
| **End users (call recipients)** | Bank retail/individual clients |
| **Key functional components** | Speech-to-text transcription; AI-driven dialogue within a compliance-constrained script; text-to-speech voice response; automated escalation to human agents; call logging and transcript audit trail; outcome tracking (payment promises, sales conversions) |
| **Compliance basis** | Governed by National Bank of Tajikistan consumer protection and collections-conduct rules (to be formally confirmed with local legal counsel); requires documented consent/recording practices, disclosure scripts, and human-escalation protocols for disputes and hardship claims |
| **Data handled** | Client name, contact number, account/loan status, payment history, call recordings and transcripts — all treated as sensitive financial personal data requiring bank-grade data protection |
| **Escalation triggers** | Dispute of debt validity, hardship claim, explicit request for a human agent, complaint, any negotiation outside pre-approved parameters, indications of crisis or distress |
| **Success metrics (collections)** | Contact rate, promise-to-pay rate, escalation rate, complaint rate, cost per successful contact |
| **Success metrics (sales)** | Contact rate, offer-acceptance/conversion rate, escalation rate, complaint rate, cost per conversion |
| **Pricing model (proposed)** | Outcome-based: fee per confirmed payment promise / per completed sale (preferred for first pilot); alternative per-call or per-minute pricing for later contracts |
| **Current stage** | Pre-MVP — feasibility validation in progress; informal bank interest established, no signed pilot yet |
| **Known risks** | Tajik voice-generation quality unconfirmed at native level; regulatory requirements not yet formally confirmed with counsel; reputational risk from poor-quality collections conversations; dependency on third-party AI/voice providers' language support |
| **Version** | v0.1 — planning stage |
| **Document owner** | [Your name / company name] |
| **Last updated** | [Insert date at time of use] |

---

*This document is a planning and reference tool. Formal regulatory or legal claims within it (compliance basis, data handling requirements) should be verified and finalized with a Tajikistan-qualified legal/compliance advisor before submission to any bank, regulator, or investor.*
