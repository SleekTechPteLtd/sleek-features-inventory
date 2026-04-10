# Retry failed queue jobs

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Retry failed queue jobs |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operations staff to recover from transient processing failures by re-queuing failed background jobs without data re-entry or manual intervention |
| **Entry Point / Surface** | Sleek Admin App > Job Queue > Failed tab > Rerun (replay) button |
| **Short Description** | Operators open the Job Queue page, navigate to the Failed tab, and click the rerun icon on any failed job. After confirming a dialog, the system POSTs a retry request to the service-delivery-api, which re-enqueues the job with its original data. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Job Queue monitoring (view all jobs across statuses); service-delivery-api `/queue-jobs/jobs` endpoints; underlying queue backend (BullMQ / Redis — not visible from frontend) |
| **Service / Repository** | sleek-billings-frontend, service-delivery-api |
| **DB - Collections** | Unknown (frontend only; queue storage managed by service-delivery-api backend) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | What queue system is used (BullMQ, Redis)? Which job types fail most frequently? Is there a retry limit or cooldown enforced by the backend? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/pages/JobQueue/JobQueue.jsx`
- `handleRerun(job, index)` — calls `sleekServiceDeliveryApi.rerunQueueJob(queueName, jobId)`, then refreshes the full job list via `fetchJobs()` (line 157–177)
- Rerun button (ReplayIcon) is rendered **only** in the Failed tab (`isFailedTab` guard, line 369)
- Confirmation dialog shown before rerun: "This will re-queue the job to the `{queueName}` queue. The job will run again with the same data." (line 397–432)
- Spinner displayed on the row during in-flight retry (`rerunningId` state, line 378)
- Job statuses mapped: `active/processing` → In progress, `waiting/delayed` → Pending, `completed`, `failed`, everything else → Others (line 34–41)
- `fetchJobs` calls `sleekServiceDeliveryApi.getQueueJobs()` → `GET /queue-jobs/jobs?limit=1000` (line 105–118)

### `src/services/service-delivery-api.js`
- `getQueueJobs()` — `GET /queue-jobs/jobs?limit=1000` (line 984–993)
- `rerunQueueJob(queueName, jobId)` — `POST /queue-jobs/jobs/{encodedQueue}/{encodedJobId}/retry` (line 994–1004)
- Base URL: `VITE_SERVICE_DELIVERY_API_URL` env variable
- Auth: Bearer JWT token (`Authorization: Bearer {token}`) or raw token fallback; `App-Origin: admin` / `admin-sso` header (line 10–17)
