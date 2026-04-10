# Review Company Role Coverage

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Company Role Coverage |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enable operations admins to identify and prioritise assignment gaps by surfacing which client companies have unfilled delivery roles, so every company has complete staff coverage before service delivery begins. |
| **Entry Point / Surface** | Sleek Admin App > Delivery > Analytics > Staff Assignment (backend API: `GET /analytics/staff-assignment/companies`, `GET /analytics/staff-assignment/summary`) |
| **Short Description** | Provides a paginated, filterable list of client companies with per-role assignment coverage (filled/unfilled for each of 18 role types), plus aggregate summary metrics. Supports filtering by role type, company status, gap presence, and name search; results are cached to reduce DB load. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: staff assignment write flows that populate the `team_assignments` table. Downstream: operations teams act on gap data to assign staff. Related features: `monitor-staff-assignment-gaps` (frontend view consuming this API), `export-staff-assignment-gap-report` (CSV export). |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | `companies`, `team_assignments`, `users` (PostgreSQL via TypeORM) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which markets/jurisdictions is this view active for? 2. What is the configured value of `ANALYTICS_CACHE_TTL_MS`? 3. The `hasGaps === false` filter (lines 289–291 in service) is applied in-memory after pagination, while `hasGaps === true` is applied in SQL — is that asymmetry intentional? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller
`src/analytics/controllers/staff-assignment-analytics.controller.ts`

- `@ApiTags('analytics/staff-assignment')` — NestJS controller under route prefix `analytics/staff-assignment`
- Auth guard: `@SleekBackAuth('admin')` — restricted to admin users only

| Method | Route | Handler | Purpose |
|---|---|---|---|
| `GET` | `/analytics/staff-assignment/summary` | `getSummary` | Aggregate metrics: total companies, companies with gaps, companies fully covered, assignments by role type |
| `GET` | `/analytics/staff-assignment/companies` | `getCompanies` | Paginated list of companies with per-role coverage detail |
| `POST` | `/analytics/staff-assignment/export` | `exportCsv` | Streams full result set as CSV (uses same `getCompanies` logic internally) |

### Service
`src/analytics/services/staff-assignment-analytics.service.ts`

**`getSummary(query)`**
- Accepts optional `roleTypes[]` and `companyStatuses[]` filters
- Queries `companies` table for total count (respecting status filter)
- Queries `team_assignments` joined to `companies` to count filled/unfilled slots
- Calls `countCompaniesWithGaps` (SQL subquery via `applyHasGapsCompanyFilter`) for accurate gap count
- Calls `getRoleTypeSummary` for breakdown by each `RoleType` enum value
- Result cached via `CACHE_MANAGER` with key `staff-assignment:summary:<query-hash>`

**`getCompanies(query)`**
- Accepts `page`, `limit`, `search`, `roleTypes[]`, `companyStatuses[]`, `hasGaps?`
- `hasGaps === true`: applies SQL subquery filter (`applyHasGapsCompanyFilter`) **before** pagination — a gap is defined as: no `team_assignments` row for the company, OR a row exists with `assignedUserId IS NULL`
- `hasGaps === false`: filtered in-memory after query (only keeps companies where `unassignedRoles === 0`)
- Loads all `team_assignments` for the paginated company IDs (without role type filter to preserve full per-role Y/N in response)
- Joins `users` to surface `firstName + lastName` of assigned staff
- Result cached via `CACHE_MANAGER` with key `staff-assignment:companies:<query-hash>`

**`exportCsv(query)`**
- Iterates pages of `getCompanies` with constant `ANALYTICS_CSV_EXPORT_PAGE_SIZE`
- Builds CSV with columns: Company ID, Name, Number, Status, Total Roles, Assigned, Unassigned, Coverage %, Role Details
- Streams response as `StreamableFile` with `Content-Disposition: attachment; filename="staff-assignment-gaps.csv"`

### Role types (18 values from `RoleType` enum)
`src/common/enums/role-type.enum.ts`

Team Lead, Accounting Manager, Bookkeeper, Corp Sec I/C, Tax Reviewer, Support I/C, Audit Onboarding I/C, Audit Manager, Audit I/C, Audit Reviewer, CSS I/C, Accountant I/C, Accountant Reviewer, Tax I/C, Tax Manager, Accounting Onboarding I/C, GST I/C, Remediation Accountant

### DB tables touched
- `companies` — filtered by `recordStatus != DELETED`, optional `status IN (...)`, optional `name/companyNumber ILIKE` search
- `team_assignments` — joined to companies; unique index on `(companyId, roleType)`; `assignedUserId` nullable (NULL = gap)
- `users` — left-joined for assignee name (`firstName`, `lastName`)
