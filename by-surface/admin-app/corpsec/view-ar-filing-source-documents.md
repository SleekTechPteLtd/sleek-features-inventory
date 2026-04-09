# View AR Filing Source Documents

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | View AR Filing Source Documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Review which documents have been auto-generated or linked by the AR workflow so the corpsec team can prepare the filing package |
| **Entry Point / Surface** | Admin App > Corp Sec > AR Filing > Source Documents panel |
| **Short Description** | After selecting a company and workflow, a 'Source Documents' panel lists all documents associated with the AR workflow (auto-populated from the Camunda workflow). A 'Go To Workflow' shortcut link is available to navigate directly to the full workflow detail. Empty state: 'No AR filing files found for this workflow.' |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | Camunda Workflows / Deadlines workflow |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | UK and AU unverified — sessions expired before audit. Confirm what events cause source documents to populate (e.g. workflow task completion, document generation step). |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/corpsec/ar-filing/index.js` and `components/*` — company selector, workflow selector, source documents, manual upload (`ManualUploadSection.js`). Webpack: `admin/corpsec/ar-filing`.

### sleek-back

- `controllers-v2/corpsec.js` + `controllers-v2/handlers/corpsec/ar-filing.js` — AR filing REST routes (documents, upload, process binding).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
