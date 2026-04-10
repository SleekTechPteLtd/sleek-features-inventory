# Monitor Staff Assignment Gaps

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor Staff Assignment Gaps |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Ensure every active client company has all four key delivery roles covered so that service ownership gaps are caught and assigned before they affect delivery quality. |
| **Entry Point / Surface** | Sleek Admin App > Delivery > Analytics > Staff Assignment Overview |
| **Short Description** | Displays a paginated table of client companies with Y/N coverage indicators for four key roles (Accountant I/C, Bookkeeper, Accounting Manager, Team Lead). A summary card shows how many companies have at least one gap; filters narrow the view by role missing, company status, or name search; the full result set can be exported as CSV. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Relies on `service-delivery-api` (`VITE_SERVICE_DELIVERY_API_URL`) analytics endpoints. Upstream: staff assignment write/update flows that populate the role assignments consumed here. Downstream: Operations teams act on gap findings to assign staff. |
| **Service / Repository** | sleek-billings-frontend (UI), sleek-service-delivery-api (backend) |
| **DB - Collections** | PostgreSQL — `companies`, `team_assignments`, `users` (TypeORM via sleek-service-delivery-api) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which markets/jurisdictions is this analytics view enabled for? 2. What is the value of `ANALYTICS_CACHE_TTL_MS` (cache TTL for summary/companies responses)? 3. Which specific `RoleType` enum values exist beyond Bookkeeper, Team Lead, Accountant I/C, Accounting Manager? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### UI component
`src/pages/Delivery/Analytics/StaffAssignmentOverview.jsx`

- Page title: **Staff Assignment Overview** / sub-label "Gap detection"
- Four tracked roles mapped via `ROLE_SLOT_TO_API_TYPE`:
  - `accountant` → `"Accountant I/C"`
  - `bookkeeper` → `"Bookkeeper"`
  - `accountManager` → `"Accounting Manager"`
  - `teamLead` → `"Team Lead"`
- Summary card: `summaryData.companiesWithGaps` / `summaryData.totalCompanies` (from `getStaffAssignmentSummary`)
- Table: paginated (30 rows/page), columns: Company name, Company status, one Y/N badge per role
- Filters:
  - Company name search (350 ms debounce)
  - "Role missing" multi-select (any combination of the four roles)
  - "Company status" multi-select (values from `COMPANY_STATUS_VALUES` — DRAFT, PAID_AND_AWAITING_COMPANY_DETAIL, PARTNER_DRAFT, PARTNER_PAID, PAID_AND_INCOMPLETE, …)
  - Toggle: "Show only companies with missing roles" (`hasGaps=true` query param when on; default on)
- Export: `handleExport` → triggers CSV download named `staff-assignment-gaps-<date>.csv`

### API calls (`src/services/service-delivery-api.js`)
Axios instance `serviceDeliveryApi` — base URL: `VITE_SERVICE_DELIVERY_API_URL`

| Method | Endpoint | Query params |
|---|---|---|
| GET | `/analytics/staff-assignment/summary` | `roleTypes[]`, `companyStatuses[]` |
| GET | `/analytics/staff-assignment/companies` | `page`, `limit`, `hasGaps`, `roleTypes[]`, `search`, `companyStatuses[]` |
| POST | `/analytics/staff-assignment/export` | body: `hasGaps`, `roleTypes[]`, `search`, `companyStatuses[]`; responseType: `blob` |

### Response shape (inferred)
- `getStaffAssignmentSummary` → `{ companiesWithGaps: number, totalCompanies: number }`
- `getStaffAssignmentCompanies` → `{ data: CompanyRoleDto[], meta: { total: number } }`
  - Each `CompanyRoleDto`: `{ companyId, companyName, companyStatus, roles: [{ roleType, isAssigned }] }`
- `exportStaffAssignment` → CSV blob

---

### Backend — sleek-service-delivery-api

**Controller**: `src/analytics/controllers/staff-assignment-analytics.controller.ts`

- Class: `StaffAssignmentAnalyticsController`
- Guard: `@SleekBackAuth('admin')` — internal admin access only; no client-facing exposure
- Routes:

| Method | Path | Handler | Description |
|---|---|---|---|
| GET | `/analytics/staff-assignment/summary` | `getSummary` | Aggregate coverage metrics across all companies |
| GET | `/analytics/staff-assignment/companies` | `getCompanies` | Paginated per-company role coverage with gap flags |
| POST | `/analytics/staff-assignment/export` | `exportCsv` | Streams CSV; filename `staff-assignment-gaps.csv` |

**Service**: `src/analytics/services/staff-assignment-analytics.service.ts`

- Class: `StaffAssignmentAnalyticsService`
- Caching: both `getSummary` and `getCompanies` responses cached via `CACHE_MANAGER` with key prefix `staff-assignment:summary` / `staff-assignment:companies`; TTL = `ANALYTICS_CACHE_TTL_MS`
- Summary metrics returned (`StaffAssignmentSummaryDto`):
  - `totalCompanies`, `companiesFullyCovered`, `companiesWithGaps`
  - `totalAssignments`, `filledAssignments`, `unfilledAssignments`, `overallCoveragePercent`
  - `byRoleType: RoleGapSummaryDto[]` — per role: `totalAssignments`, `assignedCount`, `unassignedCount`, `coveragePercent`
- Gap definition (SQL): a company has a gap if it has **no** `team_assignments` row for a role, **or** has a row with `assignedUserId IS NULL`
- CSV export columns: `Company ID, Company Name, Company Number, Company Status, Total Roles, Assigned Roles, Unassigned Roles, Coverage %, Role Details`

**Database (TypeORM / PostgreSQL)**:

| Entity | Table | Usage |
|---|---|---|
| `Company` | `companies` | Main subject; filtered by `recordStatus` and `status` (companyStatuses) |
| `TeamAssignment` | `team_assignments` | Gap source; joins to company; `roleType` and `assignedUserId` columns key |
| `User` | `users` | Left-joined to expose `firstName`/`lastName` of assigned staff |

**DTOs**: `src/analytics/dto/staff-assignment-query.dto.ts`, `src/analytics/dto/staff-assignment-response.dto.ts`

- Query filters: `roleTypes[]` (comma-separated), `companyStatuses[]` (validated against `CompanyStatus` enum), `hasGaps` (boolean), `search` (name/number ILIKE), `page`/`limit`
- `RoleType` enum sourced from `src/common/enums/role-type.enum.ts`
