# Monitor Subscription Portfolio Health

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor subscription portfolio health |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Enables admins to assess subscription portfolio health at a glance — total and active counts, service delivery status distribution, and top config codes — supporting workload planning and service delivery oversight. |
| **Entry Point / Surface** | Sleek Admin > Analytics > Subscriptions Analytics (`GET /analytics/subscriptions`) |
| **Short Description** | Returns total and active subscription counts with a breakdown across 8 service delivery statuses (none, active, inactive, delivered, discontinued, toBeStarted, toOffboard, deactivated), plus a ranked list of up to 20 subscription codes that match at least one deliverable template config. Results are cached. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Deliverable templates (config code matching), subscription management, service delivery system; sibling analytics: deliverable analytics, task analytics, team assignment analytics, SDS usage analytics, staff assignment analytics |
| **Service / Repository** | sleek-billings-frontend (UI), sleek-service-delivery-api (backend) |
| **DB - Collections** | PostgreSQL (TypeORM): `subscription` (isActive, serviceDeliveryStatus, code, name), `deliverable_template` (codes[]) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Is date-range or market filtering planned? Which markets/regions use this dashboard? Cache TTL value (`ANALYTICS_CACHE_TTL_MS`) not inspected — unknown duration. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Backend — `sleek-service-delivery-api`

**Controller** — `src/analytics/controllers/analytics.controller.ts`

- `GET /analytics/subscriptions` → `AnalyticsController.getSubscriptionAnalytics()`
- Guard: `@SleekBackAuth('admin')` — admin-only access
- Returns `SubscriptionStatsDto`
- `@ApiOperation({ summary: 'Get subscription analytics' })`

**Service** — `src/analytics/services/analytics.service.ts`

- `getSubscriptionStats()` — checks Redis cache with key `dashboard:subscription-stats` via `buildAnalyticsCacheKey`; falls back to `getSubscriptionStatsUncached()`, then writes result back.
- `getSubscriptionStatsUncached()`:
  - Fetches all rows from `subscription` table selecting `isActive` and `serviceDeliveryStatus`.
  - Counts `active` (where `isActive = true`).
  - Counts by all 8 `ServiceDeliveryStatus` buckets: `none`, `active`, `inactive`, `delivered`, `discontinued`, `toBeStarted`, `toOffboard`, `deactivated`.
  - Calls `getTopSubscriptionsByConfigCode()`:
    - Loads all `deliverable_template.codes[]` to build an `applicableCodes` set.
    - Queries `subscription` WHERE `code IN (applicableCodes)`, groups by code, orders by count DESC, limits to top 20.
    - Returns `[{ code, count, configName }]` — `configName` is the subscription name for that code.

**DTO** — `src/analytics/dto/analytics-response.dto.ts`

```ts
class SubscriptionStatsDto {
  total: number;
  active: number;
  byServiceDeliveryStatus: {
    none; active; inactive; delivered; discontinued; toBeStarted; toOffboard; deactivated;
  };
  topSubscriptionsByConfigCode?: { code: string; count: number; configName: string }[];
}
```

---

### UI — `sleek-billings-frontend`

**Component** — `src/pages/Analytics/SubscriptionsAnalytics.jsx`

- Calls `sleekServiceDeliveryApi.getSubscriptionAnalytics()` on mount.
- Renders two KPI cards: **Total Subscriptions** (`analytics.total`) and **Active Subscriptions** (`analytics.active`).
- Renders a status-breakdown grid for all 8 `byServiceDeliveryStatus` buckets.
- Conditionally renders a ranked table of `topSubscriptionsByConfigCode` — columns: rank, config code, code name (`configName`), subscription count.
  - Section label: *"Subscription codes that match at least one deliverable template, ordered by number of subscriptions."*
- No filters, date pickers, or market toggles; data fetched once on mount.

**API client** — `src/services/service-delivery-api.js`

```js
getSubscriptionAnalytics: async () => {
  const response = await serviceDeliveryApi.get("/analytics/subscriptions");
  ...
}
```

- Base client: `axios.create({ baseURL: SERVICE_DELIVERY_API_URL })` → `sleek-service-delivery-api`.
