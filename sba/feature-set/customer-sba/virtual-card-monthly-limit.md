# Virtual card monthly limit

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Virtual card monthly limit |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Allows customers to view or adjust monthly spend limits for virtual cards. |
| **Entry Point / Surface** | **`/sba/virtual-card/monthly-limit`** — **`name: "card-monthly-limit"`**, component **`SBACardMonthlyLimit`**. |
| **Short Description** | Standalone route under `/sba` (sibling to nested dashboard paths) for limit management UI. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Card APIs via orchestrator |
| **Service / Repository** | customer-sba; sba-bank-api; sba-nium-api |
| **DB - Collections** | N/A |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Confirm deep-link patterns from virtual card page |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `customer-sba/src/routes/routes.js` — `path: "virtual-card/monthly-limit"`, `component: SBACardMonthlyLimit`.
