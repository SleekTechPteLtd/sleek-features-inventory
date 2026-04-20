# Transfer money

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Transfer money |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Sends funds to saved or ad-hoc recipients (FAST/TT/etc. per product rules). |
| **Entry Point / Surface** | **`/sba/business-account/transfer`** — **`name: "transfer"`**, component **`SBATransfer`**; supports **`?recipient=`** query. |
| **Short Description** | Transfer workflow UI; `props` pass `recipientFromQuery` from route query for deep links. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Recipients; `sba-bank-api` transfer endpoints |
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

- `customer-sba/src/routes/routes.js` — `path: "business-account/transfer"`, `props: (route) => ({ recipientFromQuery: route.query.recipient })`.
