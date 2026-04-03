# Resolve resource user company access

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Resolve resource user company access |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System (integrations calling Coding Engine) |
| **Business Outcome** | Operators and downstream services can see which client companies a resource user may work on and under which roles, so routing, filtering, and authorization stay aligned with SleekBack assignments. |
| **Entry Point / Surface** | Coding Engine HTTP API under `/company` (resource-user routes and client list filtered by user); data is populated when companies sync from Sleek Platform / SleekBack. |
| **Short Description** | Exposes company IDs for a user from stored `resource_users`, optionally filtered by `resource_role_type`, and a bulk mapping of roles to users per company. Company sync copies accounting resource users and roles from SleekBack into MongoDB so this view stays current. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | SleekBack (`getAccountingCompanyResourceUsersWithRoleInfoFromSleekBack`, `getUsersInfoFromSleekBack`); company sync from Platform; JWT `user.companies` used elsewhere (`UserAuthorizationService` / `CompanyAccessGuard`) for per-request company checks — related but not the same code path as these list endpoints. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `companies` (Coding Engine MongoDB connection `acct_coding_engine` / `DBConnectionName.CODING_ENGINE`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether the resource-user GET routes are intended to be called without `AuthGuard` in production (only `GET /company/:companyId` uses `AuthGuard` in this controller); confirm market-specific behaviour if any. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** (`src/company/company.controller.ts`): `GET company/resource-user/:userId` → `getCompanyIdsByResourceUser`; `GET company/resource-user/:userId/roles` with query `roles` → `getCompanyIdsByResourceUserAndRoles`; `POST company/resource-user/fetch-company-user-roles-mapping` with body `roles` and `company_ids` → `fetchCompanyUserRolesMapping`. `GET company/all-clients/list` supports filtering by `userId` in the query (accountant-scoped client list via `resource_users` match in the service).
- **Service** (`src/company/company.service.ts`): `getCompanyIdsByResourceUser` queries `companyModel` with `resource_users: { $elemMatch: { user_id } }` and `distinct('company_id')`. `getCompanyIdsByResourceUserAndRoles` adds `resource_role_type: { $in: roles }`. `fetchCompanyUserRolesMapping` aggregates companies by `company_id`, filters embedded `resource_users` by role types, then enriches with user email/name via `sleekBackService.getUsersInfoFromSleekBack`. `syncCompanies` loads resource users via `sleekBackService.getAccountingCompanyResourceUsersWithRoleInfoFromSleekBack`, maps IDs with `mapResourseUsers`, and persists on `updateOrCreateCompany`. `companyDataSync` / `getCompanyResourceUsers` refresh `resource_users` from SleekBack on updates.
- **Schema** (`src/company/models/company.schema.ts`): `resource_users` array on `Company` stores per-user linkage and role metadata used by the queries above.
- **Related auth** (`src/common/auth/user-authorization.service.ts`, `company-access.guard.ts`): `assertCompanyAccess` checks `user.companies` for non-privileged users — complements company-scoped HTTP protection; list resolution for resource users is driven from DB `resource_users` as described above.
