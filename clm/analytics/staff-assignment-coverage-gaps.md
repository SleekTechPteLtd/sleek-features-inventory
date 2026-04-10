# Monitor Staff Assignment Coverage Gaps

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor Staff Assignment Coverage Gaps |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Enables operations admins to identify client companies with unfilled staff role assignments, ensuring every client has proper coverage across all defined service roles before delivery commences. |
| **Entry Point / Surface** | Internal Admin API — `GET /analytics/staff-assignment/summary`, `GET /analytics/staff-assignment/companies`, `POST /analytics/staff-assignment/export` |
| **Short Description** | Provides aggregate coverage metrics and a paginated, filterable company list showing which clients have unfilled role slots (e.g. Bookkeeper, Team Lead, Tax Reviewer). Admins can drill into gap details by role type and company status, and export results as a CSV file. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Team Assignments management (team_assignments table); Company lifecycle (companies table); User directory (users table); Analytics cache (CACHE_MANAGER); Delivery Staff Assignment feature (delivery-staff-assignment) |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL: `team_assignments`, `companies`, `users` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which front-end surface (internal ops dashboard?) consumes this API — not determinable from service code alone. No market-specific branching observed; unclear if coverage rules differ by region. Cache TTL strategy and invalidation trigger not visible in these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller
`src/analytics/controllers/staff-assignment-analytics.controller.ts`

- Auth guard: `@SleekBackAuth('admin')` — admin-only access
- `GET /analytics/staff-assignment/summary` → `getSummary(StaffAssignmentSummaryQueryDto)` — returns aggregate metrics: total companies, companies fully covered, companies with gaps, total/filled/unfilled assignment counts, overall coverage %, and per-role-type breakdown
- `GET /analytics/staff-assignment/companies` → `getCompanies(StaffAssignmentCompaniesQueryDto)` — paginated list of companies with per-company role coverage detail; supports `hasGaps`, `search`, `roleTypes`, `companyStatuses` filters
- `POST /analytics/staff-assignment/export` → `exportCsv(StaffAssignmentExportDto)` — streams a CSV file (`staff-assignment-gaps.csv`) with full role detail per company

### Service
`src/analytics/services/staff-assignment-analytics.service.ts`

- Results cached via `CACHE_MANAGER` with key `staff-assignment:summary|…` / `staff-assignment:companies|…` and `ANALYTICS_CACHE_TTL_MS` TTL
- Gap detection logic (`applyHasGapsCompanyFilter`): a company has a gap if it has **no** `team_assignment` row for a given role, **or** has a row with `assignedUserId IS NULL`
- Role types enumerated from `RoleType` enum: Team Lead, Accounting Manager, Bookkeeper, Corp Sec I/C, Tax Reviewer, Support I/C, Audit Onboarding I/C, Audit Manager, Audit I/C, Audit Reviewer, CSS I/C, Accountant I/C, Accountant Reviewer, Tax I/C, Tax Manager, Accounting Onboarding I/C, GST I/C, Remediation Accountant
- CSV export pages through `getCompanies` internally using `ANALYTICS_CSV_EXPORT_PAGE_SIZE` constant

### Entities / Tables
- `team_assignments` (TypeORM entity `TeamAssignment`) — columns: `companyId`, `assignedUserId`, `roleType`; unique index on `(companyId, roleType)`
- `companies` — joined for name, companyNumber, status, recordStatus filters
- `users` — joined for `firstName`, `lastName` of assigned staff
