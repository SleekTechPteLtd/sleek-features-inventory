# Monitor CLM Task Health

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor CLM Task Health |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Gives operations staff an at-a-glance view of the task pipeline — surfacing overdue, due-soon, and unassigned counts alongside a full status breakdown — so bottlenecks are caught early and follow-up is prioritised across all CLM workflows. |
| **Entry Point / Surface** | Sleek Billings Frontend > Analytics > Tasks Analytics |
| **Short Description** | Displays a summary dashboard of CLM task pipeline health: total tasks, overdue count, due-soon count, unassigned count, status breakdown (To Do / Not Required / Done / Archived), and a per-template breakdown showing count and status distribution for each task template. |
| **Variants / Markets** | Unknown (no market/locale filtering applied in query) |
| **Dependencies / Related Flows** | sleek-service-delivery API (`GET /analytics/tasks`); task templates (`task_templates` table, joined to group counts); CLM task management flows (tasks are created and assigned upstream); result is cache-manager cached to reduce DB load |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery (backend API) |
| **DB - Collections** | PostgreSQL (TypeORM): `tasks`, `task_templates` (joined via `task.template`), `deliverable_templates`, `deliverables`, `subscriptions`, `team_assignments`, `users`, `task_activities` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. Are markets scoped (SG/HK/UK/AU) or global? No market filter found in backend code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend component
- `src/pages/Analytics/TasksAnalytics.jsx`
  - On mount, calls `sleekServiceDeliveryApi.getTaskAnalytics()` and stores result in `analytics` state.
  - Renders four KPI cards: `analytics.total`, `analytics.overdue`, `analytics.dueSoon`, `analytics.unassigned`.
  - Renders a status breakdown grid: `analytics.byStatus.TO_DO`, `.NOT_REQUIRED`, `.DONE`, `.ARCHIVED`.
  - Conditionally renders a `tasksByTemplateName` table (ranked list of template names with total count and per-status breakdown: TO_DO, NOT_REQUIRED, DONE, ARCHIVED).

### API service
- `src/services/service-delivery-api.js` — `getTaskAnalytics()` (line 758)
  - `GET /analytics/tasks` via `serviceDeliveryApi` axios instance (base URL: `SERVICE_DELIVERY_API_URL`).
  - No query params; returns the full aggregated analytics object.

### Related endpoints in the same service client (context)
- `GET /tasks` — task list
- `GET /task-templates` — task template definitions
- `GET /analytics/deliverables` — sibling analytics endpoint (deliverables)
- `GET /analytics/team-assignment` — sibling analytics endpoint (team assignment)

### Backend implementation (sleek-service-delivery-api)
- `src/analytics/controllers/analytics.controller.ts` — `GET /analytics/tasks`
  - Guard: `@SleekBackAuth('admin')` — requires admin profile in the sleek-back auth system (403 for non-admin).
  - Delegates to `AnalyticsService.getTaskStats()`.
- `src/analytics/services/analytics.service.ts` — `getTaskStats()` / `getTaskStatsUncached()`
  - Loads all tasks (`status`, `dueDate`, `assignedUserId`) from the `tasks` table.
  - **Overdue**: `TO_DO` tasks whose `dueDate` is before today (start of day).
  - **Due soon**: `TO_DO` tasks due within the next **14 days** (hardcoded; not configurable).
  - **Unassigned**: tasks with no `assignedUserId`.
  - `byStatus` counts: `TO_DO`, `NOT_REQUIRED`, `DONE`, `ARCHIVED`.
  - `tasksByTemplateName`: query builder join on `task.template` → groups by `template.name` and `task.status`; sorted by total count descending.
  - `topTasksByStatus`: top 10 tasks per status (TO_DO ordered by `dueDate ASC NULLS LAST`; DONE by `completedDate DESC`; others by `updatedAt DESC`).
  - Results cached via `CACHE_MANAGER` with key `dashboard:task-stats` (TTL from `ANALYTICS_CACHE_TTL_MS`).
