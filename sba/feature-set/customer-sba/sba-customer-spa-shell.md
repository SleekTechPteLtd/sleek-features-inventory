# SBA customer SPA (Single-SPA microfrontend)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | SBA customer SPA (Single-SPA microfrontend) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Delivers the `/sba` banking experience inside the customer Single-SPA shell: onboarding, dashboard, and account flows that call `sba-bank-api`. |
| **Entry Point / Surface** | **`customer-sba`** Vue MFE loaded by `customer-root`; route prefix **`/sba`** (see architecture diagram in `sba-bank-api` README). |
| **Short Description** | Customer-facing SBA UI: composes screens for transfers, accounts, cards, and payouts; uses shared auth and axios to the orchestrator. |
| **Variants / Markets** | SG-first; env-specific API base URLs |
| **Dependencies / Related Flows** | sba-bank-api; Sleek Auth / customer shell |
| **Service / Repository** | customer-sba; sba-bank-api |
| **DB - Collections** | N/A (browser + orchestrator) |
| **Evidence Source** | sba-bank-api README (system overview diagram) |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Enumerate route map and parity with orchestrator OpenAPI |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `sba-bank-api/README.md` — Frontend: `customer-sba` (Vue 2) at `/sba`, loaded from single-SPA shell.
