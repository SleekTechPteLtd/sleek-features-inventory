# CLM Operations Overview Dashboard

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | CLM Operations Overview Dashboard |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Gives operations staff a single-pane view of CLM performance metrics so they can monitor revenue, active subscriptions, pending payments, and renewal health without leaving the internal tool. |
| **Entry Point / Surface** | Sleek Billings Frontend > `/overview` (accessible via direct URL; nav-rail entry currently commented out under Billing > Dashboard) |
| **Short Description** | Renders an embedded Looker Studio report (Google Data Studio) inside the Overview page. The report covers CLM KPIs including revenue, active subscriptions, pending payments, and renewals. No bespoke data fetching occurs on this page — all data is sourced from the external Looker Studio report. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Looker Studio report ID `a0bc737e-696e-4f65-a469-2018855bf79b`; auth token passed via URL param and stored in localStorage by `AppContent`; billing config fetched from `sleekBillingsApi.getBillingConfig()` on app load |
| **Service / Repository** | sleek-billings-frontend |
| **DB - Collections** | None (read-only embed; no direct DB access from this page) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. Nav-rail entry (`/overview` under Billing > Dashboard) is commented out — is this page intentionally hidden or pending re-enablement? 2. The original native widget layout (Total Revenue, Active Subscriptions, Pending Payments, Upcoming Renewals, Revenue Trend, Subscription Distribution, Recent Activity cards) is fully commented out — has it been deprecated in favour of Looker Studio permanently? 3. Which markets/environments does the embedded Looker report cover? 4. Access control: the route has no explicit role guard; any authenticated user with a valid `auth` token can reach `/overview`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### File
- `src/pages/Overview/OverviewList.jsx` (sleek-billings-frontend) — entire component is a single `<iframe>` embedding the Looker Studio report.

### Looker Studio embed
```
src: https://lookerstudio.google.com/embed/reporting/a0bc737e-696e-4f65-a469-2018855bf79b/page/p_tbt6yha8rd
sandbox: allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox
dimensions: width=100%, height=980px, maxWidth=1250px
```

### Routing
- `src/App.jsx:154` — `<Route path="overview" element={<OverviewList />} />` under the `MasterLayout` authenticated shell.
- `src/data/nav-rail-items.js:14–20` — nav-rail entry (`label: "Dashboard"`, `navigation: "/overview"`) is commented out; the route exists but is not surfaced in the sidebar.

### Auth surface
- `src/App.jsx:84–101` — `auth` query param is stripped from the URL, stored in `localStorage`, and validated on every render; unauthenticated users are redirected to `/401`.
- No role-based guard specific to `/overview`.

### Commented-out native dashboard (decommissioned / paused)
The following widgets were present in markup but are fully commented out, replaced by the Looker Studio iframe:
- KPI cards: Total Revenue, Active Subscriptions, Pending Payments, Upcoming Renewals
- Charts: Revenue Trend, Subscription Distribution
- Table: Recent Activity
