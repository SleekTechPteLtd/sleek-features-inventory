# Monitor Job Queue Health

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor Job Queue Health |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Operations User) |
| **Business Outcome** | Operators can inspect the real-time health of background processing across all queues, identify failures, and manually re-trigger failed jobs to recover without engineering intervention. |
| **Entry Point / Surface** | Sleek Billings App > Job Queue; backend at `GET /queue-jobs` and `GET /queue-jobs/jobs` |
| **Short Description** | Displays BullMQ job counts per queue and aggregated by status (waiting, active, completed, failed, delayed, etc.). Admins can drill into individual job payloads, failure reasons, and retry any failed or completed job directly from the UI. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: any feature that enqueues background jobs — subscriptions, deliverables, team assignments, offboarding. Downstream: `POST /queue-jobs/jobs/:queueName/:jobId/retry` re-queues failed jobs. UI in `sleek-billings-frontend`. |
| **Service / Repository** | sleek-service-delivery-api (backend); sleek-billings-frontend (UI, `VITE_SERVICE_DELIVERY_API_URL`) |
| **DB - Collections** | None (BullMQ persists job state in Redis, not MongoDB) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. What markets/environments is this deployed to — SG only or also HK/AU/UK? 2. The "Others" tab in the UI captures statuses outside active/waiting/completed/failed — what statuses appear in practice (delayed, paused, prioritized)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Backend — `src/queue-jobs/queue-jobs.controller.ts`

- **Auth:** `@SleekBackAuth('admin')` on the entire controller — admin role required for all endpoints.
- **Endpoints:**
  - `GET /queue-jobs` — returns job counts for all registered queues, per-queue and totals by status (`waiting`, `active`, `completed`, `failed`, `delayed`, etc.)
  - `GET /queue-jobs/jobs?queue=&status=&limit=` — returns up to 1,000 job records (id, name, data, status, failedReason, stacktrace, timestamps, attemptsMade) for one queue or all queues, optionally filtered by status. Defaults: queue=all, status=all, limit=50.
  - `POST /queue-jobs/jobs/:queueName/:jobId/retry` — retries a job; job must be in `failed` or `completed` state.

### Backend — `src/queue-jobs/queue-jobs.service.ts`

- **Registered queues (5 total):**
  - `auto-mark-for-companies` — auto-marks tasks for companies
  - `update-tasks-bulk` — bulk task updates
  - `team-assignment-sync` — syncs team assignments
  - `subscription-change` — processes subscription changes
  - `offboarding-request` — handles offboarding requests
- `getJobsGroupedByStatus()` calls `queue.getJobCounts()` on each queue and aggregates totals across all queues.
- `getJobsWithData()` fetches job records with full payload, failure reason, and stacktrace for UI display.
- `retryJob()` calls `job.retry(state)` and resets `timestamp` so retried jobs sort correctly when listed.
- All queue interaction is via BullMQ (`Queue`, `Job` from `bullmq`); state stored in Redis.

### UI — `src/pages/JobQueue/JobQueue.jsx` (sleek-billings-frontend)

- **Status tabs:** In Progress (`active`), Pending (`waiting`), Completed, Failed, Others
- **Columns:** Job ID, Queue Name, Data (expandable JSON modal), Timestamp; Failed tab adds Failed Reason and Rerun button
- **Refresh:** Manual "Refresh" button — no auto-polling
- **Rerun flow:** Confirmation dialog → `POST /queue-jobs/jobs/{queueName}/{jobId}/retry` → re-fetch list

### Service layer — `src/services/service-delivery-api.js` (sleek-billings-frontend)

```js
getQueueJobs: () => serviceDeliveryApi.get("/queue-jobs/jobs?limit=1000")
rerunQueueJob: (queueName, jobId) =>
  serviceDeliveryApi.post(`/queue-jobs/jobs/${encodeURIComponent(queueName)}/${encodeURIComponent(jobId)}/retry`)
```
