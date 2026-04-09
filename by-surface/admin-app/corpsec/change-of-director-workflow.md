# Change of Director Workflow

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Change of Director Workflow |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corp Sec staff |
| **Business Outcome** | Automates the process of replacing a company director including nominee assignment |
| **Entry Point / Surface** | Admin App > Workflows > Camunda Workflows (filter: Change of Director) |
| **Short Description** | Manages director change requests — routing through nominee director assignment to complete the change. |
| **Variants / Markets** | SG (107 active instances; AU: definition exists 0 instances; HK/UK: not present) |
| **Dependencies / Related Flows** | Appointment of Director workflow, Nominee Director assignment |
| **Service / Repository** | sleek-back, sleek-website, sleek-workflow (Camunda) |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | AU has definition but 0 instances; only Assign a Nominee Director step observed — may have additional steps not captured |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/sleek-workflow/` — Camunda task inbox and workflow UI (filter by process name). Also `src/views/admin/workflow/` for related legacy/new workflow entry.

### sleek-workflow (Camunda)

- Workflow definitions and instances are executed in **Camunda** (`sleek-workflow` repo per sheet); `sleek-back` integrates via workflow handlers and external tasks.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
