# Monitor SDS Platform Usage and Staff Engagement

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor SDS Platform Usage and Staff Engagement |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Gives admins visibility into SDS platform adoption — tracking active staff counts, task completion rates, and per-staff engagement trends — so they can assess platform uptake and identify participation gaps across the service delivery team. |
| **Entry Point / Surface** | Sleek App > Delivery > Analytics > SDS Usage Dashboard (`/delivery/analytics/sds-usage-dashboard`); backend via internal admin API at `GET /analytics/sds-usage/summary`, `GET /analytics/sds-usage/staff-engagement`, `POST /analytics/sds-usage/export` |
| **Short Description** | Aggregates platform usage metrics (active staff counts, task stats, engagement totals, weekly trends) and per-staff engagement breakdowns (engagements by activity type, tasks assigned/completed, companies served, last activity date). Supports date-range filtering, pagination, and CSV export of both summary and per-staff views. Results are Redis-cached to reduce repeated query load. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Redis cache (CACHE_MANAGER, ANALYTICS_CACHE_TTL_MS); sleek-billings-frontend (dashboard consumer); sits alongside Staff Task Distribution and Staff Assignment Overview dashboards in the same Analytics nav group |
| **Service / Repository** | sleek-service-delivery-api, sleek-billings-frontend |
| **DB - Collections** | PostgreSQL tables (TypeORM): `task`, `task_activity`, `user`, `team_assignment` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Are markets SG/HK/AU/UK all enabled or is this SG-only? Is the `exportType: "summary"` variant surfaced in the UI or backend-only? Is ANALYTICS_CACHE_TTL_MS configurable per environment? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Auth surface
- `analytics/controllers/sds-usage-analytics.controller.ts:27` — `@SleekBackAuth('admin')` applied at controller level; all three endpoints require admin role.

### Endpoints
| Method | Path | Purpose |
|---|---|---|
| `GET` | `/analytics/sds-usage/summary` | Platform-wide totals: active staff, tasks (total/completed/overdue/due soon), total engagements, avg engagements per staff, weekly engagement trend % |
| `GET` | `/analytics/sds-usage/staff-engagement` | Paginated per-staff breakdown: engagements by activity type, tasks assigned/completed, companies assigned, last activity date, per-week engagement data |
| `POST` | `/analytics/sds-usage/export` | CSV download — `exportType: "summary"` or `"staff-engagement"`, optional `userId` and date range; pages through full dataset before streaming file |

### Service logic (sds-usage-analytics.service.ts)
- `getSummary` / `getStaffEngagement`: results cached under key `sds-usage:summary` / `sds-usage:staff-engagement` using `buildAnalyticsCacheKey`; cache TTL = `ANALYTICS_CACHE_TTL_MS`.
- Active staff count: users with at least one `team_assignment` row, excluding soft-deleted users (`RecordStatus.DELETED`).
- Task stats: computed in-memory from `task.status` (DONE = completed) and `task.dueDate` relative to today (overdue if past today, due soon if within 14 days).
- Weekly engagement: `date_trunc('week', activity.createdAt)` grouped by ISO week; rolls back `N` weeks (default 4).
- Engagement trend: week-over-week % change comparing last two weekly buckets.
- Per-staff engagement: joins `task_activity` counts subquery onto `user` ordered by total engagement count DESC; secondary sorts by first/last name.
- CSV export uses `ANALYTICS_CSV_EXPORT_PAGE_SIZE` constant for batch pagination.

### DB tables accessed
- `user` — staff identity, recordStatus filter
- `team_assignment` — maps staff to companies; used for active staff count and companies-assigned metric
- `task` — task status (DONE/TO_DO) and dueDate; filtered by assignedUserId per staff
- `task_activity` — engagement events; grouped by `performedByUserId` and `activityType`; provides per-week activity counts and last-activity date

### Related frontend file
- `clm/delivery-sds-usage/monitor-sds-staff-engagement-and-adoption.md` — frontend-perspective write-up (sleek-billings-frontend); covers UI components, nav entry point, and API call shapes.
