# AGM & Annual Return Workflow

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | AGM & Annual Return Workflow |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corp Sec staff |
| **Business Outcome** | Automates annual AGM and Annual Return compliance obligations for SG companies |
| **Entry Point / Surface** | Admin App (SG) > Workflows > Camunda Workflows (filter: AGM & AR) |
| **Short Description** | Manages the Annual General Meeting and Annual Return filing process for Singapore companies — Annual General Meeting is the primary observed task step. |
| **Variants / Markets** | SG (5529 active instances; AU: definition exists 0 instances; HK/UK: not present) |
| **Dependencies / Related Flows** | Company Deadlines workflow, ACRA filing, compliance calendar |
| **Service / Repository** | sleek-back, sleek-website, sleek-workflow (Camunda) |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | HK and UK show no AGM & AR workflow — confirm if AGM is not a requirement in those jurisdictions or handled via a different flow |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/sleek-workflow/` — Camunda task inbox and workflow UI (filter by process name). Also `src/views/admin/workflow/` for related legacy/new workflow entry.

### sleek-workflow (Camunda)

- Workflow definitions and instances are executed in **Camunda** (`sleek-workflow` repo per sheet); `sleek-back` integrates via workflow handlers and external tasks.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
