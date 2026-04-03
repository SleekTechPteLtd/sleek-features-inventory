# Browse and look up companies

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Browse and look up companies |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Bookkeeper, Finance User; internal integrations and operator tools |
| **Business Outcome** | Staff and connected systems can find the right client company, see who is assigned, and open a full company record so accounting and document workflows run against the correct entity. |
| **Entry Point / Surface** | Coding Engine REST API under `@ApiTags('company')` (`/company` routes), consumed by Sleek bookkeeping/operator experiences and integrations; exact app navigation is not defined in this repo. |
| **Short Description** | Exposes paginated and filtered company and “all clients” lists (including sort by name, accounting plan tier, document count, supplier count), lightweight lookup by name or IDs, company detail by ID (authenticated), and resource-user views (company IDs by user, by user and role, and role-to-user mapping with Sleek Back user details). List and detail reads are backed by MongoDB and, where needed, aggregates over documents or HTTP calls for supplier-rule counts. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Company data populated or updated via `syncCompanies` / platform sync and Kafka `companyDataSync` (see company-listener inventory). **Downstream:** Document counts per company use `documents` in the receipts DB; supplier rule counts call external `VITE_APP_SUPPLIER_RULES_API`. **Sleek Back:** `getUsersInfoFromSleekBack` for role mapping; accountant display fields on `getCompanyById` via `getUserInfoFromSleekBack` for team leaders. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | companies (connection `CODING_ENGINE` / `sleek_acct_coding_engine`); documents on `SLEEK_RECEIPTS` connection for distinct company resolution, counts, and aggregates in list paths |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Several list endpoints have no `AuthGuard` on the controller—confirm whether a gateway or network policy enforces auth. Whether production UIs rely on `GET /company` vs `GET /company/all-clients/*` for the same workflows. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller (HTTP surface)** — `src/company/company.controller.ts`: `GET /company` → `getCompaniesList` (`GetAllRequest`: supplier, skip, limit, company_name); `GET /company/:companyId` + `AuthGuard` → `getCompanyById`; `GET /company/resource-user/:userId` → `getCompanyIdsByResourceUser`; `GET /company/resource-user/:userId/roles?roles=` → `getCompanyIdsByResourceUserAndRoles`; `POST /company/resource-user/fetch-company-user-roles-mapping` (body `roles`, `company_ids`) → `fetchCompanyUserRolesMapping`; `GET /company/all-clients/list` and `GET /company/all-clients/lookup` → `getAllClientsList` / `getAllClientsListLookup` with `GetCompaniesDto` (page, limit, companyName, companyIds, userId, sortProperty, sortOrder, filteredByActiveReceiptSystem, getDocumentSubmission). Swagger `@ApiOperation` summaries describe “Companies list”, “Company details by company id”, “All Clients (Companies) Paginated List”, etc.
- **List by documents + companies** — `CompanyService.getCompaniesList`: builds company filter from distinct `company` on `documentModel` (optional supplier regex on documents), then `companyModel` find with optional `company_name` regex, sort by `company_name`, skip/limit, returns `{ total, data }`.
- **All clients list** — `CompanyService.getAllClientsList`: `GetCompaniesDto` drives pagination (`page`/`limit`), filters (`userId` on `resource_users`, `companyName`, optional `receipt_system_status: active`), aggregation pipeline with optional sort (company name, accounting plan ordering from `active_subscriptions`, functional currency, document count, supplier count); per-row enrichment with `documentModel` counts, distinct suppliers, and `getSpecificRulesCountByCompanyId` (HTTP GET to supplier-rules service). Returns `CompaniesResponseDto` with `pagination.totalData` / `totalPages`.
- **Lookup variant** — `CompanyService.getAllClientsListLookup`: active receipt system only; optional name regex and `companyIds`; optional `document_submission` in projection; collation sort on `company_name`; returns `{ total, data }` with selected fields.
- **Detail** — `CompanyService.getCompanyById`: `companyModel.findOne` by `company_id`; enriches `resource_users` with `assignAccountantInfoIntoResourceUsers` / Sleek Back for accounting-team-leader display fields.
- **Resource user resolution** — `getCompanyIdsByResourceUser`, `getCompanyIdsByResourceUserAndRoles` (`distinct` on `company_id` with `resource_users` `$elemMatch`); `fetchCompanyUserRolesMapping` aggregates companies by IDs, filters `resource_users` by role types, joins user emails/names via `sleekBackService.getUsersInfoFromSleekBack`.
- **Schema** — `src/company/models/company.schema.ts`: `Company` model fields used in these reads include `company_id`, `company_name`, `uen`, `resource_users`, `active_subscriptions`, `accounting_settings`, `receipt_system_status`, `document_submission`, etc.
- **Out of scope for this capability (same module):** `POST /company/sync`, `PUT /company/update`, and email/sync helpers are separate operational or write flows; they are not required to describe browse/lookup but relate as data sources for fresh company rows.
