# Seed and Reset Service Delivery Test Data

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Seed and Reset Service Delivery Test Data |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal developer / QA operator) |
| **Business Outcome** | Enables operators to populate the service delivery database with representative test data or wipe it clean, so the environment is always in a known state for testing and development. |
| **Entry Point / Surface** | Sleek Billings Admin > Developer Tools > Triggers tab |
| **Short Description** | Provides four one-click database actions: full seed (companies, users, subscriptions, deliverable templates, task templates, deliverables, tasks), full truncate (permanently deletes all data), one-time sync of companies from MongoDB → PostgreSQL, and one-time sync of users from MongoDB → PostgreSQL. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Depends on the Sleek Service Delivery backend API (`VITE_SERVICE_DELIVERY_API_URL`). Seed and truncate affect the same PostgreSQL tables used by all other service delivery features (subscriptions, deliverables, tasks, users, companies). Sync flows pull source data from MongoDB. |
| **Service / Repository** | sleek-billings-frontend (UI); Sleek Service Delivery API (backend — separate repo, unknown name) |
| **DB - Collections** | PostgreSQL tables: companies, users, subscriptions, deliverable_templates, task_templates, deliverables, tasks (names inferred from seed result fields). MongoDB collections: companies, users (source for sync operations). |
| **Evidence Source** | codebase |
| **Criticality** | Low |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. Is this page guarded by a role/permission check (no auth guard visible in the frontend route)? 2. What backend repo owns `/seed`, `/seed/truncate`, `/seed/sync/companies`, `/seed/sync/users`? 3. Is this page accessible in production environments or only staging/dev? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/Delivery/TestDelivery.jsx` — `TriggersList` component exposes four action buttons; `TestDelivery` wraps it in a "Developer Tools" page with a Users tab and a Triggers tab.
- `src/services/service-delivery-api.js` — `sleekServiceDeliveryApi` object; relevant methods:

| Method | HTTP call | Purpose |
|---|---|---|
| `seedDatabase()` | `POST /seed` | Clears existing data and creates representative seed records |
| `truncateDatabase()` | `POST /seed/truncate` | Permanently deletes all rows from all tables |
| `syncCompanies()` | `POST /seed/sync/companies` | One-time push of companies from MongoDB to PostgreSQL |
| `syncUsers()` | `POST /seed/sync/users` | One-time push of users from MongoDB to PostgreSQL |

### Seed result shape (from UI display, `TestDelivery.jsx:246–265`)
```
{
  companies, users, subscriptions,
  deliverableTemplates, taskTemplates,
  deliverables, tasks
}
```

### Auth surface
- API client sets `Authorization` header from `localStorage.getItem("auth")` and `App-Origin: admin` or `admin-sso`.
- No frontend route guard is visible in this file; access control enforced server-side (unknown).

### Confirmation guards (`TestDelivery.jsx:148, 168`)
- Seed: `window.confirm` dialog warns the user that all existing data will be cleared.
- Truncate: `window.confirm` dialog explicitly warns the action **cannot be undone**.
