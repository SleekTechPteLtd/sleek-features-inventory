# SPA shell: SBA root redirect and BusinessAccount layout

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | SPA shell: `/sba` redirect and BusinessAccount layout |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Mounts the SBA customer experience under `/sba` and sends users to the business-account area by default. |
| **Entry Point / Surface** | **`/sba`** → redirect **`/sba/business-account`**; nested routes use **`BusinessAccount`** container (`customer-sba`). |
| **Short Description** | Root route registers the redirect; parent **`business-account`** name wraps dashboard, transfers, recipients, accounts, PayNow, FX, and related screens as Vue children. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Single-SPA host (`customer-root`); `sba-bank-api` for data |
| **Service / Repository** | customer-sba |
| **DB - Collections** | N/A |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `customer-sba/src/routes/routes.js` — `path: "/sba"` redirect; `name: "business-account"`, `component: BusinessAccount`.
