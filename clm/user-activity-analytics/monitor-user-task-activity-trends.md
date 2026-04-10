# Monitor User Task Activity Trends

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor user task activity trends |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations Admin |
| **Business Outcome** | Enables operations admins to track team engagement and productivity by reviewing week-over-week task activity volumes, broken down by activity type and optionally filtered to a specific user. |
| **Entry Point / Surface** | Sleek Billings App > Dev Tools > Analytics > User Activity (`analytics/user-activity`) — gated by `devMode === "true"` or `environment !== "production"` |
| **Short Description** | Displays a weekly breakdown of task activities (comments, links, files, assignments, status changes, due date changes, deletions) across all users or filtered to a specific user. Admins choose a time window (1–52 weeks, default 12) and can drill into a selected user's recent activity log with task context. Results are cached on the backend for 5 minutes. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | sleek-service-delivery-api (`GET /analytics/user-activity`, `GET /task-activities`, `GET /users`); Tasks Analytics (`/analytics/tasks`); Team Assignments Analytics (`/analytics/team-assignments`) |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL (TypeORM): `task_activity` (fields: `createdAt`, `performedByUserId`, `activityType`, `recordStatus`); `task`; `user` |
| **Evidence Source** | codebase |
| **Criticality** | Low |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Is this intended only for non-production/internal environments, or will it be promoted to production? No market-specific logic observed — is this a global feature? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Backend — `sleek-service-delivery-api`

**Controller** — `src/analytics/controllers/analytics.controller.ts:77`
- `GET /analytics/user-activity`
- Guard: `@SleekBackAuth('admin')` on the whole controller — admin role required
- Query params: `UserActivityQueryDto` → `weeks` (integer, 1–52, default 12), `performedByUserId` (optional UUID)
- Returns: `UserActivityStatsDto`

**Service** — `src/analytics/services/analytics.service.ts:500`
- Method: `getUserActivityStats(query)` → `getUserActivityStatsUncached(query)`
- Cache key: `user-activity:{weeks}:{userId|'all'}` with `ANALYTICS_CACHE_TTL_MS` (5-minute TTL)
- Three SQL queries against `task_activity` (TypeORM `Repository<TaskActivity>`):
  1. Total activity count grouped by ISO week (`date_trunc('week', createdAt)`)
  2. Distinct active user count per week (`COUNT(DISTINCT performedByUserId)`)
  3. Activity count per week per `activityType`
- Soft-delete filter: excludes records where `recordStatus = DELETED`
- Optional user filter: `activity.performedByUserId = :performedByUserId`
- Returns weeks ordered latest first (`weeklyCounts.reverse()`)

**DTOs**
- `src/analytics/dto/user-activity-query.dto.ts` — `weeks` (default 12, min 1, max 52), `performedByUserId` (UUID, optional)
- `src/analytics/dto/user-activity-stats.dto.ts` — `UserActivityStatsDto { weeklyCounts: WeeklyCountDto[] }` where each entry has `weekStart` (ISO date), `count`, `activeUserCount`, `byActivityType: Record<string, number>`

### Frontend — `sleek-billings-frontend`

**Component** — `src/pages/Analytics/UserActivityAnalytics.jsx`
- Filters: week window (6 / 12 / 24 weeks), user selector (all users or specific user)
- Table 1: weekly counts with `weekStart`, total count, `activeUserCount`, and per-`activityType` breakdown
- Table 2 (user-scoped): recent 100 activities sorted by `createdAt DESC`, showing date, type, and task name
- Activity types tracked: `COMMENT`, `LINK`, `FILE`, `COMMENT_AND_FILE`, `ASSIGNMENT`, `STATUS_CHANGE`, `DUE_DATE_CHANGE`, `COMMENT_DELETED`, `LINK_DELETED`, `FILE_DELETED`

**API calls** (via `src/services/service-delivery-api.js`)
| Method | Endpoint | Params |
|---|---|---|
| `GET` | `/analytics/user-activity` | `weeks`, `performedByUserId` (optional) |
| `GET` | `/task-activities` | `performedByUserId`, `limit=100`, `page=1`, `sortBy=createdAt`, `sortOrder=DESC` |
| `GET` | `/users` | `limit=500` |

**Navigation / routing**
- Route: `analytics/user-activity` in `src/App.jsx:160`
- Nav entry: `src/data/nav-rail-items.js:248` — nested under **Dev Tools > Analytics**; gated by `devMode === "true"` or `environment !== "production"`
