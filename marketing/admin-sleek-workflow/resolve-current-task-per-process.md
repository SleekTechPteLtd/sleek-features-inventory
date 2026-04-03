# Resolve current task per process

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Resolve current task per process |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (staff workflow list); selection logic runs in the browser after Camunda task payloads load |
| **Business Outcome** | Each row in the admin workflow list shows a meaningful “current task” label (active step when work is in flight, otherwise the last visible completed step) so staff can see progress at a glance. |
| **Entry Point / Surface** | **sleek-website** admin: **Workflow** list (`/admin/sleek-workflow/` or equivalent route mounting `WorkFlowList`) — sidebar `camunda-workflow`; table column renders task title via `currentTask`. |
| **Short Description** | After processes and per-process task lists are fetched from the Camunda workflow API, `getCurrentTask` picks one task per process: the first **open** task (`startTime` set, `endTime` absent, non-hidden, with `id`), or if none exists, the **last** matching **completed** visible task (`findLast` on the ordered list). That value becomes `row.currentTask` for assignee display and the “current task” column. |
| **Variants / Markets** | **Unknown** in this view — tenant is read from platform config for layout/API host context; task rules are not market-specific in code. |
| **Dependencies / Related Flows** | **`initialize`** loads processes via `getSleekWorkflowProcesses` then enriches rows with `getSleekWorkflowProcessTasks` (`withVariables=true`). **Table** (`components/table.js`) shows `setTitle(row.currentTask)` (task `name`, or “all completed” style label when `deleteReason` matches completed). **Assignee** updates mutate `row.currentTask`. Related pattern: `deadlines-process-instance.js` defines its own `getCurrentTask` for a single process detail flow — same intent, separate implementation. |
| **Service / Repository** | **sleek-website**: `src/views/admin/sleek-workflow/index.js` (`getCurrentTask`), `src/views/admin/sleek-workflow/services/api-camunda.js` (`GET /v2/sleek-workflow/processes`, `GET /v2/sleek-workflow/processes/tasks`). Backend implementation for those routes not in this repo. |
| **DB - Collections** | **Unknown** — this view consumes REST responses only; persistence for processes/tasks is assumed Camunda (and any backing store behind **sleek-back**), not referenced here. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `findLast` ordering always matches Camunda’s task list order for “last completed” semantics across all workflow types; whether `hidden` is exhaustive for tasks that should never surface in this column. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/sleek-workflow/index.js`

- **`getCurrentTask(tasks)`** (lines 204–220): `find` for first task with `task.startTime && !task.endTime && task.id && !task.hidden`; else `findLast` for `task.startTime && task.endTime && task.id && !task.hidden`; returns `""` if no match (falsy in row).
- **`initialize`**: builds `rows` from `getSleekWorkflowProcesses`, then `fetchProcessTasks` → for each row, `currentTask = this.getCurrentTask(workflowTask.tasks.taskList)`, sets `assignee` from `currentTask`, merges `tasks` and `tasksVariables`.

### `src/views/admin/sleek-workflow/services/api-camunda.js`

- **`getSleekWorkflowProcesses`**: `GET ${base}/v2/sleek-workflow/processes` with query (`limit`, `offset`, filters, `need_task_obj=false`).
- **`getSleekWorkflowProcessTasks`**: `GET ${base}/v2/sleek-workflow/processes/tasks` with `processIds`, `withVariables=true`.

### `src/views/admin/sleek-workflow/components/table.js`

- **Current task column**: Renders spinner while `currentTask` is null; otherwise tooltip + ellipsis with `setTitle(currentTask)` — uses `currentTask.name` or a completed label when `deleteReason === COMPLETED`.

### `src/views/admin/sleek-workflow/components/assignee.js`

- Uses `row.currentTask.id` and assignee fields for reassignment UI tied to the resolved task.
