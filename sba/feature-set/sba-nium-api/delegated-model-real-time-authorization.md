# Delegated model (real-time authorization)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Delegated model (real-time authorization) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | NIUM (RHA requests) |
| **Business Outcome** | Approves or declines card transactions within NIUM's timeout using SBA business rules and balance checks. |
| **Entry Point / Surface** | NIUM → `sba-nium-api` authorization endpoints |
| **Short Description** | Implements NIUM Delegated Model: receive authorization payload, evaluate policy, return decision to NIUM. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | sba-bank-api may coordinate customer context; Mongo for balances |
| **Service / Repository** | sba-nium-api |
| **DB - Collections** | MongoDB |
| **Evidence Source** | README |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `README.md` — Delegated Model client and authorization flow.
