# Client Portal – Company Secretary File Browser

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Portal – Company Secretary File Browser |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Company Director |
| **Business Outcome** | Enables clients to self-serve access to their company documents without contacting Sleek support, reducing support load and improving transparency. |
| **Entry Point / Surface** | Client App > Company Secretary (left nav) |
| **Short Description** | Hierarchical document repository where clients browse top-level folders: A – Registers, B – Share Certificates, C – Minutes and Resolutions, D – ACRA Filings, Draft, E – Constitution, F – Miscellaneous, G – KYC, H – Immigration. Supports inline PDF preview, multi-select with bulk download, file search, name/date sorting, and pagination. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Admin app file management; Corpsec document generation flows; SleekSign (signed docs stored here) |
| **Service / Repository** | customer-main, customer-common, customer-root (client shell and shared UI) |
| **DB - Collections** | — |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** |  |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### customer-main

- Route `GET /customer/secretary` — `src/routes/routes.js` (`name: corporate-secretary`).
- `src/modules/corporate-secretary/containers/CorporateSecretary.vue` → `CorporateSecretaryPanel.vue` — folder tree, search, `FileDataTable` for files/folders (bulk actions, PDF flow per shared file explorer).

### customer-common

- `MasterLayout` / nav: `SleekDrawerContentV2.vue`, `SleekDrawer.vue`, `SleekMobileDrawer.vue` — `company_secretary` feature flag gates **Company secretary** left-nav entry.
- `src/modules/shared/components/presentational/FileDataTable.vue` — shared table/download copy used by secretary (and similar explorers).

### customer-root

- `src/root-config.js` — registers `@sleek/customer-main` for `activeWhen: ["/customer"]` (shell loads the MFE where `/customer/secretary` is handled).

### Live app walkthrough

- Confirms folder labels (A–H etc.), preview, search, and pagination described on the sheet.
