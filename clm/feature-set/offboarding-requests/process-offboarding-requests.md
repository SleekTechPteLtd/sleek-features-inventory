# Process Offboarding Requests

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Process Offboarding Requests |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables the operations team to advance clients through the offboarding lifecycle — from approving or rejecting initial requests, assigning responsibility, escalating for senior review, and marking completion or cancellation — so client churn and strike-off workflows are tracked and actioned consistently. |
| **Entry Point / Surface** | Sleek Billings Frontend > Offboarding Requests > [Request Detail] (`/offboarding-requests/:id`) |
| **Short Description** | A detail view for a single offboarding request where operations users can take status-advancing actions: approve (assigning request type, churn reason, offboarding in-charge, and Zendesk link), reject (with rejection reason), submit for review, complete, or cancel. Each action is gated by the request's current status and records an activity log entry. |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | sleek-back-api (company details lookup by external_ref_id); offboarding request list page (`/offboarding-requests`); service-delivery-api offboarding endpoints |
| **Service / Repository** | sleek-billings-frontend, service-delivery-api |
| **DB - Collections** | Unknown (managed by service-delivery-api backend; frontend has no direct DB access) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which backend service owns the `/offboarding-requests` resource — is service-delivery-api the canonical store or does it delegate to another system? 2. Are there role/permission guards on the approve/reject/complete endpoints, or is any authenticated admin user able to perform all actions? 3. Is "Submit for review" intended for a different ops tier (e.g. a senior reviewer), and if so, is that reviewer flow captured in a separate screen? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point & routing
- `pages/Offboarding/OffboardingRequestDetails.jsx` — component mounted at `/offboarding-requests/:id`
- Back button navigates to `/offboarding-requests` with preserved list state (tab, search, filters, sort, page)

### Status lifecycle
Statuses defined in `src/lib/constants.jsx:527–543`:
- `pending` → approve → `approved`
- `pending` → reject → `rejected`
- `approved` → submit-for-review → `to_be_reviewed`
- `approved` → cancel → `cancelled`
- `to_be_reviewed` → complete → `completed`
- `to_be_reviewed` → cancel → `cancelled`

Action buttons rendered conditionally (`OffboardingRequestDetails.jsx:649–790`):
- **Pending**: "Reject request", "Review and approve"
- **Approved**: "Cancel request", "Submit for review"
- **To Be Reviewed**: "Cancel request", "Complete offboarding"

### API calls (`services/service-delivery-api.js:1093–1156`)
| Action | Method | Endpoint |
|---|---|---|
| Fetch detail | GET | `/offboarding-requests/{id}` |
| Approve | PUT | `/offboarding-requests/{id}/approve` |
| Reject | PUT | `/offboarding-requests/{id}/reject` |
| Submit for review | PUT | `/offboarding-requests/{id}/submit-for-review` |
| Complete | PUT | `/offboarding-requests/{id}/complete` |
| Cancel | PUT | `/offboarding-requests/{id}/cancel` |

Auth header: `Authorization: Bearer <JWT>` (OAuth) or raw token; `App-Origin: admin-sso` (or `admin` for alternate login).

### Approve modal required fields (`OffboardingRequestDetails.jsx:299–302`)
- `requestType` — one of 8 types (partial/full churn, strike-off, archive; by client or by Sleek)
- `reason` — churn reason, options vary by request type
- `offboardingInChargeUserId` — assignee selected from all users (`/users?limit=2000`)
- `zendeskLink` — ticket reference

### Request types (`src/lib/constants.jsx:545–573`)
`partial_churn_requested_by_client`, `partial_churn_requested_by_sleek`, `full_churn_requested_by_client`, `full_churn_requested_by_sleek`, `strike_off_requested_by_client`, `strike_off_requested_by_sleek`, `archive_requested_by_client`, `archive_requested_by_sleek`

### Rejection reasons (`OffboardingRequestDetails.jsx:345–356`)
Predefined list including: final email chaser not sent, chaser not lapsed 30 days, no director contact, client recently active, incorrect workflow/type, others.

### Cross-service dependency
- `sleekBackApi.getCompanyDetails(companyRefId)` called after fetching the offboarding request to enrich company info (status, identifiers per market: UEN/SG, CRN+BRN/HK, ABN+ACN/AU, Company Number/UK).

### Activity log
- `request.activities` rendered as a timeline (`ActivityLogEntry` component)
- Each entry records: new status, actor (user or system), offboarding in-charge, request type, churn reason, rejection reason, comments, and timestamp
- System-generated entries (no actor) are flagged as "Automatically flagged for offboarding"
