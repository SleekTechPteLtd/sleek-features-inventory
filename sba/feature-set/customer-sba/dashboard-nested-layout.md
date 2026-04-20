# Dashboard nested layout (SBADashboard)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Dashboard nested layout (SBADashboard) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Hosts the main SBA home experience with child routes for account activity vs virtual card. |
| **Entry Point / Surface** | **`/sba`** with empty child path under `business-account` — **`name: "dashboard"`**, component **`SBADashboard`**. |
| **Short Description** | Dashboard route nests **`virtual-card`** and **`business-account`** (account transactions) as child paths. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Virtual card page; account transactions |
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

- `customer-sba/src/routes/routes.js` — `path: ""`, `name: "dashboard"`, `component: SBADashboard`, `children` for `virtual-card` and `business-account`.
