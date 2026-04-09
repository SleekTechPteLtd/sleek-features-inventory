# Appointment of Director Workflow

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Appointment of Director Workflow |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corp Sec staff |
| **Business Outcome** | Automates the appointment of a new director including nominee assignment and completion |
| **Entry Point / Surface** | Admin App > Workflows > Camunda Workflows (filter: Appointment of Director) |
| **Short Description** | Guides appointment of a new director — progressing through nominee assignment to end. |
| **Variants / Markets** | SG (110 active instances; AU: definition exists 0 instances; HK/UK: not present) |
| **Dependencies / Related Flows** | Change of Director workflow, Nominee Director assignment, ACRA filing |
| **Service / Repository** | sleek-back, sleek-website, sleek-workflow (Camunda) |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | AU has definition but 0 instances |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/sleek-workflow/` — Camunda task inbox and workflow UI (filter by process name). Also `src/views/admin/workflow/` for related legacy/new workflow entry.

### sleek-workflow (Camunda)

- Workflow definitions and instances are executed in **Camunda** (`sleek-workflow` repo per sheet); `sleek-back` integrates via workflow handlers and external tasks.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
