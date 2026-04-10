# Manage Offboarding Request Lifecycle

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM (Client Lifecycle Management) |
| **Feature Name** | Manage Offboarding Request Lifecycle |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Sleek internal operator) |
| **Business Outcome** | Enables operators to drive a client offboarding request through its full lifecycle — from initial review to approval, submission for review, completion, rejection, or cancellation — with structured reason capture and assignee accountability at each decision point, creating a documented audit trail of the offboarding outcome. |
| **Entry Point / Surface** | Sleek Billings App > Offboarding Requests > [Request Detail View] |
| **Short Description** | Operators view a single offboarding request and take lifecycle actions (approve, reject, submit for review, complete, cancel). Each action opens a modal capturing structured data (request type, churn reason, rejection reason, assignee, Zendesk link, comments) before committing the status transition. An activity log renders the full audit trail. |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | sleek-back-api (company details lookup); sleekServiceDeliveryApi (offboarding CRUD + transitions); sleek-billings (MongoDB: updateServiceDeliveryStatus, cancelRenewal — called on approve, cancel, complete); BullMQ `offboarding-request` queue (automatic request processing); Zendesk (linked ticket URL captured on approve); AssigneeSelect component (operator assignment); Offboarding Requests list view (navigation parent) |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL (sleek-service-delivery-api): `offboarding_requests`, `offboarding_request_activities`, `subscriptions` (read/write), `companies` (read), `tasks` (read — used to infer restored delivery status on cancel) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Are there role-level guards on approve/reject beyond `@SleekBackAuth()`, or is any authenticated operator able to take all actions? Is `submitForReview` ever triggered automatically, or always manual? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/Offboarding/OffboardingRequestDetails.jsx` — main detail page component
- `src/services/service-delivery-api.js` — API client with all offboarding action methods

### Status lifecycle
Statuses (from `src/lib/constants.jsx`):
- `pending` → operator can **approve** or **reject**
- `approved` → operator can **submit for review** or **cancel**
- `to_be_reviewed` → operator can **complete** or **cancel**
- `rejected` | `completed` | `cancelled` → terminal, no actions shown

### API endpoints (sleekServiceDeliveryApi)
| Method | Endpoint | Payload |
|---|---|---|
| GET | `/offboarding-requests` | query params (pagination, filter) |
| GET | `/offboarding-requests/:id` | — |
| PUT | `/offboarding-requests/:id/approve` | `requestType`, `reason`, `zendeskLink`, `comments`, `offboardingInChargeUserId` (all required) |
| PUT | `/offboarding-requests/:id/reject` | `reasonForRejection` (required), `comments` |
| PUT | `/offboarding-requests/:id/submit-for-review` | `comments` |
| PUT | `/offboarding-requests/:id/complete` | `comments` |
| PUT | `/offboarding-requests/:id/cancel` | `comments` |

### Cross-service call
- `sleekBackApi.getCompanyDetails(companyRefId)` — fetches enriched company info (name, status, identifiers) from the sleek-back service using the company's `external_ref_id`.

### Request types (8 variants)
`partial_churn_requested_by_client`, `partial_churn_requested_by_sleek`, `full_churn_requested_by_client`, `full_churn_requested_by_sleek`, `strike_off_requested_by_client`, `strike_off_requested_by_sleek`, `archive_requested_by_client`, `archive_requested_by_sleek`

### Structured reason capture
- **Churn reasons**: dropdown scoped per request type (e.g. "Client is MIA", "Outside risk appetite", "Closing business")
- **Rejection reasons**: fixed list (e.g. "Chaser not sent", "30-day lapse not met", "Client recently active")
- **Assignee**: `offboardingInChargeUserId` selected from full operator user list (up to 2000 users)
- **Zendesk link**: free-text URL captured on approval

### Market-specific fields
Platform-conditional company identifier display:
- SG: UEN
- HK: CRN, BRN
- AU: ABN, ACN
- UK: Company Number (labelled as UEN)

### Activity log
`request.activities[]` renders a chronological timeline. Each entry shows: status label, actor name (or "System" with tooltip for auto-flagged), timestamps, and per-status contextual data (assignee, churn reason, rejection reason, comments).

---

### Backend evidence (sleek-service-delivery-api)

**Files**
- `src/offboarding-requests/offboarding-requests.controller.ts` — REST controller, `@SleekBackAuth()` guard, five PUT transition endpoints + GET list/detail
- `src/offboarding-requests/offboarding-requests.service.ts` — state transition logic, subscription side-effects, activity recording
- `src/offboarding-requests/entities/offboarding-request.entity.ts` — PostgreSQL entity, `offboarding_requests` table
- `src/offboarding-requests/entities/offboarding-request-activity.entity.ts` — PostgreSQL entity, `offboarding_request_activities` table
- `src/offboarding-requests/dto/` — DTOs for each transition (approve, reject, cancel, complete, submit-for-review)

**Subscription side-effects per transition**

| Transition | Subscription mutation (via sleekBillingsService) |
|---|---|
| Approve | `updateServiceDeliveryStatus → toOffboard`; `cancelRenewal` if not already cancelled |
| Cancel | `updateServiceDeliveryStatus → delivered / active / toBeStarted` (derived from task completion + subscription start date) |
| Complete | `updateServiceDeliveryStatus → discontinued` |
| Reject | No subscription mutation |
| Submit for review | No subscription mutation |

After each mutation, `subscriptionsService.findAndSyncSubscription` is called to re-sync local PostgreSQL with the billing source.

**Audit activity actions**
`create`, `update`, `approve`, `reject`, `cancel`, `complete`, `submit_for_review` — each stored in `offboarding_request_activities` with `oldValue`/`newValue` JSON diff and actor info snapshot.

**BullMQ queue**
`OFFBOARDING_REQUEST_QUEUE` — used for automatic offboarding request creation/update, not for manual operator transitions.
