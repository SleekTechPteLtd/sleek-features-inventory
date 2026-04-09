# Company Deadlines Workflow

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Company Deadlines Workflow |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corp Sec staff / Finance staff |
| **Business Outcome** | Tracks and manages ongoing company compliance deadlines including management accounts obligations |
| **Entry Point / Surface** | Admin App (SG) > Workflows > Camunda Workflows (filter: Deadlines) |
| **Short Description** | Manages ongoing company compliance deadline workflows — surfaces as "Company Deadlines" instances; Management Account is a key observed task step. |
| **Variants / Markets** | SG (5498 active instances; AU: definition exists 0 instances; HK/UK: not present) |
| **Dependencies / Related Flows** | AGM & AR workflow, compliance calendar, Companies List > Deadlines tab |
| **Service / Repository** | sleek-back, sleek-website, sleek-workflow (Camunda) |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | HK and UK show no Deadlines workflow — confirm if handled differently in those markets; AU has definition but 0 instances |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/sleek-workflow/` — Camunda task inbox and workflow UI (filter by process name). Also `src/views/admin/workflow/` for related legacy/new workflow entry.

### sleek-workflow (Camunda)

- Workflow definitions and instances are executed in **Camunda** (`sleek-workflow` repo per sheet); `sleek-back` integrates via workflow handlers and external tasks.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
