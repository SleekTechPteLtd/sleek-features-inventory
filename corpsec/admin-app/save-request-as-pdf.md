# Save Request as PDF

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Save Request as PDF |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Export a finalised request document as a formatted PDF for offline use or client delivery |
| **Entry Point / Surface** | Admin App > Request detail > SAVE AS PDF button |
| **Short Description** | Generates and downloads a PDF version of the request document. |
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
