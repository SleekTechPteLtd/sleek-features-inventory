# Edit Request Document Content

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Edit Request Document Content |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer |
| **Business Outcome** | Directly author or correct the full document body for a request before signing or delivery |
| **Entry Point / Surface** | Admin App > Request detail > Edit Document (rich text editor) |
| **Short Description** | Rich text editor for editing the full document content of a request. Supports formatted text editing and live document preview. |
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
