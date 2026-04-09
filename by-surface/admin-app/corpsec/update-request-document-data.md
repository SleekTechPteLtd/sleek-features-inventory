# Update Request Document Data

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Update Request Document Data |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer |
| **Business Outcome** | Keep the structured data fields of a request document accurate as corporate details change |
| **Entry Point / Surface** | Admin App > Request detail > Update Document Data |
| **Short Description** | Edit structured form fields (e.g. title, parties, dates, addresses) for the request's document. Changes are saved to the request record. |
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
