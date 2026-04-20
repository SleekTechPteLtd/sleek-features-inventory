# FX and MAS rate lookups

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | FX and MAS rate lookups |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System / internal admin flows |
| **Business Outcome** | Surfaces currency conversion and regulatory reference rates for cross-currency and reporting. |
| **Entry Point / Surface** | REST endpoints on `sba-bank-dbs-api` (Swagger) |
| **Short Description** | Integrates DBS FX endpoints and MAS daily rate feeds as described in orchestrator README. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | MAS; DBS FX |
| **Service / Repository** | sba-bank-dbs-api |
| **DB - Collections** | |
| **Evidence Source** | sba-bank-api README vendor matrix (currency exchange) |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Confirm exact DBS vs MAS call split in this repo |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- Architecture references in `sba-bank-api/README.md` — currency exchange via DBS; MAS daily FX.
