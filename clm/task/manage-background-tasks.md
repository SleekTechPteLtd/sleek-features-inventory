# Manage Background Tasks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Background Tasks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Gives platform operators visibility and control over all async background tasks so that failed or stalled workflows can be diagnosed, retried, or removed without requiring engineering intervention. |
| **Entry Point / Surface** | Internal Admin API — `GET/POST/PUT/DELETE /tasks`; likely surfaced via Sleek CLM admin tooling |
| **Short Description** | Provides full lifecycle management (list, detail, create, update, retry, delete) of background tasks that power async workflows across the billing platform. Operators can filter by company, reference entity, or task hierarchy and retry failed tasks by re-enqueuing them. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | QueueService (BullMQ) — task dispatch on create/retry; TaskRepository — active task persistence; ArchivedTaskRepository — completed/expired task store; UserService — creator resolution; nestjs-cls — request-scoped context propagation (parentTaskId, rootTaskId, companyId); task-processor.scheduler.ts — polls and dispatches batch tasks; task-processor.processor.ts — executes task business logic |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `tasks` (active tasks, SleekPaymentDB), `archivedtasks` (completed / auto-expired tasks, SleekPaymentDB) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | No frontend surface identified in code — unclear whether operators access this via CLM admin UI or internal scripts. `DataStreamerService` is injected into `TaskService` but not called in any visible method — may be used by subclasses or may be unused. Markets not determinable from code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `task/controllers/task.controller.ts`

All endpoints are guarded with `@Auth()`.

| Method | Route | Operation |
|---|---|---|
| `GET` | `/tasks` | List tasks (paginated, filtered by `companyId`, `referenceId`, `rootTaskId`) |
| `GET` | `/tasks/:id` | Get single task detail; throws 404 if not found |
| `POST` | `/tasks` | Create a new task (idempotent — reuses existing draft/ready/processing task with same name+data) |
| `PUT` | `/tasks/:id` | Update task fields; throws 404 if not found |
| `POST` | `/tasks/:id/retry` | Re-create a failed task with `status=ready, attempts=0` and re-enqueue it |
| `DELETE` | `/tasks/:id` | Soft-delete task (`deleted: true`) |

### Service — `task/services/task.service.ts`

Key behaviors:
- **Deduplication on create:** checks for existing tasks with same `name` + `data` in `draft/ready/processing` states; reuses last match.
- **Task hierarchy:** supports `rootTaskId`, `parentTaskId`, `previousTaskId`, `childrenTaskIds`, and `requiredTaskIds` for chaining and fan-out workflows. Parent's `childrenTaskIds` array is updated on child creation.
- **Sequential chaining:** on `resolveTask`, looks for a task with `previousTaskId == completedTask._id`; if found, sets it to `ready` and enqueues it.
- **Retry gate:** skips processing if already `completed`, or if `processing/failed` with `attempts == maxRetry`.
- **Duplicate-run guard:** in-memory `processingTasks` array prevents concurrent execution of identical tasks; cancels the duplicate.
- **Archive lifecycle:** completed/failed/canceled tasks receive an `archiveAt` timestamp (default: `TASK_ARCHIVE_DURATION` days); a scheduler moves them to the `archivedtasks` collection and TTL indexes handle final expiry.
- **Context propagation:** uses `nestjs-cls` to carry `parentTaskId`, `rootTaskId`, and `companyId` through async execution scope so child tasks created during processing inherit hierarchy automatically.

### Schema — `task/models/task.schema.ts` & `task/models/archived-task.schema.ts`

**Collection: `tasks`**

| Field | Type | Notes |
|---|---|---|
| `name` | string | Task type identifier (e.g. `resolveLatestPaymentIntentV2`) |
| `queue` | string | BullMQ queue name |
| `interval` | number | Retry interval in ms (default 10 min) |
| `maxRetry` | number | Max attempts (default 3) |
| `data` | Mixed | Task payload |
| `status` | enum | `draft`, `ready`, `processing`, `failed`, `canceled`, `completed` |
| `attempts` | number | Current attempt count |
| `pickedAt` | Date | Timestamp when scheduler last picked for processing |
| `lastAttemptedAt` | Date | Timestamp of last attempt |
| `rootTaskId` | ObjectId → Task | Top-level ancestor |
| `parentTaskId` | ObjectId → Task | Direct parent |
| `previousTaskId` | ObjectId → Task | Predecessor in sequential chain |
| `requiredTaskIds` | ObjectId[] → Task | Tasks that must complete before this one runs |
| `childrenTaskIds` | ObjectId[] → Task | Child tasks spawned during processing |
| `referenceId` | ObjectId | Link to external entity (e.g. invoice, subscription) |
| `referenceType` | string | Type label for `referenceId` |
| `companyId` | ObjectId | Owning company |
| `userId` | ObjectId | Creator user |
| `archiveAt` | Date | When to move to archive collection |
| `startedAt / endedAt` | Date | Execution window |
| `executionTime` | number | Duration in ms |
| `deleted` | boolean | Soft-delete flag |

Indexes: `{ archiveAt: 1 }`, `{ status: 1, attempts: 1 }`

**Collection: `archivedtasks`** — mirrors `tasks` schema; additional TTL index on `expireAt` for automatic MongoDB expiry. Extra indexes: `{ companyId: 1 }`, `{ parentTaskId: 1 }`, `{ lastAttemptedAt: 1 }`.

### Repository — `task/repositories/task.repository.ts`

`findBatchProcessTasks(batchSize)`: picks tasks where `pickedAt` and `lastAttemptedAt` are beyond their `interval`, status is actionable (`ready`, or `processing/failed` with remaining retries). Updates `pickedAt` atomically to prevent concurrent pick.
