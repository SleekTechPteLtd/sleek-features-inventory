# Automatic Churn Offboarding Detection

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Automatic Churn Offboarding Detection |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Ensures churning clients are surfaced to operators daily without manual triage, so offboarding action can be taken before accounts become stale or revenue leaks unnoticed. |
| **Entry Point / Surface** | System — scheduled cron job (daily 5 AM, UTC offset configurable via env) |
| **Short Description** | Every day the platform queries billing data to find clients with churn signals (subscriptions overdue ≥ 90 days or no active subscriptions for ≥ 1 year) and automatically creates or refreshes pending offboarding requests in the service-delivery database, ready for operator review. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | SleekBillings API (MongoDB candidate queries, subscription updates); CompaniesService (SleekBack company sync); SubscriptionsService (subscription sync); BullMQ queue `offboarding-request`; Review Offboarding Request Details; Manage Offboarding Request Lifecycle |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL: `offboarding_requests`, `offboarding_request_activities`, `companies`, `subscriptions`, `tasks`; MongoDB (SleekBillings): `customersubscriptions`, `invoices` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | UTC offset for the 5 AM cron is env-driven — confirm which timezone is used in each deployed environment. No market-specific filtering logic found; unclear if detection rules differ per market (SG/HK/UK/AU). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Scheduler
`offboarding-requests/offboarding-requests-scheduler.service.ts`
- `@Cron(CronExpression.EVERY_DAY_AT_5AM, { utcOffset: process.env.UTC_OFFSET })` → calls `processAutomaticOffboardingRequests()`

### Candidate detection
`sleek-billings/services/sleek-billings.service.ts` → `getAutomaticOffboardingCandidates(ninetyDaysAgo, oneYearAgo)`

Two candidate sets queried from MongoDB `customersubscriptions`:

1. **Subscription churn candidates** — subscriptions with `serviceDeliveryStatus` in `['active', 'toBeStarted']`, `subscriptionRenewalStatus = 'cancelled'`, and `subscriptionEndDate` null or ≤ 90 days ago. Grouped per company:
   - All eligible → `FULL_CHURN_REQUESTED_BY_SLEEK` / `autoCreatedReason: full_churn_company`
   - Some eligible → `PARTIAL_CHURN_REQUESTED_BY_SLEEK` / `autoCreatedReason: partial_churn_company`

2. **Inactive company candidates** — companies with zero active/toBeStarted subscriptions whose latest paid invoice (`invoices` collection) is ≤ 1 year old ago → `FULL_CHURN_REQUESTED_BY_SLEEK` / `autoCreatedReason: inactive_company`

Constant reasons:
- `SUBSCRIPTION_CHURN_REASON` = "The client has a subscription more than 90 days past renewal due"
- `INACTIVE_COMPANY_FULL_CHURN_REASON` = "The client has no active subscription for the past year"

### Queue dispatch
`offboarding-requests/offboarding-requests.service.ts` → `processAutomaticOffboardingRequests()`
- Batches candidates into BullMQ queue `offboarding-request` in groups of 500 (`AUTOMATIC_OFFBOARDING_QUEUE_BATCH_SIZE`)
- Job name: `automatic-offboarding-request`

### Queue processing
`offboarding-requests/offboarding-requests.processor.ts`
- `@Processor(OFFBOARDING_REQUEST_QUEUE, { concurrency: 10 })`
- Dispatches each job to `processAutomaticOffboardingRequestCandidate()`

### Per-candidate processing
`offboarding-requests/offboarding-requests.service.ts` → `processAutomaticOffboardingRequestCandidate()`
- Resolves or creates the company via `CompaniesService.findOrCreateCompanyFromSleekBack()`
- If company status is not `LIVE` or `LIVE_POST_INCORPORATION`: removes any existing automatic+PENDING offboarding request and exits
- Syncs subscriptions from SleekBillings if not already in the local DB
- Checks for open requests (`PENDING`, `APPROVED`, `TO_BE_REVIEWED`):
  - Existing **manual** or non-PENDING open request → skips (does not overwrite human-initiated requests)
  - Existing **automatic+PENDING** request with changed data → updates fields and logs `UPDATE` activity
  - No open request → creates new `OffboardingRequest` with `source: automatic`, `status: pending`, `requestedBy: system`
- All mutations are recorded as `OffboardingRequestActivity` entries

### Entities
`offboarding-requests/entities/offboarding-request.entity.ts`
- Table: `offboarding_requests`
- Key fields: `companyId`, `subscriptionIds[]`, `requestType`, `reason`, `autoCreatedReason`, `status`, `source`, `lastPaidInvoiceDate`
- `OffboardingRequestSource.AUTOMATIC` distinguishes system-generated records from manual ones
