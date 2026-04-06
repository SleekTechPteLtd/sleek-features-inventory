# Client Portal – History of Requests View

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Portal – History of Requests View |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Company Director |
| **Business Outcome** | Provides an audit trail of completed requests for client reference and compliance record-keeping. |
| **Entry Point / Surface** | Client App > Requests > History (left nav) |
| **Short Description** | Paginated table of completed Corpsec requests. Columns: Request type, Track Status (e.g. DONE), Price, Request ID, Date. Configurable rows-per-page. Test account showed Accounting Onboarding V2 and KYC Individual as DONE entries. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | On-going Requests view; admin-side request processing |
| **Service / Repository** | customer-main, customer-common, customer-root (client shell and shared UI) |
| **DB - Collections** | — |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** |  |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### customer-main

- Route `GET /customer/history-of-request` — `src/routes/routes.js` (`name: history-of-request`).
- `src/modules/customer-requests/containers/HistoryOfRequest.vue` → `components/HistoryOfRequestContent.vue` — paginated completed requests table.
- `src/proxies/back-end/customer-requests/get.js` — list data via `/customer-requests`.

### customer-common

- Shared layout / navigation chrome for customer pages.

### customer-root

- `src/root-config.js` — MFE registration for `/customer`.

### Live app walkthrough

- Confirms columns (type, status, price, ID, date) and row paging.
