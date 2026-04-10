# Manage Client Service Subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage client service subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Sleek operator / admin) |
| **Business Outcome** | Enables Sleek operators to oversee the full lifecycle of client service subscriptions — browsing, filtering by urgency and assignee, and propagating delivery status changes to downstream tasks — so no service obligation falls through the cracks. |
| **Entry Point / Surface** | Internal Ops Portal > Subscriptions (backed by `sleek-service-delivery-api` REST API at `/subscriptions`) |
| **Short Description** | Operators browse a paginated subscription list filterable by free-text search, assignee, priority labels, financial year end, company team assignment, and delivery status, with an overdue-tasks count per row. Updates to a subscription's delivery status (inactive, discontinued, or deactivated) cascade automatically to mark related tasks as NOT_REQUIRED. Subscription data is kept in sync with SleekBillings (MongoDB) via an upsert on external reference ID. |
| **Variants / Markets** | SG, HK, AU |
| **Dependencies / Related Flows** | SleekBillings (MongoDB) — source of truth for subscription data synced via `syncSubscription`; Tasks module — delivery status change cascades to task status updates; SubscriptionFyGroups module — loads deliverables for financial-year-grouped subscriptions; Deliverables module — joined for overdue count and relation hydration; Team Assignments — joined for `companyAssigneeIds` filter |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL (Supabase): `subscriptions`, `deliverables`, `tasks`, `team_assignments`; MongoDB (SleekBillings): customer subscriptions (read-only for sync) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. No UK-specific priority labels found in `SubscriptionPriorityLabel` enum — is UK market supported for this feature? 2. Is subscription creation (`POST /subscriptions`) done manually by operators or only triggered programmatically via sync from SleekBillings? 3. Which frontend app or internal tool surfaces this API to operators? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Auth surface
- `@SleekBackAuth('admin')` on `SubscriptionsController` — all endpoints are admin-only internal access.

### Endpoints (`subscriptions/controllers/subscriptions.controller.ts`)
| Method | Route | Purpose |
|---|---|---|
| `POST` | `/subscriptions` | Create a new subscription |
| `GET` | `/subscriptions` | List subscriptions with pagination and filters |
| `GET` | `/subscriptions/by-external-ref/:external_ref_id` | Lookup by SleekBillings external ref ID |
| `POST` | `/subscriptions/by-external-ref/:external_ref_id` | Sync from SleekBillings and cascade delivery status to tasks |
| `GET` | `/subscriptions/:id` | Get single subscription by internal ID |
| `PATCH` | `/subscriptions/:id` | Update subscription fields |
| `DELETE` | `/subscriptions/:id` | Delete subscription |

### Filtering capabilities (`subscription-pagination-query.dto.ts`)
- `search` — LIKE match on `subscription.name`, `subscription.code`, `subscription.subscriptionRefNumber`, `company.name`
- `assignedUserId` — EXISTS subquery: subscriptions with at least one non-archived task assigned to this user
- `priorityLabels` — PostgreSQL array overlap (`&&`) on `subscription.priorityLabels`
- `serviceFyeYears` — EXTRACT(YEAR) filter on `subscription.financialYearEnd`
- `companyAssigneeIds` — EXISTS subquery on `team_assignments` table
- `deliveryStatuses` — IN filter on `subscription.serviceDeliveryStatus`

### Overdue tasks count (`subscriptions.service.ts:242–328`)
Computed via a subquery counting `tasks` with `status = TO_DO` and `dueDate < today`, grouped by `subscriptionId`, and left-joined onto the pagination query. Returned as `overdueTasksCount` per subscription row.

### Delivery status cascade (`subscriptions.service.ts:456–508`)
- `updateTasksByDeliveryStatus` syncs latest data from MongoDB then calls `tasksService.updateTasksBySubscriptionDeliveryStatus`
- Only cascades when status is inactive, discontinued, or deactivated (converts TO_DO tasks → NOT_REQUIRED)
- Guard: if transitioning from `delivered` → `active`, cascade is skipped to avoid reverting NOT_REQUIRED tasks

### FY group handling (`subscriptions.service.ts:86–107`)
- Subscriptions with `subscriptionGroupingCriteria = financial_year` load their deliverables from the `subscription_fy_groups` table via `SubscriptionFyGroupsService`, not directly from the `deliverables` relation.

### Entity fields (`subscriptions/entities/subscription.entity.ts`)
- Key fields: `external_ref_id` (unique, links to SleekBillings), `subscriptionRefNumber` (unique), `code`, `financialYearEnd`, `serviceDeliveryStatus`, `priorityLabels` (text array), `subscriptionGroupingCriteria`, `billingCycle`, `subscriptionRenewalStatus`
- Relations: `company` (ManyToOne → Company), `deliverables` (OneToMany → Deliverable), `fyGroup` (ManyToOne → SubscriptionFyGroup)

### Market-specific priority labels
- **SG**: AGM Due Soon, Client Escalation, High Transaction Volume, Sleek ND, Unresponsive Client
- **HK**: PTR Received, Court Summons Received, Penalties Received, Client Escalation, High Transaction Volume, Unresponsive Client
- **AU**: ATO Due Soon, BAS Due Soon, Compliance Action Required, Client Escalation, Critical Business Event, Backlog Work, Complex Transactions, High Transaction Volume, Unresponsive Client

### External dependency
- `SleekBillingsService` (`src/sleek-billings/services/sleek-billings.service.ts`) — connects to MongoDB via `MongoClient`, fetches `CustomerSubscriptionResult` for upsert sync
