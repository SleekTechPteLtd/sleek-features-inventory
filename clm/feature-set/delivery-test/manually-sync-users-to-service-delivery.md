# Manually Sync Users to Service Delivery

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manually Sync Users to Service Delivery |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User / Developer |
| **Business Outcome** | Allows operators to immediately propagate user records from MongoDB into the service delivery PostgreSQL database without waiting for the next scheduled sync cycle. |
| **Entry Point / Surface** | Sleek Admin App > Developer Tools > Triggers tab > One-Time Sync > Sync Users |
| **Short Description** | Provides a manual trigger for operators to push user data from MongoDB to the service delivery PostgreSQL database on demand. The operator clicks "Sync Users" in the Developer Tools panel; the frontend calls `POST /seed/sync/users` on the service delivery API and displays the result inline. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | MongoDB (user source); service delivery PostgreSQL (sync target); scheduled user sync job (this feature bypasses it); Sync Companies (`POST /seed/sync/companies`) is a companion action on the same screen |
| **Service / Repository** | sleek-billings-frontend, service-delivery-api (backend, URL from `VITE_SERVICE_DELIVERY_API_URL`) |
| **DB - Collections** | Unknown — frontend hits the backend endpoint; which MongoDB collections are read is determined by the service delivery API |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which MongoDB collections/documents are read during the sync? What is the scheduled sync cadence this feature bypasses? Is this screen accessible in production or only staging/dev environments (page is labeled "Developer Tools" and lives under `TestDelivery`)? Are there guardrails preventing concurrent syncs? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

| File | Key evidence |
|---|---|
| `src/pages/Delivery/TestDelivery.jsx:202–215` | `handleSyncUsers` calls `sleekServiceDeliveryApi.syncUsers()`, shows loading state, surfaces success/error snackbar |
| `src/pages/Delivery/TestDelivery.jsx:217–293` | `TriggersList` component — "One-Time Sync" section with descriptive label: *"Manually trigger synchronization of companies and users from MongoDB to PostgreSQL without waiting for the scheduled sync."* |
| `src/pages/Delivery/TestDelivery.jsx:424–461` | `TestDelivery` (parent page) titled "Developer Tools"; Triggers tab hosts this action alongside seed/truncate database actions |
| `src/services/service-delivery-api.js:490–498` | `syncUsers: async () => serviceDeliveryApi.post("/seed/sync/users")` — unauthenticated-context POST to service delivery backend |
| `src/services/service-delivery-api.js:1–17` | API client uses `VITE_SERVICE_DELIVERY_API_URL`; auth via `Authorization` header (Bearer JWT or raw token); `App-Origin: admin` or `admin-sso` |
