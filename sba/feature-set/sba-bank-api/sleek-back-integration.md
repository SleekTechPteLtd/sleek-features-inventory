# Sleek Back integration (users and companies)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Sleek Back integration (users and companies) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Aligns banking accounts and permissions with core Sleek company/user records and auth context. |
| **Entry Point / Surface** | Internal calls from `sba-bank-api` to sleek-back |
| **Short Description** | Orchestrator loads or updates user/company context used for business-account features and admin flows. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | sleek-back REST APIs |
| **Service / Repository** | sba-bank-api; sleek-back |
| **DB - Collections** | |
| **Evidence Source** | README architecture (sleek-back box) |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Exact endpoint list per flow |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `README.md` — diagram: sba-bank-api ↔ sleek-back.
