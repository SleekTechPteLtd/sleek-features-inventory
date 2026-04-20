# Virtual accounts and CAMT statements

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Virtual accounts and CAMT statements |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Provides virtual account lifecycle and CAMT052/053 statement ingestion for reconciliation and reporting. |
| **Entry Point / Surface** | v3 virtual-account and statement routes on `sba-bank-dbs-api` |
| **Short Description** | Virtual account controllers/services manage VA setup; statement pipeline processes CAMT files for balances and transactions. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | DBS virtual account and statement APIs |
| **Service / Repository** | sba-bank-dbs-api |
| **DB - Collections** | MongoDB |
| **Evidence Source** | README; `src/v3/controllers/virtual-account`, `src/v3/controllers/statement` |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `README.md` — virtual accounts and CAMT statement processing.
- `src/v3/services/virtual-account`, `src/v3/services/statement`.
