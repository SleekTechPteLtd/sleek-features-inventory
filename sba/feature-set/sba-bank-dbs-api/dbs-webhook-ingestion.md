# DBS webhook ingestion

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | DBS webhook ingestion |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | DBS |
| **Business Outcome** | Applies DBS push notifications for transaction and account events without polling. |
| **Entry Point / Surface** | Webhook routes on `sba-bank-dbs-api` |
| **Short Description** | Webhook controller validates and forwards to webhook service for persistence and downstream signalling. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | May correlate with sba-bank-api consumers |
| **Service / Repository** | sba-bank-dbs-api |
| **DB - Collections** | |
| **Evidence Source** | `src/v2/controllers/webhook-controller` |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `src/v2/controllers/webhook-controller`, `src/v2/services/webhook-service`.
