# View & Search Requests List

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | View & Search Requests List |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Give staff a single view of all corpsec requests to track and manage them efficiently |
| **Entry Point / Surface** | Admin App > Requests |
| **Short Description** | Paginated list of all requests. Supports search by company name and status filters. Columns include company name, request type, status, and created date. |
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

- `src/views/admin/requests/index.js` — request list; `requests/new.js` — new request. Webpack: `admin/requests/index`, `admin/requests/new`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
