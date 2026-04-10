# Team Assignment Coverage Analytics

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Team Assignment Coverage Analytics |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal admin) |
| **Business Outcome** | Gives operations staff a real-time view of staffing gaps across all client companies — how many role slots are filled vs. vacant, broken down by role type and per company — so they can identify under-resourced accounts and act before service delivery is impacted. |
| **Entry Point / Surface** | Sleek Billings Frontend > Analytics > Team Assignments (`/analytics/team-assignments`) |
| **Short Description** | Surfaces aggregate coverage metrics (total/filled/unfilled slots, overall coverage %, companies fully covered vs. with gaps, per-role-type breakdown) and a paginated per-company role coverage table with gap filtering. Supports CSV export of the gap dataset. Results are server-side cached to reduce query load. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Team Assignments management (CRUD); Auto-Assignments; Delivery Staff Assignment overview; `companies` and `users` modules in sleek-service-delivery-api |
| **Service / Repository** | sleek-service-delivery-api, sleek-clm-monorepo / sleek-billings-frontend |
| **DB - Collections** | `company`, `team_assignments`, `users` (PostgreSQL via TypeORM) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. The frontend component (`TeamAssignmentsAnalytics.jsx`) calls `GET /analytics/team-assignments` and reads `analytics.total/assigned/unassigned/byUser`, which does not match the backend controller's routes (`/analytics/staff-assignment/summary` and `/analytics/staff-assignment/companies`). There may be a separate, older analytics endpoint not surfaced in the scanned files. 2. The `byUser` table in the UI (totalTasksAssigned, totalAssignedCompanies) has no matching backend method in this controller — source unknown. 3. Markets/jurisdictions: no geo-gating logic found. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Backend controller
`src/analytics/controllers/staff-assignment-analytics.controller.ts`

- Guard: `@SleekBackAuth('admin')` — all endpoints are restricted to internal admin users.
- Tag: `analytics/staff-assignment`
- Endpoints:
  - `GET /analytics/staff-assignment/summary` — returns `StaffAssignmentSummaryDto`:
    `totalCompanies`, `companiesFullyCovered`, `companiesWithGaps`, `totalAssignments`,
    `filledAssignments`, `unfilledAssignments`, `overallCoveragePercent`, `byRoleType[]`
  - `GET /analytics/staff-assignment/companies` — paginated list of companies with per-role coverage;
    supports filters: `roleTypes`, `hasGaps`, `search`, `companyStatuses`; returns `CompanyRoleCoverageDto[]`
  - `POST /analytics/staff-assignment/export` — streams a CSV file (`staff-assignment-gaps.csv`)
    with columns: Company ID, Name, Number, Status, Total/Assigned/Unassigned Roles, Coverage %, Role Details

### Backend service
`src/analytics/services/staff-assignment-analytics.service.ts`

- Repositories injected: `Company`, `TeamAssignment`, `User` (TypeORM/PostgreSQL).
- Caching: all read results cached via `CACHE_MANAGER` with key prefix `staff-assignment:summary` / `staff-assignment:companies` and TTL from `ANALYTICS_CACHE_TTL_MS`.
- Gap detection logic (`applyHasGapsCompanyFilter`): a company has a gap if it has no `team_assignments` row at all, or if any relevant `team_assignments` row has `assignedUserId IS NULL`. Filtering is applied in SQL before pagination to ensure accurate total counts.
- Role-type breakdown (`getRoleTypeSummary`): uses SQL `GROUP BY ta.roleType` with `SUM(CASE WHEN assignedUserId IS NOT NULL …)` to produce per-role filled/unfilled/coverage% rows.
- CSV export (`exportCsv`): pages through `getCompanies()` using `ANALYTICS_CSV_EXPORT_PAGE_SIZE` and streams the result.

### DTOs
`src/analytics/dto/staff-assignment-query.dto.ts`

- `StaffAssignmentSummaryQueryDto`: optional `roleTypes[]` (CSV), optional `companyStatuses[]`
- `StaffAssignmentCompaniesQueryDto`: extends `PaginationQueryDto`; adds `roleTypes[]`, `hasGaps`, `search`, `companyStatuses[]`
- `StaffAssignmentExportDto`: same filters as companies query (no pagination)

### Frontend component
`apps/sleek-billings-frontend/src/pages/Analytics/TeamAssignmentsAnalytics.jsx`

- Calls `sleekServiceDeliveryApi.getTeamAssignmentAnalytics()` on mount (maps to `GET /analytics/team-assignments` — different route than the backend controller above).
- Renders: three KPI cards (Total, Assigned, Unassigned), a role-type breakdown grid, and a per-user table (name, email, totalAssignments, totalAssignedCompanies, totalTasksAssigned, roleTypes badges).

### DB tables touched
- `company` — filtered by `recordStatus`, `status` (company lifecycle state)
- `team_assignments` — `companyId`, `roleType`, `assignedUserId`, `record_status`
- `users` — `firstName`, `lastName` joined for display in companies response
