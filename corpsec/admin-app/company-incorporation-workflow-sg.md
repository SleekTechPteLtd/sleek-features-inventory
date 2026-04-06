# Company Incorporation Workflow (SG)

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Company Incorporation Workflow (SG) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corp Sec staff / Operations |
| **Business Outcome** | Automates end-to-end SG company incorporation from RAF through company members setup |
| **Entry Point / Surface** | Admin App (SG) > Workflows > Camunda Workflows (filter: Incorporation) |
| **Short Description** | Manages Singapore company incorporation — progressing through Incorporation RAF and Company Members setup stages. |
| **Variants / Markets** | SG (3453 active instances; AU: definition exists 0 instances) |
| **Dependencies / Related Flows** | KYC, Company Members, RAF, HK/UK Incorporation workflows |
| **Service / Repository** | sleek-back, sleek-website, sleek-workflow (Camunda) |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | SG/HK/UK each run an "Incorporation" workflow in their respective regional environments — confirm if same definition deployed per-region or separate workflow definitions |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/sleek-workflow/` — Camunda task inbox and workflow UI (filter by process name). Also `src/views/admin/workflow/` for related legacy/new workflow entry.

### sleek-workflow (Camunda)

- Workflow definitions and instances are executed in **Camunda** (`sleek-workflow` repo per sheet); `sleek-back` integrates via workflow handlers and external tasks.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
