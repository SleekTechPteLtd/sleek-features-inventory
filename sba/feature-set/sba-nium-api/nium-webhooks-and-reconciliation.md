# NIUM webhooks and reconciliation reporting

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | NIUM webhooks and reconciliation reporting |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | NIUM |
| **Business Outcome** | Keeps card and transaction state in sync via 20+ webhook types and Kafka-backed reconciliation. |
| **Entry Point / Surface** | Webhook handlers on `sba-nium-api`; Kafka consumers |
| **Short Description** | Processes customer, card, transaction, wallet/3DS events; maps NIUM statuses to SBA; feeds reporting. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Kafka cluster |
| **Service / Repository** | sba-nium-api |
| **DB - Collections** | MongoDB |
| **Evidence Source** | README Webhook System and Reporting |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `README.md` — Webhook event list; Kafka-based processing.
