# Operations Analytics Dashboard

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Operations Analytics Dashboard |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Gives operations admins a real-time view of platform health across subscriptions, deliverables, tasks, team capacity, and week-on-week user activity so they can spot bottlenecks and act before issues escalate. |
| **Entry Point / Surface** | Internal admin dashboard (exact frontend surface Unknown — API only observed) |
| **Short Description** | Aggregates and exposes platform-wide metrics for subscriptions, deliverables, tasks, team assignments, and task-activity trends. Admins can retrieve all metrics in one call or drill into each category separately; user-activity data supports week-on-week filtering by user. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Subscriptions module, Deliverables module, Tasks module, Team Assignments module, Task Activities module, Deliverable Templates module; Redis cache layer (CACHE_MANAGER) |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | tasks, deliverables, subscriptions, team_assignments, users, deliverable_templates, task_activities (PostgreSQL via TypeORM) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which frontend app surfaces this dashboard? Is there a separate reporting UI or is it embedded in the internal admin panel? Are markets/jurisdictions filtered at the UI layer or is the data always global? What is ANALYTICS_CACHE_TTL_MS set to in production? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Auth surface
- `@SleekBackAuth('admin')` on `AnalyticsController` — all endpoints restricted to admin role.

### Endpoints (`GET /analytics/*`)
| Route | Method in service | What it returns |
|---|---|---|
| `GET /analytics` | `getAnalytics()` | All four stat categories combined |
| `GET /analytics/subscriptions` | `getSubscriptionStats()` | Total, active count, by service-delivery status, top codes |
| `GET /analytics/deliverables` | `getDeliverableStats()` | Total, by status (PENDING/IN_PROGRESS/COMPLETED/CANCELLED/ARCHIVED) |
| `GET /analytics/tasks` | `getTaskStats()` | Total, by status, overdue, due-soon (14d window), unassigned, top tasks per status, tasks by template name |
| `GET /analytics/team-assignments` | `getTeamAssignmentStats()` | Total, assigned/unassigned, by role type, per-user breakdown with task counts |
| `GET /analytics/user-activity` | `getUserActivityStats(query)` | Week-on-week task-activity counts, distinct active users per week, breakdown by activity type; accepts `weeks` (default 12) and optional `performedByUserId` |

### Caching
- All stat methods check Redis (via `CACHE_MANAGER`) before hitting the DB.
- Cache key helper: `buildAnalyticsCacheKey(...)` in `analytics-cache.helper.ts`.
- TTL constant: `ANALYTICS_CACHE_TTL_MS` (value not inspected).
- User-activity cache key pattern: `user-activity:<weeks>:<userId|'all'>`.

### DB tables read (read-only, no writes)
- `tasks` — status, dueDate, assignedUserId, completedDate, companyId, template join
- `deliverables` — status
- `subscriptions` — isActive, serviceDeliveryStatus, code, name
- `deliverable_templates` — codes
- `team_assignments` — assignedUserId, roleType, companyId
- `users` — id, firstName, lastName, email
- `task_activities` — createdAt, performedByUserId, activityType, recordStatus

### Key business logic
- **Overdue tasks**: `TaskStatus.TO_DO` with `dueDate < today`.
- **Due-soon tasks**: `TaskStatus.TO_DO` with `dueDate` within next 14 days.
- **Top subscriptions by config code**: cross-references subscription codes against deliverable template codes to surface only "applicable" subscriptions (top 20 by count).
- **Week-on-week activity**: ISO week (Monday start), excludes soft-deleted activities (`RecordStatus.DELETED`), returns latest week first.
