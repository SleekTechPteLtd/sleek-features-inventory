# Manage Client Offboarding Requests

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Client Offboarding Requests |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User; System (automatic detection) |
| **Business Outcome** | Enables operations teams to systematically process client departures — approving, rejecting, escalating, and completing churn and exit requests — while automatically surfacing at-risk clients based on billing signals, so subscription lifecycle changes and revenue recognition are applied consistently across all exit scenarios. |
| **Entry Point / Surface** | Service Delivery API > `GET/PUT /offboarding-requests` (consumed by Sleek Billings Frontend > Offboarding Requests); daily scheduler (5 AM UTC) |
| **Short Description** | Backend module managing the full lifecycle of client offboarding requests. Operations staff advance requests through a multi-step workflow (pending → to-be-reviewed → approved → completed, or rejected/cancelled); each status transition cascades to subscription service delivery states in SleekBillings (toOffboard, discontinued, reactivated) and cancels renewals on approval. A BullMQ-backed daily scheduler automatically creates and updates offboarding requests for companies with subscriptions 90+ days past renewal or inactive for 1 year, processing candidates in batches of 500 with concurrency 10. |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | SleekBillingsService — subscription delivery status updates, renewal cancellations, automatic candidate detection; CompaniesService — company sync from SleekBack; SubscriptionsService — subscription sync; Tasks module — task completion status checked to determine correct delivery status on cancellation; BullMQ queue (`offboarding-request`); sleek-billings-frontend (UI consumer) |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL: `offboarding_requests`, `offboarding_request_activities` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Are the 90-day churn and 1-year inactivity thresholds configurable or hardcoded? 2. Does `@SleekBackAuth()` enforce role-based restrictions (e.g. only specific tiers can approve vs. complete)? 3. Are there downstream hooks to Xero or ERPNext when an offboarding is completed, beyond SleekBillings subscription updates? 4. Which markets are in scope — entity has no explicit market field; SG/HK/AU/UK inferred from frontend company identifier display. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `src/offboarding-requests/offboarding-requests.controller.ts`

- Auth guard: `@SleekBackAuth()` — all endpoints restricted to authenticated Sleek Back (internal operations) users.
- `GET /offboarding-requests` — paginated list; query params: `statuses[]`, `requestTypes[]`, `searchTerm`, `page`, `limit`, `sortBy` (requestDate | lastPaidInvoiceDate), `sortOrder` (ASC | DESC).
- `GET /offboarding-requests/:id` — detail view; returns request + hydrated `company`, `subscriptions[]`, `activities[]`.
- `PUT /offboarding-requests/:id/approve` — transitions to `approved`; requires `requestType`, `reason`, `offboardingInChargeUserId`, `zendeskLink`.
- `PUT /offboarding-requests/:id/reject` — transitions to `rejected`; requires `reasonForRejection`.
- `PUT /offboarding-requests/:id/submit-for-review` — transitions to `to_be_reviewed`.
- `PUT /offboarding-requests/:id/complete` — transitions to `completed`.
- `PUT /offboarding-requests/:id/cancel` — transitions to `cancelled`.
- `POST /offboarding-requests/trigger-automatic-requests` — manual trigger for the automatic offboarding scheduler (for ops/admin use).

### Entity — `src/offboarding-requests/entities/offboarding-request.entity.ts`

PostgreSQL table: **`offboarding_requests`**

Key fields:
- `companyId` (UUID, FK → `companies`)
- `subscriptionIds` (UUID[])
- `requestType` enum: `partial_churn_requested_by_client`, `partial_churn_requested_by_sleek`, `full_churn_requested_by_client`, `full_churn_requested_by_sleek`, `strike_off_requested_by_client`, `strike_off_requested_by_sleek`, `archive_requested_by_client`, `archive_requested_by_sleek`
- `status` enum: `pending`, `approved`, `to_be_reviewed`, `rejected`, `completed`, `cancelled`
- `source` enum: `automatic`, `manual`
- `autoCreatedReason` enum: `full_churn_company`, `partial_churn_company`, `inactive_company`
- `offboardingInChargeUserId` (UUID, nullable, FK → `users`)
- `zendeskLink`, `reasonForRejection`, `comments` (text, nullable)
- `lastPaidInvoiceDate` (timestamp, nullable)
- Indexes on `(companyId, source)`, `(companyId, status)`, `(companyId, requestType, status)`, `(companyId, requestDate)`

### Activity Entity — `src/offboarding-requests/entities/offboarding-request-activity.entity.ts`

PostgreSQL table: **`offboarding_request_activities`**

- Tracks every state change with `action` enum: `create`, `update`, `approve`, `reject`, `cancel`, `complete`, `submit_for_review`.
- Stores `oldValue` / `newValue` as JSONB snapshots of the changed fields.
- `actionByUserInfo` (JSONB) snapshots actor details at time of action (handles deleted users).
- Index on `(offboardingRequestId, createdAt)`.

### Service — `src/offboarding-requests/offboarding-requests.service.ts`

**Status transition side-effects:**
- **Approve**: calls `sleekBillingsService.updateServiceDeliveryStatus(subscriptionRefId, toOffboard)` and `sleekBillingsService.cancelRenewal(subscriptionRefId)` for all linked subscriptions (skips cancel if already `cancelled`). Re-syncs subscriptions after.
- **Cancel**: restores subscription delivery status — `delivered` if all tasks are done, `active` if subscription has started, `toBeStarted` otherwise — by checking `tasks` table via `TaskRepository`.
- **Complete**: sets delivery status to `discontinued` for all linked subscriptions.

**Automatic request creation** (`processAutomaticOffboardingRequests`):
- Queries `sleekBillingsService.getAutomaticOffboardingCandidates(90DaysAgo, 1YearAgo)` for churn signals.
- Batches candidates (500 per batch) into BullMQ queue `offboarding-request` as `automatic-offboarding-request` jobs.
- Per candidate: finds-or-creates the company via `companiesService.findOrCreateCompanyFromSleekBack`; syncs subscriptions; upserts the pending automatic request (updating it if data changed, skipping if unchanged, removing it if company is no longer live).
- Churn reasons defined in constants: `SUBSCRIPTION_CHURN_REASON` ("subscription more than 90 days past renewal due"), `INACTIVE_COMPANY_FULL_CHURN_REASON` ("no active subscription for the past year").

### Scheduler — `src/offboarding-requests/offboarding-requests-scheduler.service.ts`

- `@Cron(EVERY_DAY_AT_5AM, { utcOffset: UTC_OFFSET })` — fires daily, calls `processAutomaticOffboardingRequests`.

### Processor — `src/offboarding-requests/offboarding-requests.processor.ts`

- BullMQ `@Processor('offboarding-request', { concurrency: 10 })`.
- Handles job name `automatic-offboarding-request` by calling `processAutomaticOffboardingRequestCandidate`.

### Constants — `src/offboarding-requests/offboarding-request.constant.ts`

- Queue name: `offboarding-request`
- Job name: `automatic-offboarding-request`
- Batch size: 500
- Churn signal thresholds: 90 days past renewal (partial/full churn), 1 year inactive (full churn)
