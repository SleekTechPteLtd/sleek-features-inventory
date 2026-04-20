# DBS transfers (FAST, PayNow, TT, A2A)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | DBS transfers (FAST, PayNow, TT, A2A) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (via sba-bank-api) |
| **Business Outcome** | Executes domestic and cross-border payment rails supported by DBS for SBA customers. |
| **Entry Point / Surface** | REST API on `sba-bank-dbs-api` (API key); called only from orchestrator |
| **Short Description** | Transfer controller and services wrap DBS APIs for FAST, PayNow, telegraphic/SWIFT, and account-to-account transfers with validation and error mapping. |
| **Variants / Markets** | SG DBS sandbox/UAT vs production |
| **Dependencies / Related Flows** | DBS corporate banking APIs |
| **Service / Repository** | sba-bank-dbs-api |
| **DB - Collections** | MongoDB (per service migrations) |
| **Evidence Source** | README; `src/v2/controllers/transfer-controller` |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `README.md` — FAST, PayNow, TT, A2A scope.
- `src/v2/services/transfer-service` — transfer orchestration.
