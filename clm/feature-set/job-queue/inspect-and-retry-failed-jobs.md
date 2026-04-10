# Inspect and Retry Failed Jobs

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Inspect and Retry Failed Jobs |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Admins can observe the health of all background job queues and manually recover from processing failures by retrying failed or completed jobs with their original data, without code deployments or engineering escalation. |
| **Entry Point / Surface** | Sleek Billings App > Job Queue (API: `GET /queue-jobs`, `GET /queue-jobs/jobs`, `POST /queue-jobs/jobs/:queueName/:jobId/retry`) |
| **Short Description** | Admin-only REST API (guarded by `@SleekBackAuth('admin')`) that returns BullMQ job counts grouped by status across all queues, lists job details including payload, failure reasons, and stack traces, and re-enqueues any failed or completed job with its original data. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: auto-mark-for-companies, update-tasks-bulk, team-assignment-sync, subscription-change, offboarding-request queues (all BullMQ/Redis-backed). UI consumer: sleek-billings-frontend Job Queue page (`monitor-job-queue-health`, `retry-failed-queue-jobs`). |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | None (queue state stored in Redis via BullMQ, not MongoDB) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. `team-assignment-sync` queue is injected in the service but absent from the `QUEUE_NAMES` allowlist in `list-jobs-query.dto.ts` — is this an oversight or intentional? 2. What BullMQ retry limits / backoff strategies are configured per queue? 3. Is `@SleekBackAuth('admin')` restricted to internal tooling only or accessible from customer-facing surfaces? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Auth surface

- `@SleekBackAuth('admin')` applied at controller class level (`queue-jobs.controller.ts:14`) — all endpoints require admin role.

### Endpoints (`queue-jobs.controller.ts`)

| Method | Route | Description |
|---|---|---|
| `GET` | `/queue-jobs` | Job counts for all queues, grouped by status (waiting, active, completed, failed, delayed, etc.) |
| `GET` | `/queue-jobs/jobs` | List jobs with full payload, failure reason, stacktrace, timestamps, attemptsMade. Filterable by `queue` and `status`; default limit 50, max 1 000. |
| `POST` | `/queue-jobs/jobs/:queueName/:jobId/retry` | Retry a single job by queue name + job ID. Allowed only when job state is `failed` or `completed`. |

### Queues managed (`queue-jobs.service.ts:74–80`)

```ts
const PROJECT_QUEUE_NAMES = [
  AUTO_MARK_FOR_COMPANIES_QUEUE,   // 'auto-mark-for-companies'
  UPDATE_TASKS_BULK_QUEUE,         // 'update-tasks-bulk'
  TEAM_ASSIGNMENT_SYNC_QUEUE,      // 'team-assignment-sync'
  SUBSCRIPTION_CHANGE_QUEUE,       // 'subscription-change'
  OFFBOARDING_REQUEST_QUEUE,       // 'offboarding-request'
]
```

### Retry mechanics (`queue-jobs.service.ts:257–280`)

- Calls `job.retry(state)` (BullMQ native retry) where `state` is `'failed'` or `'completed'`.
- After re-queue, updates the job's `timestamp` key in Redis to `Date.now()` so the retried job sorts correctly (newest-first) in subsequent list queries.
- Throws `NotFoundException` if job ID is not found in the queue; `BadRequestException` if current state is not `failed` or `completed`.

### Query DTO (`list-jobs-query.dto.ts`)

- `queue`: enum of named queues or `'all'` (note: `team-assignment-sync` is in the service but **not** in this enum).
- `status`: full BullMQ status set — `wait`, `waiting`, `active`, `completed`, `failed`, `delayed`, `paused`, `prioritized`, `waiting-children`, or `all`.
- `limit`: integer 1–1000, default 50.
