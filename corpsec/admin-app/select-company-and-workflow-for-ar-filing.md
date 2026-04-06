# Select Company & Workflow for AR Filing

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Select Company & Workflow for AR Filing |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Quickly locate a specific company's active Annual Return workflow without navigating through the company list |
| **Entry Point / Surface** | Admin App > Corp Sec > AR Filing |
| **Short Description** | Dedicated AR Filing page (Corp Sec > AR Filing in SG sidebar; accessible via URL in HK). Corpsec officer selects a company via searchable dropdown — a 'Go to Company' shortcut link appears on selection. The 'Select Workflow' dropdown then populates with the company's active Camunda AGM & AR deadlines workflows (auto-selects if only one exists). |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Corp Sec nav section is present in SG sidebar but absent from HK sidebar — the /admin/corpsec/ar-filing/ URL loads in HK but is not surfaced in HK navigation. Confirm whether this is intentional. UK and AU unverified — sessions expired before audit. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/corpsec/ar-filing/index.js` and `components/*` — company selector, workflow selector, source documents, manual upload (`ManualUploadSection.js`). Webpack: `admin/corpsec/ar-filing`.

### sleek-back

- `controllers-v2/corpsec.js` + `controllers-v2/handlers/corpsec/ar-filing.js` — AR filing REST routes (documents, upload, process binding).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
