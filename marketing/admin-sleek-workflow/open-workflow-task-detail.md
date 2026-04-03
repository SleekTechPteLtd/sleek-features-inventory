# Open workflow task detail

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Open workflow task detail |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Lets admins move from the Camunda workflow list into the full workflow task workspace for a specific process without losing the list context (new tab). |
| **Entry Point / Surface** | Sleek Admin > Workflow list (Camunda workflow) — click a row (status, workflow name, company, current task, or date column; not the assignee column) |
| **Short Description** | From the admin workflow table, clicking most cells on a process row calls `window.open` with `/admin/sleek-workflow/workflow-task/?processId={processId}&processInstanceId={processInstanceId}` and target `_blank`, opening the workflow task page in a new browser tab. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Parent list: `WorkFlowList` in `sleek-workflow/index.js` loads rows via `getSleekWorkflowProcesses` / Camunda APIs. Downstream: workflow task shell at `workflow-task/` (task UI, `api-camunda`). Same URL pattern is reused from incorporation/KYC flows (`table-row-all-users.js`, `kyc-action-button.js`, etc.). Row actions also include force cancel/done modals calling `updateProcessStatusForce` (`api-wfe`), separate from open-in-tab. |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **New-tab navigation**: `src/views/admin/sleek-workflow/components/table.js` — `handleOpen(e, id, processInstanceId)` prevents default and runs `window.open(\`/admin/sleek-workflow/workflow-task/?processId=${id}&processInstanceId=${processInstanceId}\`, "_blank")` (lines 529–532).
- **Row click wiring**: Status, workflow/company name, company, current task, and date-created cells attach `onClick={(e) => this.handleOpen(e, row.processId, row.processInstanceId)}` in `renderRows` (e.g. lines 965–965, 977–977, 981–981, 985–987, 1015–1015). The assignee column renders `Assignee` without `handleOpen`, so reassignment does not open the task page.
- **List shell**: `src/views/admin/sleek-workflow/index.js` — `AdminLayout` with `sidebarActiveMenuItemKey="camunda-workflow"`, breadcrumb “Workflow list”, mounts `Table` with process rows from list initialization.
- **Related API imports on same table** (separate feature paths): `updateProcessStatusForce` from `utils/api-wfe` for force cancel/done modals (`handleApprove` / `ModalForceChangeStatus`).
