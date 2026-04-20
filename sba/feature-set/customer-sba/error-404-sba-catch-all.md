# SBA catch-all 404

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | SBA catch-all 404 |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Shows a consistent not-found experience for unknown paths under `/sba`. |
| **Entry Point / Surface** | **`/sba/*`** (unmatched) — **`name: "Error 404 - Page Not Found"`**, component **`Error404Page`** from `@sleek/customer-common`. |
| **Short Description** | Must be registered after concrete `/sba` routes so specific pages win; generic 404 shell. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Shared customer-common package |
| **Service / Repository** | customer-sba |
| **DB - Collections** | N/A |
| **Evidence Source** | codebase |
| **Criticality** | Low |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Confirm package ownership for `@sleek/customer-common` in your stack |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `customer-sba/src/routes/routes.js` — `path: "/sba/*"`, `component: Error404Page`.
