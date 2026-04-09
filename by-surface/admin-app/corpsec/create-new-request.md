# Create New Request

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Create New Request |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Initiate a new corpsec document request for a company from a standard template |
| **Entry Point / Surface** | Admin App > Requests > NEW REQUEST button |
| **Short Description** | Create a new corpsec request by selecting a company and a request template. Populates the request with default document data from the template. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Request Templates |
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
