# Virtual card page

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Virtual card page |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Lets customers view and manage NIUM virtual card entry points from the dashboard. |
| **Entry Point / Surface** | **`/sba/business-account/virtual-card`** — **`name: "virtual card"`**, component **`VirtualCardPage`**. |
| **Short Description** | Nested under dashboard; card UI and controls before drilling into limits elsewhere. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | `sba-nium-api` via `sba-bank-api`; monthly limit route |
| **Service / Repository** | customer-sba; sba-bank-api; sba-nium-api |
| **DB - Collections** | N/A |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `customer-sba/src/routes/routes.js` — `path: "virtual-card"`, `component: VirtualCardPage`.
