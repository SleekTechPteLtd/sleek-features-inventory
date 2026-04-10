# Export staff assignment gap report

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Export staff assignment gap report |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operations teams to download a filtered list of companies missing key delivery role assignments, supporting offline review and escalation workflows without requiring repeated access to the admin tool. |
| **Entry Point / Surface** | Sleek Admin App > Delivery > Analytics > Staff Assignment Overview > "Export report" button |
| **Short Description** | From the Staff Assignment Overview page, operations users click "Export report" to download a CSV of companies filtered by role gaps (Accountant I/C, Bookkeeper, Accounting Manager, Team Lead), company status, and name search. The export mirrors the active filter state and is named `staff-assignment-gaps-<date>.csv`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Staff Assignment Overview (gap detection view); `getStaffAssignmentSummary` and `getStaffAssignmentCompanies` for the page's live data; `COMPANY_STATUS_VALUES` constants for status filter options |
| **Service / Repository** | sleek-billings-frontend, service-delivery-api (backend) |
| **DB - Collections** | `companies`, `team_assignments`, `users` (PostgreSQL via TypeORM) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets or entity types are included in the export? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Export trigger
`pages/Delivery/Analytics/StaffAssignmentOverview.jsx` — `handleExport` (line 203–228):
- Collects active filter state: `hasGaps`, `roleTypes[]`, `search`, `companyStatuses[]`
- Calls `sleekServiceDeliveryApi.exportStaffAssignment(params)`
- Receives a blob response and downloads it as `staff-assignment-gaps-<YYYY-MM-DD>.csv`
- Export button is disabled and shows a spinner while the request is in-flight

### API methods — `services/service-delivery-api.js`
| Method | HTTP | Path | Notes |
|---|---|---|---|
| `exportStaffAssignment` | POST | `/analytics/staff-assignment/export` | Body carries filter params; `responseType: "blob"` |
| `getStaffAssignmentSummary` | GET | `/analytics/staff-assignment/summary` | Returns `companiesWithGaps` and `totalCompanies` counts |
| `getStaffAssignmentCompanies` | GET | `/analytics/staff-assignment/companies` | Paginated; supports `hasGaps`, `roleTypes[]`, `search`, `companyStatuses[]`, `page`, `limit` |

Base URL: `VITE_SERVICE_DELIVERY_API_URL` (service-delivery-api backend service).  
Auth header: Bearer JWT (SSO) or raw token; `App-Origin: admin` / `admin-sso`.

### Role slots tracked
| Slot key | API `roleType` string |
|---|---|
| `accountant` | `Accountant I/C` |
| `bookkeeper` | `Bookkeeper` |
| `accountManager` | `Accounting Manager` |
| `teamLead` | `Team Lead` |

### Backend endpoint — `analytics/controllers/staff-assignment-analytics.controller.ts`
- `POST /analytics/staff-assignment/export` — protected by `@SleekBackAuth('admin')` (internal admin auth)
- Returns `StreamableFile` with `Content-Type: text/csv; charset=utf-8`
- Accepts `StaffAssignmentExportDto` body: `roleTypes[]`, `hasGaps`, `search`, `companyStatuses[]`
- File disposition: `attachment; filename="staff-assignment-gaps.csv"`

### CSV columns (from `exportCsv` in `staff-assignment-analytics.service.ts`)
`Company ID, Company Name, Company Number, Company Status, Total Roles, Assigned Roles, Unassigned Roles, Coverage %, Role Details`
- Role Details format: `<roleType>:<AssigneeName|Assigned|Unassigned>` joined by `;`

### Backend data access — `analytics/services/staff-assignment-analytics.service.ts`
- Queries `companies`, `team_assignments` (with `assignedUser` join to `users`) via TypeORM repositories
- Export paginates internally using `ANALYTICS_CSV_EXPORT_PAGE_SIZE` to exhaust all matching rows
- Summary and list endpoints cache results in Redis via `CACHE_MANAGER` (`ANALYTICS_CACHE_TTL_MS`)
- Gap detection uses SQL `EXISTS`/`NOT EXISTS` subqueries scoped to `team_assignments` per company

### UI surface
- Page title: **Staff Assignment Overview** / "Gap detection"
- Summary card shows count of companies with at least one gap out of total companies
- Filters: company name search (debounced 350 ms), "Role missing" multi-select, company status multi-select, "Show only companies with missing roles" toggle
- Table columns: Company name, Company status, one Y/N badge column per role slot
- Pagination: 30 rows per page
