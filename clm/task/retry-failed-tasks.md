# Retry Failed Tasks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Retry Failed Tasks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Allows operators to recover stalled or failed async workflows by re-queuing a failed task without manual re-submission or engineering intervention. |
| **Entry Point / Surface** | Internal ops tooling / API — `POST /tasks/:id/retry` |
| **Short Description** | Clones a failed task with reset status (`ready`) and zero attempts, then publishes it back onto its Bull queue so the existing worker picks it up and re-executes the workflow. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Task lifecycle (create, process, resolve, reject, archive); Bull queue workers (PAYMENT, PAYMENT_INTENT_RESOLVER, ProcessXeroWebhook); upstream flows that produce tasks (Xero webhooks, payment intents, subscription processing) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `tasks`, `archivedtasks` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. Is there a guard preventing retry of an already-processing task (no explicit status check before clone — could cause duplicate execution)? 2. No max-retry guard on retryTask itself; repeated retries bypass the original `maxRetry` ceiling. 3. What UI or internal tooling surfaces this endpoint to operators? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `task/controllers/task.controller.ts:65-71` — `POST /tasks/:id/retry`, guarded by `@Auth()` decorator, delegates to `TaskService.retryTask`.

### Core logic
- `task/services/task.service.ts:336-358` — `retryTask(taskId)`:
  1. Looks up the original task by ID via `TaskRepository.findById`.
  2. Calls `createTask({ ...task, status: TaskStatus.ready, attempts: 0, error: null })` — clones the task with a fresh identity.
  3. `createTask` deduplication check (`findExistingTask`) may short-circuit if an identical task is already `draft/ready/processing`.
  4. Publishes the new task to its assigned queue via `QueueService.addToQueue(retryTask.queue, retryTask.name, { taskId: retryTask._id })`.

### Queue dispatch
- `shared/services/queue.service.ts:18-28` — `addToQueue` routes to one of three Bull queues based on `task.queue`: `PAYMENT`, `PAYMENT_INTENT_RESOLVER`, or `ProcessXeroWebhook`.

### Data model
- `task/models/task.schema.ts` — `Task` collection; statuses: `draft`, `ready`, `processing`, `failed`, `canceled`, `completed`; tracks `attempts`, `maxRetry`, `error`, `errorDetail`, `rootTaskId`, `parentTaskId`, `childrenTaskIds`, `referenceId`, `companyId`.
- `task/models/archived-task.schema.ts` — `ArchivedTask` collection; read during `getTaskList` but not directly written by `retryTask`.
