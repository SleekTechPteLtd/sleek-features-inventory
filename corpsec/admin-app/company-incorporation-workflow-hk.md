# Company Incorporation Workflow (HK)

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Company Incorporation Workflow (HK) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corp Sec staff / Operations |
| **Business Outcome** | Automates end-to-end HK company incorporation |
| **Entry Point / Surface** | Admin App (HK) > Workflows > Camunda Workflows (filter: Incorporation) |
| **Short Description** | Manages Hong Kong company incorporation — progressing through Incorporation RAF and Company Members setup stages. |
| **Variants / Markets** | HK (1589 active instances) |
| **Dependencies / Related Flows** | KYC, Company Members, RAF, SG/UK Incorporation workflows |
| **Service / Repository** | sleek-back, sleek-website, sleek-workflow (Camunda) |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Confirm if same Camunda workflow definition as SG or region-specific variant |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/sleek-workflow/` — Camunda task inbox and workflow UI (filter by process name). Also `src/views/admin/workflow/` for related legacy/new workflow entry.

### sleek-workflow (Camunda)

- Workflow definitions and instances are executed in **Camunda** (`sleek-workflow` repo per sheet); `sleek-back` integrates via workflow handlers and external tasks.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
