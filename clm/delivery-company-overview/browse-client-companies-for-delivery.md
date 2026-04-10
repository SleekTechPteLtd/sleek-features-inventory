# Browse client companies for delivery

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Browse client companies for delivery |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Delivery Team (internal admin users) |
| **Business Outcome** | Enables delivery teams to monitor and prioritise their full portfolio of client companies by surfacing lifecycle status, team staffing assignments, and gaps in role coverage across 18 service roles. |
| **Entry Point / Surface** | Sleek Service Delivery App > Companies list |
| **Short Description** | Delivery staff search and filter the paginated company list by name, company number, lifecycle status, assigned staff roles, specific assignees, and staffing gaps. Each row includes a computed `unassignedRolesCount` so teams can immediately identify clients with uncovered service roles. |
| **Variants / Markets** | SG, HK, AU (status enum includes REFERRED_TO_ACRA for SG and REFERRED_TO_ASIC for AU; no explicit market field observed) |
| **Dependencies / Related Flows** | sleek-back (MongoDB — authoritative company source of truth via `findOrCreateCompanyFromSleekBack`); sleek-billings (status mapping via `SleekBillingsService.mapCompanyStatus`); task-activities (per-company file/link activity via `TaskActivitiesService`); delivery-staff-assignment (team assignments written by that flow, read here) |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL: `companies`, `team_assignments` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. No explicit market/jurisdiction column on `companies` — are markets inferred solely from status values (REFERRED_TO_ACRA = SG, REFERRED_TO_ASIC = AU)? 2. What front-end surface consumes `GET /companies`? Delivery dashboard, admin portal, or both? 3. UK not evidenced in status enum or RoleType — is it a supported market? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Endpoint
`GET /companies` — `CompaniesController.findAll()` (`companies/controllers/companies.controller.ts:42–52`)
- Auth: `@SleekBackAuth('admin')` on controller class — internal delivery/admin users only
- Returns: `PaginatedResponseDto<Company & { unassignedRolesCount: number }>`

### Query filters (`CompanyPaginationQueryDto`)
| Parameter | Purpose |
|---|---|
| `search` | Full-text LIKE across `company.name`, `company.companyNumber`, `company.status`, `assignedUser.email`, `assignedUser.firstName + lastName` |
| `statuses` | Filter by one or more `CompanyStatus` values (20-value enum covering full CLM lifecycle) |
| `assignedRoles` | Filter companies where at least one team slot matches a given `RoleType` |
| `assignedUserIds` | Filter by specific assigned user IDs |
| `unassignedRoles` | Filter companies missing coverage for given role types (correlated EXISTS subquery) |
| `sortBy` | `createdAt` \| `name` \| `unassignedRolesCount` |

### Computed field: `unassignedRolesCount`
`companies/services/companies.service.ts:136–153` — SQL subquery: `totalRoles (18) − COUNT(assignedUser.id)` per company, computed via `TeamAssignment` join. Exposed per page row to prioritise understaffed clients.

### DB tables touched
- `companies` — `name`, `external_ref_id`, `companyNumber`, `status`, `incorporationDate`
- `team_assignments` — `companyId`, `assignedUserId`, `roleType` (unique index on `[companyId, roleType]`)

### RoleType enum (18 roles)
Team Lead, Accounting Manager, Bookkeeper, Corp Sec I/C, Tax Reviewer, Support I/C, Audit Onboarding I/C, Audit Manager, Audit I/C, Audit Reviewer, CSS I/C, Accountant I/C, Accountant Reviewer, Tax I/C, Tax Manager, Accounting Onboarding I/C, GST I/C, Remediation Accountant

### CompanyStatus lifecycle states (20 values)
DRAFT → PAID_AND_AWAITING_COMPANY_DETAIL → PARTNER_DRAFT / PARTNER_PAID → PAID_AND_INCOMPLETE → PROCESSING_BY_SLEEK → PENDING_KYC → PROCESSING_INCORP_TRANSFER → REFERRED_TO_ACRA / REFERRED_TO_ASIC → LIVE_POST_INCORPORATION → LIVE → CHURN_REQUESTED → CHURN_PROCESS → CHURN → STRIKING_OFF_REQUESTED → STRIKING_OFF → STRIKED_OFF → ARCHIVED

### External dependencies
- `SleekBackService.findCompany(mongoCompanyId)` — fetches canonical company record from sleek-back MongoDB; used in upsert flow (`findOrCreateCompanyFromSleekBack`) that keeps the local PG record in sync
- `SleekBillingsService.mapCompanyStatus()` — translates billing-system status to `CompanyStatus` enum during upsert
- `TaskActivitiesService.findAll({ companyId })` — surfaces per-company task files/links via `GET /companies/:id/task-activities`
