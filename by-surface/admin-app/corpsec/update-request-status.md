# Update Request Status

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Update Request Status |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Advance a request through its lifecycle and optionally alert the client of the change |
| **Entry Point / Surface** | Admin App > Request detail > Update Status |
| **Short Description** | Change the request status (e.g. Draft → Pending → Completed). Includes an option to notify the company when the status is updated. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** |  |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/requests/edit.js` — request detail (document data, status, rich-text document, PDF, SleekSign). Webpack: `admin/requests/edit`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
