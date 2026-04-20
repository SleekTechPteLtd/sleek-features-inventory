# Inbound webhooks and callbacks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Inbound webhooks and callbacks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | External banks / NIUM / internal systems |
| **Business Outcome** | Receives asynchronous status updates (payments, cards, payouts) and normalizes them into SBA state and notifications. |
| **Entry Point / Surface** | Webhook routes on `sba-bank-api` (see v2 `webhook-controller`) |
| **Short Description** | Webhook controller delegates to webhook services; validates signatures/headers per integration; may update Mongo and emit further events. |
| **Variants / Markets** | Per-vendor webhook contracts |
| **Dependencies / Related Flows** | Downstream DBS / NIUM webhook endpoints on vendor services |
| **Service / Repository** | sba-bank-api |
| **DB - Collections** | |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Full inventory of webhook paths per vendor |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `src/v2/controllers/webhook-controller` — inbound webhook surface.
