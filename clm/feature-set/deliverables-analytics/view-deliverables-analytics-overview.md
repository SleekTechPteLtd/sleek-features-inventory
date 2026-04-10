# Monitor Deliverables Service Delivery Health

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor deliverables service delivery health |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operators to assess service delivery health at a glance — total deliverable count and breakdown across 5 lifecycle statuses — supporting workload visibility and delivery oversight. |
| **Entry Point / Surface** | Sleek Admin > Analytics > Deliverables Analytics (`/analytics/deliverables`) |
| **Short Description** | Displays a summary dashboard showing total deliverable count and a per-status breakdown across PENDING, IN_PROGRESS, COMPLETED, CANCELLED, and ARCHIVED. Data is fetched once on mount from `GET /analytics/deliverables` with no filters or date-range controls. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Analytics overview dashboard (`GET /analytics`, `Analytics.jsx`); sibling analytics: subscriptions (`GET /analytics/subscriptions`), tasks (`GET /analytics/tasks`), team assignments (`GET /analytics/team-assignments`); Service Delivery API backend |
| **Service / Repository** | sleek-billings-frontend (UI), sleek-service-delivery-api (backend — `GET /analytics/deliverables`) |
| **DB - Collections** | PostgreSQL — `deliverables` table (status counts); sibling analytics endpoints additionally query `tasks`, `subscriptions`, `team_assignments`, `users`, `deliverable_templates`, `task_activities` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Is date-range or market filtering planned? Which markets/regions use this dashboard? Cache backend (Redis assumed via CACHE_MANAGER) not confirmed from config. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### UI — `src/pages/Analytics/DeliverablesAnalytics.jsx`

- React component mounts and immediately calls `sleekServiceDeliveryApi.getDeliverableAnalytics()`.
- Renders two KPI cards:
  - **Total Deliverables** — `analytics.total`
  - **Deliverables by Status** — five rows from `analytics.byStatus`: `PENDING`, `IN_PROGRESS` (blue), `COMPLETED` (green), `CANCELLED` (red), `ARCHIVED` (grey)
- No filters, date pickers, or market toggles present; data is fetched once on mount.
- Route: `/analytics/deliverables` (lazy-loaded in `App.jsx` line 30, registered at line 157).

### API client — `src/services/service-delivery-api.js`

```js
// line 749
getDeliverableAnalytics: async () => {
  const response = await serviceDeliveryApi.get("/analytics/deliverables");
  ...
}
```

- Base client: `axios.create({ baseURL: SERVICE_DELIVERY_API_URL })` — environment variable pointing to the Service Delivery API.
- Auth headers: `Authorization` (Bearer JWT or raw token) + `App-Origin` (`admin` or `admin-sso`).
- Sibling analytics endpoints on the same base client: `/analytics`, `/analytics/subscriptions`, `/analytics/tasks`, `/analytics/team-assignments`, `/analytics/sds-usage/*`, `/analytics/staff-assignment/*`, `/analytics/task-distribution/*`.

### Deliverables status values (from UI)

| Status constant | Display label | UI colour |
|---|---|---|
| `PENDING` | Pending | grey |
| `IN_PROGRESS` | In Progress | blue |
| `COMPLETED` | Completed | green |
| `CANCELLED` | Cancelled | red |
| `ARCHIVED` | Archived | grey |

### Analytics overview context — `src/pages/Analytics/Analytics.jsx`

The parent `Analytics` dashboard (`GET /analytics`) also surfaces a deliverables sub-section with the same `total` + `byStatus` structure, confirming this is one consistent data shape returned by the Service Delivery API.

---

### Backend — `sleek-service-delivery-api`

#### Controller — `src/analytics/controllers/analytics.controller.ts`

- Class decorated `@SleekBackAuth('admin')` — admin-role JWT required for all analytics endpoints.
- `GET /analytics/deliverables` → `AnalyticsService.getDeliverableStats()` — returns `DeliverableStatsDto`.
- `GET /analytics` → `AnalyticsService.getAnalytics()` — aggregates deliverables, tasks, subscriptions, and team assignments in parallel; returns `AnalyticsResponseDto`.

#### Service — `src/analytics/services/analytics.service.ts`

- `getDeliverableStats()` checks a **5-minute cache** (key: `analytics:dashboard:deliverable-stats:<hash>`) via `CACHE_MANAGER` before querying DB.
- `getDeliverableStatsUncached()`: queries all rows from the `deliverables` table (`select: ['status']`), accumulates counts into a `byStatus` map (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `ARCHIVED`), and returns `{ total, byStatus }`.
- No date-range, subscription, or market filters applied — always a global aggregate.

#### DTO — `src/analytics/dto/analytics-response.dto.ts`

```ts
class DeliverableStatsDto {
  total: number;
  byStatus: { PENDING: number; IN_PROGRESS: number; COMPLETED: number; CANCELLED: number; ARCHIVED: number; };
}
```

#### Cache — `src/analytics/analytics-cache.helper.ts`

- `ANALYTICS_CACHE_TTL_MS = 5 * 60 * 1000` (5 minutes).
- Keys are SHA-256 hashed from normalized query params for cache stability.

#### DB tables touched (TypeORM / PostgreSQL)

| Table | Purpose |
|---|---|
| `deliverables` | Status counts for deliverable analytics |
| `tasks` | Task status, due-date, assignee counts (sibling endpoint) |
| `subscriptions` | Active count, service-delivery-status breakdown (sibling endpoint) |
| `team_assignments` | Role-type and user assignment counts (sibling endpoint) |
| `users` | Resolves user names/emails for team assignment stats |
| `deliverable_templates` | Used to find applicable subscription codes |
| `task_activities` | Week-on-week user activity analytics (sibling endpoint) |
