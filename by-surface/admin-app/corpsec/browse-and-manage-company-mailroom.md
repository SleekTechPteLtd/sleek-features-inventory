# Browse & Manage Company Mailroom

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Browse & Manage Company Mailroom |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Give staff access to physical mail and documents received on behalf of a company via a centralised mailroom view |
| **Entry Point / Surface** | Admin App > Mailroom > Select Company |
| **Short Description** | Company-scoped mailroom browser with identical file browser UI to the Files section. Admin selects a company to view and manage received mail/documents. Supports browse, upload, create folder, download, delete, search, and generate standard folder structure — all inherited from the Files section. Unique addition: NOTIFY OWNER button. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Files section (shared UI) |
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

- `src/views/admin/mailroom.js` — mailroom UI (shared patterns with Files; notify owner action). Webpack: `admin/mailroom`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
