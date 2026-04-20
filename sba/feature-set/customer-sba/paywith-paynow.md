# Pay with PayNow

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Pay with PayNow |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Initiates or completes PayNow flows for SBA payments. |
| **Entry Point / Surface** | **`/sba/business-account/paynow`** — **`name: "paynow"`**, dynamic import **`PayWithPayNow`**. |
| **Short Description** | Code-split page for PayNow UX; integrates with DBS PayNow rails via backend. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | `sba-bank-dbs-api` via `sba-bank-api` |
| **Service / Repository** | customer-sba; sba-bank-api; sba-bank-dbs-api |
| **DB - Collections** | N/A |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `customer-sba/src/routes/routes.js` — `path: "business-account/paynow"`, `component: () => import("@/modules/business-account/pages/PayWithPayNow")`.
