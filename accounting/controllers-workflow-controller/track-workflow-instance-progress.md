# Track workflow instance progress

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Track workflow instance progress |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User (authenticated caller via Sleek Back; typically the client app for a user in a guided workflow) |
| **Business Outcome** | Users and apps can see how far a guided workflow has progressed and which section and task are active so they can resume work or explain status without guessing. |
| **Entry Point / Surface** | Sleek Back HTTP API: `GET /workflow-instances/:workflowInstanceId/progress` (mounted from `controllers/workflow-controller.js` at `/`); requires `userService.authMiddleware` (authenticated session). |
| **Short Description** | Loads the workflow instance with populated section tasks, loads all tasks for that instance, computes completed vs total counts and a completion percentage, and finds the first task with status `available` in presentation order to return the current section name and task name. Response JSON: `percentage`, `total`, `completed`, `section`, `task`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | User authentication (`user-service` middleware); workflow templates and task lifecycle elsewhere in Sleek Back that set task `status` (`unavailable`, `available`, `completed` per `config/shared-data.json`); downstream clients that poll or display this payload. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `workflowinstances` (WorkflowInstance model), `workflowtasks` (WorkflowTask model) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | If every task is non-`available` (e.g. all completed) or presentation order has no `available` task, `section` and `task` are omitted/undefined in the JSON; `percentage` divides by `counts.total`—if zero tasks, percentage is NaN. Confirm intended API contract. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/workflow-controller.js`

- `GET /workflow-instances/:workflowInstanceId/progress` with `userService.authMiddleware`.
- `WorkflowInstance.findById(workflowInstanceId)` with `populate({ path: "presentation.sections.tasks", model: "WorkflowTask" })`.
- `WorkflowTask.find({ workflow_instance: workflowInstanceId })` for all tasks on the instance.
- Reduces tasks to `total` and `completed` (where `status === "completed"`); `percentage = Math.round((100 * completed) / total)`.
- Walks `workflowInstance.presentation.sections` in order; nested `section.tasks`; first task with `status === "available"` sets `currentTask = task.name`, `currentSection = section.name`.
- Responds with `{ percentage, total, completed, section, task }`; errors → `422` with JSON body.

### `schemas/workflow-instance.js`

- Model `WorkflowInstance`: `workflow_template` ref, `name`, `presentation.sections[]` with `tasks` (ObjectId refs to `WorkflowTask`), `name`, `data`, plus `data` at root; `timestamps`.

### `schemas/workflow-task.js`

- Model `WorkflowTask`: `workflow_instance` ref, `name`, `type` and `status` enums from `sharedData.workflowTasks`, `dependencies`, typed `data` subdocument (company, user, request instance, files, etc.); `timestamps`.

### `config/shared-data.json` (workflow task status)

- `workflowTasks.status`: `unavailable`, `available`, `completed` — aligns with “current” task detection (`available`) and progress counting (`completed`).
