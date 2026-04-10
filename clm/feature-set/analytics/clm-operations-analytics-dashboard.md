# CLM Operations Analytics Dashboard

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | CLM Operations Analytics Dashboard |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Gives operators a real-time, single-pane view of CLM service delivery health so they can identify overdue tasks, stalled deliverables, and subscription lifecycle problems before they escalate. |
| **Entry Point / Surface** | Sleek Billings Admin > Analytics |
| **Short Description** | Displays aggregate counts and status breakdowns for tasks (total, overdue, due soon, unassigned, by-status), deliverables (total, by-status), and subscriptions (total, active, by service-delivery status). Data is fetched from the service-delivery backend on page load and refreshed on demand. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | sleek-service-delivery backend (`GET /analytics` and sub-routes); related deeper views: subscriptions analytics, tasks analytics, staff assignment analytics, SDS usage analytics, task distribution analytics |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery (backend via `VITE_SERVICE_DELIVERY_API_URL`) |
| **DB - Collections** | Unknown (backend collections not visible from frontend code) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/jurisdictions does this cover? Are there role-based access controls that restrict which operators see this view? The backend `/analytics` endpoint aggregates tasks + deliverables + subscriptions in one call — is that composition maintained server-side or assembled from separate queries? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend component
- `src/pages/Analytics/Analytics.jsx`
  - Calls `sleekServiceDeliveryApi.getAnalytics()` on mount
  - Destructures response into `{ tasks, deliverables, subscriptions }`
  - **Tasks panel**: total, overdue (red), dueSoon (orange), unassigned (yellow); status grid: `TO_DO`, `NOT_REQUIRED`, `DONE`, `ARCHIVED`
  - **Deliverables panel**: total; status list: `PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `ARCHIVED`
  - **Subscriptions panel**: total, active; service-delivery status grid: `none`, `active`, `inactive`, `delivered`, `discontinued`, `toBeStarted`, `toOffboard`, `deactivated`

### API service
- `src/services/service-delivery-api.js`
  - Base URL: `VITE_SERVICE_DELIVERY_API_URL` (env var — service-delivery backend)
  - Auth: Bearer JWT or raw token; `App-Origin: admin-sso` (internal operator access only)
  - `getAnalytics()` → `GET /analytics` — unified summary for the main dashboard page
  - Additional granular analytics endpoints (used by other pages):
    - `GET /analytics/subscriptions`
    - `GET /analytics/deliverables`
    - `GET /analytics/tasks`
    - `GET /analytics/team-assignments`
    - `GET /analytics/user-activity`
    - `GET /analytics/sds-usage/summary` + `/staff-engagement` + `/export`
    - `GET /analytics/staff-assignment/summary` + `/companies` + `/export`
    - `GET /analytics/task-distribution/summary` + `/staff` + `/filter-options` + `/export`
