# Sync Billing Subscriptions and Provision Deliverables

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Sync Billing Subscriptions and Provision Deliverables |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Keeps the service delivery platform's subscription records in sync with the billing system and automatically creates or recreates deliverables — and updates task statuses — whenever a subscription is purchased, its dates change, or its delivery status is updated, so delivery teams can begin work without manual data entry. |
| **Entry Point / Surface** | Background system — no UI surface; triggered by MongoDB Change Stream on the billing database |
| **Short Description** | A MongoDB Change Stream listener watches the billing system's `customersubscriptions` collection for inserts and relevant field updates (`financialYearEnd`, `subscriptionStartDate`, `subscriptionEndDate`, `serviceDeliveryStatus`). Each change event is enqueued in a BullMQ queue (concurrency 1 for ordering). The queue processor upserts the subscription into Supabase, then either creates deliverables (new subscription with valid dates), recreates deliverables (date/FYE change), or updates linked task statuses (delivery status change). |
| **Variants / Markets** | SG, HK, AU |
| **Dependencies / Related Flows** | Sleek Billings (MongoDB, `customersubscriptions` collection — source of truth); Deliverables module (`DeliverablesQueueService.createDeliverables`, `recreateDeliverables`); Tasks module (`TasksService.updateTasksBySubscriptionDeliveryStatus`); SubscriptionFyGroups module (FY grouping logic); BullMQ / Redis (job queue); `SleekBillingsService.findCustomerSubscription` (fetches full subscription document from MongoDB for upsert) |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | MongoDB (Sleek Billings): `customersubscriptions` (watched via change stream, read on upsert); PostgreSQL (Supabase): `subscriptions`, `deliverables`, `tasks` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Is UK market supported? Entity priority labels only reference SG, HK, and AU variants. On insert, failed deliverables creation is logged as a warning but not retried — is this acceptable for production? Change stream reconnect is capped at 10 attempts with no alerting; what monitors for permanent reconnect failure? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Change stream listener
`src/subscriptions/listeners/customer-subscription-change-stream.listener.ts`

- Implements `OnModuleInit` / `OnModuleDestroy`; disabled when `APP_TYPE=scheduler` or `DISABLE_CHANGE_STREAM=true`
- Connects to MongoDB at `SLEEK_BILLINGS_DB_MONGODB_URI` with a capped connection pool (max 10)
- Watches `db.collection('customersubscriptions')` with an aggregation pipeline filter for:
  - `operationType: 'insert'`
  - `updateDescription.updatedFields.financialYearEnd` exists
  - `updateDescription.updatedFields.serviceDeliveryStatus` exists
  - `updateDescription.updatedFields.subscriptionStartDate` exists
  - `updateDescription.updatedFields.subscriptionEndDate` exists
- Uses `fullDocument: 'updateLookup'` to include the complete document on each event
- Delegates to `SubscriptionChangeQueueService.addChangeEvent(change)` for deduplication and queuing
- Reconnects with exponential backoff (base 1 s, max 60 s, up to 10 attempts)

### Queue service
`src/subscriptions/change-stream/services/subscription-change-queue.service.ts`

- Adds change events to the `SUBSCRIPTION_CHANGE_QUEUE` BullMQ queue
- Generates a unique `jobId` from `documentKey._id`, `operationType`, and `resumeToken` to prevent duplicate processing across replicas
- Completed jobs retained 1 hour / 1 000 count; failed jobs retained 7 days

### Queue processor
`src/subscriptions/queues/subscription-change.processor.ts` — `SubscriptionChangeProcessor`

- `@Processor(SUBSCRIPTION_CHANGE_QUEUE, { concurrency: 1 })` — single-threaded to preserve event order
- **Insert**: skips if `subscriptionGroupingCriteria === 'financial_year'` and no `financialYearEnd`; skips if no start/end dates; otherwise calls `DeliverablesQueueService.createDeliverables({ externalRefId, createdBy: masterUser.id })`
- **Update — date fields** (`financialYearEnd`, `subscriptionStartDate`, `subscriptionEndDate` changed): calls `DeliverablesQueueService.recreateDeliverables(documentId, masterUser.id)`
- **Update — `serviceDeliveryStatus`** changed: calls `SubscriptionsService.updateTasksByDeliveryStatus(documentId, newStatus, masterUser.id)`
- Uses a cached master user (`isMasterUser: true`) from the `users` table as the `createdBy` / `updatedBy` actor

### Subscriptions service — sync and task update
`src/subscriptions/services/subscriptions.service.ts`

- `syncSubscription(externalRefId, companyId, mongoDoc)` — upserts into `subscriptions` table on conflict of `external_ref_id`; updates `name`, `code`, `financialYearEnd`, `subscriptionStartDate`, `subscriptionEndDate`, `paymentDate`, `serviceDeliveryStatus`, `subscriptionGroupingCriteria`, `subscriptionRenewalStatus`, `billingCycle`
- `findAndSyncSubscription(externalRefId, companyId)` — fetches from MongoDB via `SleekBillingsService.findCustomerSubscription` then calls `syncSubscription`
- `updateTasksByDeliveryStatus(externalRefId, deliveryStatus, updatedByUserId)` — syncs the subscription, then calls `TasksService.updateTasksBySubscriptionDeliveryStatus`; skips task revert when transitioning `delivered → active` to protect `NOT_REQUIRED` tasks

### Subscription entity
`src/subscriptions/entities/subscription.entity.ts` — `@Entity('subscriptions')`

Key columns: `external_ref_id` (unique, FK to billing MongoDB `_id`), `subscriptionRefNumber`, `code`, `financialYearEnd`, `subscriptionStartDate`, `subscriptionEndDate`, `serviceDeliveryStatus` (enum), `subscriptionGroupingCriteria`, `subscriptionRenewalStatus`, `billingCycle`, `companyId`, `fyGroupId`
