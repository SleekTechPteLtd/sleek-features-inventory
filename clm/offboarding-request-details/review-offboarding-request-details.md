# Review Offboarding Request Details

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Offboarding Request Details |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operators to assess the full context of a client's offboarding request — company profile, targeted subscriptions, request classification, and a timestamped activity log — so they can make informed approve, reject, or escalate decisions. |
| **Entry Point / Surface** | Sleek Billings Frontend > Offboarding Requests > [Company row] > `/offboarding-requests/:id` |
| **Short Description** | A detail view for a single offboarding request, showing company information (name, status, registration identifiers per market), request metadata (type, churn reason, Zendesk link, Slack link, assignee), the list of subscriptions targeted for offboarding with service periods, and a chronological activity log. Context-sensitive action buttons allow the operator to approve, reject, submit for review, complete, or cancel the request depending on its current status. |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | Upstream: Review Offboarding Requests list (`/offboarding-requests`); Company overview in Admin App (deep-link via `VITE_ADMIN_APP_URL`); Service Delivery API — offboarding-requests resource; Sleek Back API — company details enrichment (`/companies/:id?load[]=fye`) |
| **Service / Repository** | sleek-billings-frontend; Service Delivery API (external backend); Sleek Back API |
| **DB - Collections** | Unknown (backend services; not visible from frontend) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which service owns the offboarding-requests resource in the backend — and what DB collections back it? Can the "System" actor (auto-flagged for offboarding) be further identified (scheduled job or rule engine)? Is the Slack request link populated automatically or manually entered? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/pages/Offboarding/OffboardingRequestDetails.jsx`

- Route param: `id` from `useParams()` — page renders at `/offboarding-requests/:id`.
- **Data fetching** (lines 379–411):
  - `sleekServiceDeliveryApi.getOffboardingRequestById(id)` — loads the offboarding request DTO.
  - `sleekBackApi.getCompanyDetails(companyRefId)` — enriches the request with full company data (`/companies/:id?load[]=fye`); falls back gracefully on error.
  - `sleekServiceDeliveryApi.getAllUsers({ limit: 2000 })` — loads all internal users for the Offboarding In Charge assignee picker and for resolving actor names in the activity log.
- **Market-aware company info section** (lines 88–96, 793–816):
  - `COMPANY_INFO_FIELDS_BY_PLATFORM` maps platform slug (`sg`, `hk`, `au`, `uk`) to which registration identifiers to show (UEN, CRN/BRN, ABN/ACN).
  - Field labels are normalised per market via `LABELS_MAPPING` (e.g. UK renders "Company Number" instead of "UEN").
- **Request Details section** (lines 818–880): displays status badge, offboarding-in-charge user, request type label, reason for churn, Zendesk link (clickable), Slack request link.
- **Subscriptions to offboard** (lines 882–): table listing each subscription with service period dates.
- **Activity log** (`ActivityLogEntry` component, lines 137–289): timeline of all state transitions with timestamp, actor name (or "System" with tooltip), status label, churn reason, rejection reason, comments, and offboarding-in-charge assignment.
- **Action buttons** are conditional on current status (lines 649–790):
  - `pending` → "Reject request" + "Review and approve"
  - `approved` → "Cancel request" + "Submit for review"
  - `to_be_reviewed` → "Cancel request" + "Complete offboarding"
- **Approve modal required fields** (line 300): `requestType`, `reason`, `offboardingInChargeUserId`, `zendeskLink`.
- **Reject modal required fields** (line 301): `reasonForRejection`.
- **Request type options** (lines 304–343): 8 values — partial/full churn, strike off, archive — each split by initiating party (Client vs Sleek).
- **Rejection reason options** (lines 345–356): 10 pre-defined reasons covering procedural non-compliance (e.g. chaser not sent, client recently active, incorrect workflow).

### `src/services/service-delivery-api.js` (lines 1103–1156)

- `GET /offboarding-requests/:id` — fetch single request (line 1103).
- `PUT /offboarding-requests/:id/approve` — payload: `requestType`, `reason`, `zendeskLink`, `comments`, `offboardingInChargeUserId` (line 1112).
- `PUT /offboarding-requests/:id/reject` — payload: `reasonForRejection`, `comments` (line 1121).
- `PUT /offboarding-requests/:id/submit-for-review` — payload: `comments` (line 1130).
- `PUT /offboarding-requests/:id/complete` — payload: `comments` (line 1139).
- `PUT /offboarding-requests/:id/cancel` — payload: `comments` (line 1148).
- Base URL: `VITE_SERVICE_DELIVERY_API_URL`. Auth header: Bearer JWT or raw token from `localStorage`.

### `src/services/sleek-back-api.js` (lines 73–81)

- `GET /companies/:id?load[]=fye` — used to enrich the request with live company status, name, identifiers, and FYE.

### `src/lib/constants.jsx` (lines 527–582)

- `OFFBOARDING_REQUEST_STATUS`: `pending`, `approved`, `to_be_reviewed`, `rejected`, `completed`, `cancelled`.
- `OFFBOARDING_REQUEST_TYPE`: 8 values covering partial churn, full churn, strike off, archive — each by Client or Sleek.
- `OFFBOARDING_REQUEST_STATUS_BADGE_VARIANT`: maps statuses to SDS badge colour variants.
