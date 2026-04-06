# Amend Company Share Structure Workflow

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Amend Company Share Structure Workflow |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corp Sec staff |
| **Business Outcome** | Automates amendment of a company's share structure including review confirmation and ACRA filing |
| **Entry Point / Surface** | Admin App > Workflows > Camunda Workflows (filter: Amend Company share structure) |
| **Short Description** | Manages amendments to a company's share capital or structure — from review & confirmation through ACRA filing. |
| **Variants / Markets** | SG (269 active instances; AU: definition exists 0 instances; HK/UK: not present) |
| **Dependencies / Related Flows** | ACRA filing, Shares register, Corp Sec requests |
| **Service / Repository** | sleek-back, sleek-website, sleek-workflow (Camunda) |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | AU has definition but 0 instances; system name is "Amend Company share structure" (lowercase s) |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/sleek-workflow/` — Camunda task inbox and workflow UI (filter by process name). Also `src/views/admin/workflow/` for related legacy/new workflow entry.

### sleek-workflow (Camunda)

- Workflow definitions and instances are executed in **Camunda** (`sleek-workflow` repo per sheet); `sleek-back` integrates via workflow handlers and external tasks.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
