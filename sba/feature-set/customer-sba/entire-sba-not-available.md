# Entire SBA not available notice

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Entire SBA not available notice |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Communicates when SBA is disabled or unavailable for the company (feature flag, market, or compliance). |
| **Entry Point / Surface** | **`/sba/business-account/not-available`** — **`name: "not-available"`**, component **`EntireSBANotAvailable`**. |
| **Short Description** | Blocking informational screen instead of core banking flows. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Product/config from `sleek-back` or orchestrator |
| **Service / Repository** | customer-sba; sba-bank-api; sleek-back |
| **DB - Collections** | N/A |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `customer-sba/src/routes/routes.js` — `path: "business-account/not-available"`.
