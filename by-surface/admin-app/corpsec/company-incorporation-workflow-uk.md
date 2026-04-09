# Company Incorporation Workflow (UK)

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Company Incorporation Workflow (UK) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corp Sec staff / Operations |
| **Business Outcome** | Automates end-to-end UK company incorporation including KYC verification |
| **Entry Point / Surface** | Admin App (UK) > Workflows > Camunda Workflows (filter: Incorporation) |
| **Short Description** | Manages UK company incorporation — key task step is KYC Verification (differs from SG/HK which has Incorporation RAF + Company Members). |
| **Variants / Markets** | UK (1333 active instances) |
| **Dependencies / Related Flows** | KYC Verification, SG/HK Incorporation workflows |
| **Service / Repository** | sleek-back, sleek-website, sleek-workflow (Camunda) |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | UK task steps differ from SG/HK (KYC Verification vs Incorporation RAF + Company Members) — different workflow definition or market-specific configuration? |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/sleek-workflow/` — Camunda task inbox and workflow UI (filter by process name). Also `src/views/admin/workflow/` for related legacy/new workflow entry.

### sleek-workflow (Camunda)

- Workflow definitions and instances are executed in **Camunda** (`sleek-workflow` repo per sheet); `sleek-back` integrates via workflow handlers and external tasks.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
