# Beneficiary and recipient management

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Beneficiary and recipient management |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer / admin |
| **Business Outcome** | Stores and validates payout beneficiaries for repeat international transfers. |
| **Entry Point / Surface** | REST modules on `sba-nium-payout` |
| **Short Description** | CRUD-style beneficiary flows aligned with NIUM recipient APIs; linked to payout execution. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | sba-bank-api `recipient-controller` orchestration |
| **Service / Repository** | sba-nium-payout; sba-bank-api |
| **DB - Collections** | PostgreSQL |
| **Evidence Source** | sba-bank-api README — Recipient Management via NIUM payout |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `sba-bank-api/README.md` — vendor matrix: Recipient Management → NIUM payout.
- `src/v2/controllers/recipient-controller` (orchestrator).
