# Review Offboarding Requests

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Offboarding Requests |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Sleek internal operator) |
| **Business Outcome** | Gives operators a filtered, searchable view of all client offboarding requests and full contextual detail per request—company profile, targeted subscriptions, and a timestamped activity log—so they can efficiently triage and act on churn signals. |
| **Entry Point / Surface** | Sleek Billings App > Offboarding Requests list → `GET /offboarding-requests`; detail at `GET /offboarding-requests/:id` |
| **Short Description** | Exposes a paginated, filterable list of offboarding requests (by status, request type, and company name search) and a detail endpoint that aggregates the request record with its linked company, resolved subscription records, and full activity history. Both surfaces are protected by SleekBack internal auth. |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | CompaniesService (company profile enrichment); SubscriptionsService + SleekBillingsService (subscription resolution and sync); BullMQ `offboarding-request` queue (automatic request processing); Sleek Back Auth guard; Manage Offboarding Request Lifecycle (action endpoints on the same controller) |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL — `offboarding_requests`, `offboarding_request_activities`, `subscriptions`, `companies`, `users` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Does `@SleekBackAuth()` enforce role-level scoping (e.g. only certain operator roles can view all requests), or is any authenticated back-office user granted full read access? Exact market scope inferred from subscription/company context — not explicitly gated in backend code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `offboarding-requests/offboarding-requests.controller.ts`

- Guard: `@SleekBackAuth()` on the entire controller — endpoints are restricted to authenticated Sleek internal (back-office) users.
- `GET /offboarding-requests` → `getOffboardingRequestList(params)` — paginated list with query filters.
- `GET /offboarding-requests/:id` → `getOffboardingRequestById(id)` — full detail view with joins.

### `offboarding-requests/offboarding-requests.service.ts` — `getOffboardingRequestList`

- Default page size: 20; default sort: `requestDate DESC`.
- Filters available via `GetOffboardingRequestListDto`:
  - `statuses` — multi-value enum (`pending`, `approved`, `to_be_reviewed`, `rejected`, `completed`, `cancelled`)
  - `requestTypes` — multi-value enum (8 values: partial/full churn, strike-off, archive — each by client or Sleek)
  - `searchTerm` — case-insensitive LIKE match on `company.name`
  - `sortBy` — `requestDate` (default) or `lastPaidInvoiceDate`
  - `sortOrder` — `ASC` / `DESC`
- Left-joins `company` relation so company name is available for search and display in the list row.
- Returns standard paginated envelope: `docs`, `totalDocs`, `totalPages`, `page`, `hasPrevPage`, `hasNextPage`, etc.

### `offboarding-requests/offboarding-requests.service.ts` — `getOffboardingRequestById`

- Loads `OffboardingRequest` with relations `offboardingInChargeUser` and `company`.
- Resolves `subscriptionIds[]` via `subscriptionRepository.find({ where: { id: In(subscriptionIds) } })`.
- Loads all `OffboardingRequestActivity` records for the request, ordered `createdAt DESC`, with `actionByUser` joined.
- Falls back to `actionByUserInfo` (JSONB snapshot) when `actionByUser` relation is null — ensures actor name is always resolvable even if the internal user record is deleted.
- Returns `OffboardingRequestDetails = OffboardingRequest & { company, subscriptions, activities }`.

### `offboarding-requests/entities/offboarding-request.entity.ts` — table `offboarding_requests`

- Key columns: `companyId`, `subscriptionIds` (uuid[]), `requestType`, `reason`, `autoCreatedReason`, `requestDate`, `status`, `requestedBy`, `comments`, `reasonForRejection`, `offboardingInChargeUserId`, `zendeskLink`, `source`, `lastPaidInvoiceDate`.
- `source`: `automatic` (system-generated via SleekBillings churn detection) or `manual`.
- `requestType` (8 variants): `partial_churn_requested_by_client`, `partial_churn_requested_by_sleek`, `full_churn_requested_by_client`, `full_churn_requested_by_sleek`, `strike_off_requested_by_client`, `strike_off_requested_by_sleek`, `archive_requested_by_client`, `archive_requested_by_sleek`.
- Composite indexes on `(companyId, source)`, `(companyId, status)`, `(companyId, requestType, status)`, `(companyId, requestDate)`.

### `offboarding-requests/entities/offboarding-request-activity.entity.ts` — table `offboarding_request_activities`

- Captures every state transition: actions `create`, `update`, `approve`, `reject`, `cancel`, `complete`, `submit_for_review`.
- Stores `oldValue` and `newValue` as JSONB snapshots of the changed fields.
- `actionByUserInfo` JSONB snapshot (`external_ref_id`, `email`, `firstName`, `lastName`) preserves actor identity independent of the user FK.
- Index on `(offboardingRequestId, createdAt)` for efficient activity timeline queries.
