# Manage client deliverables

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage client deliverables |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (admin) |
| **Business Outcome** | Gives operators a single view to track and action all deliverables (reports, documents) owed to clients under a subscription, so service commitments are met on time and nothing falls through the cracks. |
| **Entry Point / Surface** | Sleek Billings Admin > Deliverables (`/deliverables`); Analytics sub-page at `/analytics/deliverables`; Internal admin API `POST /deliverables`, `PATCH /deliverables/:id`, `DELETE /deliverables/:id` |
| **Short Description** | Operators create, review, update, and remove deliverables tied to client subscriptions. Deliverables are generated from templates when a subscription is provisioned, carry lifecycle statuses (PENDING → IN_PROGRESS → COMPLETED / CANCELLED / ARCHIVED), due dates, and user assignments. Creation is queued via BullMQ to ensure sequential processing per company; a recreate endpoint archives and regenerates all deliverables when subscription data changes. |
| **Variants / Markets** | SG, HK, AU (ATO reporting integration present), UK likely — confirm per market rollout |
| **Dependencies / Related Flows** | Deliverable Templates (source of truth for deliverable shape); Tasks (child records under each deliverable); Subscriptions (parent); Subscription FY Groups (for monthly-billed annual subscriptions); Auto-Mark Rules; ATO Reporting Requirements (AU); SleekBillings API (MongoDB subscription source); Companies service |
| **Service / Repository** | sleek-service-delivery-api (backend); sleek-billings-frontend (admin UI) |
| **DB - Collections** | PostgreSQL (TypeORM): `deliverables`, `subscriptions`, `companies`, `deliverable_templates`, `tasks`, `task_activities`, `team_assignments`, `subscription_fy_groups`, `users`; MongoDB (read-only via SleekBillingsService): customer subscriptions |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) Nav entry for `/deliverables` is commented out in the frontend — is the list page still in development or intentionally hidden behind a flag? (2) Markets not explicitly scoped in backend config — AU is implied by ATO reporting dependency. (3) `createdBy` field on recreate/sync endpoints — what system identity populates this in practice? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Backend — `sleek-service-delivery-api`

#### Controller — `src/deliverables/controllers/deliverables.controller.ts`
- Auth guard: `@SleekBackAuth('admin')` on the entire controller — admin-only internal surface.
- Endpoints:
  - `POST /deliverables` — creates deliverables from templates matching the subscription code; routed through BullMQ queue (`DeliverablesQueueService.createDeliverables`) so creation is sequential per company.
  - `GET /deliverables` — paginated list with `DeliverablePaginationQueryDto` filters.
  - `GET /deliverables/:id` — fetch single deliverable.
  - `PATCH /deliverables/:id` — update status, dueDate, assignedUserId, etc.
  - `DELETE /deliverables/:id` — hard delete (204 No Content).
  - `POST /deliverables/recreate/:externalRefId` — archives all existing deliverables and tasks for a subscription then recreates from current billing data; useful when subscription data changes.
  - `POST /deliverables/sync-missing/:externalRefId` — adds missing deliverables from newly added templates without archiving existing records.

#### Queue — `src/deliverables/queues/deliverables-queue.service.ts`
- BullMQ queue (`DELIVERABLES_QUEUE`) backed by Redis.
- Jobs: `CREATE_DELIVERABLES`, `RECREATE_DELIVERABLES`.
- Queue ensures only one deliverable creation job per company runs at a time (Redis distributed lock in processor).
- `job.waitUntilFinished(queueEvents)` — synchronous response despite async queue.

#### Service — `src/deliverables/services/deliverables.service.ts`
- External calls: `SleekBillingsService.findCustomerSubscription(externalRefId)` — fetches subscription from MongoDB.
- `CompaniesService.findOrCreateCompanyFromSleekBack(mongoCompanyId)` — upserts company in PostgreSQL.
- Task frequency calculation: WEEKLY, BI_WEEKLY, MONTHLY, QUARTERLY, ONE_TIME — drives how many task instances are created per deliverable.
- `AutoMarkRulesService` — applies auto-mark rules after deliverable/task creation.
- `AtoReportingRequirementsService` (entry point `AutoMarkATOReportingTaskEntryPoint`) — AU-specific compliance task handling.
- FY Group logic: deliverables for monthly-billed annual subscriptions are grouped under `SubscriptionFyGroup` to share across billing periods.

#### Entity — `src/deliverables/entities/deliverable.entity.ts`
- Table: `deliverables` (PostgreSQL).
- Status enum: `PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `ARCHIVED`.
- Indexed on: `fyGroupId`, `recordStatus`, `status`, `name`, `subscriptionId`.
- Relations: `Subscription` (ManyToOne, CASCADE delete), `DeliverableTemplate` (ManyToOne, CASCADE delete), `User` assignee (ManyToOne, SET NULL), `Task[]` (OneToMany, cascade), `SubscriptionFyGroup` (ManyToOne, SET NULL).

#### DTO — `src/deliverables/dto/create-deliverable.dto.ts`
- Accepts `subscriptionId` (UUID) **or** `externalRefId` (string from SleekBillings) — at least one required.
- Optional: `name`, `description`, `status`, `dueDate`, `assignedUserId`, `createdBy`.

### UI — `sleek-billings-frontend`

#### `src/pages/Deliverables/DeliverablesList.jsx`
- Route: `/deliverables` (registered in `App.jsx`; lazy-loaded). **Nav entry is commented out** — page may be staged/in-progress.
- Table columns: Reference, Customer, Type, Status (badge), Due Date, Assigned To, Last Updated, Priority, Actions.
- Uses `getAllDeliverables`, `createDeliverable`, `updateDeliverable`, `deleteDeliverable` from `src/services/service-delivery-api.js`.

#### `src/pages/Analytics/DeliverablesAnalytics.jsx`
- Route: `/analytics/deliverables` (active, nav entry live).
- Calls `GET /analytics/deliverables` → counts by status: PENDING, IN_PROGRESS, COMPLETED, CANCELLED, ARCHIVED.

#### `src/services/service-delivery-api.js`
- Axios instance to `VITE_SERVICE_DELIVERY_API_URL`.
- Auth: `Authorization: Bearer <JWT>`; `App-Origin: admin`.
- Deliverable endpoints mirror the backend controller above.
- Deliverable Template endpoints also present (related dependency): CRUD + `import-csv`, `export-csv`, lightweight list.
