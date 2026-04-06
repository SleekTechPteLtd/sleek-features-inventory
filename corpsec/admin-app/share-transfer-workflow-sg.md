# Share Transfer Workflow (SG)

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Share Transfer Workflow (SG) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corp Sec staff |
| **Business Outcome** | Automates share transfer between parties including RAF review and document generation |
| **Entry Point / Surface** | Admin App > Workflows > Camunda Workflows (filter: Transfer) |
| **Short Description** | Manages share transfer requests in SG — progressing through Company Members update, Transfer RAF, transfer review, and document generation. |
| **Variants / Markets** | SG (357 active instances; AU: definition exists 0 instances; HK/UK: not present) |
| **Dependencies / Related Flows** | Company Members, Transfer documents, RAF |
| **Service / Repository** | sleek-back, sleek-website, sleek-workflow (Camunda) |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | System name is "Transfer" (not "SG Transfer"); AU has definition but 0 instances |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/sleek-workflow/` — Camunda task inbox and workflow UI (filter by process name). Also `src/views/admin/workflow/` for related legacy/new workflow entry.

### sleek-workflow (Camunda)

- Workflow definitions and instances are executed in **Camunda** (`sleek-workflow` repo per sheet); `sleek-back` integrates via workflow handlers and external tasks.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
