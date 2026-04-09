# Company people and resource access for internal services

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Company people and resource access for internal services |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Internal Sleek services can resolve who is tied to a company—client company users, receipt users, and accounting resource staff with role metadata—so downstream automation can enforce permissions, route work, and run accounting workflows consistently. |
| **Entry Point / Surface** | Internal HTTP API on sleek-back (internal-services router): `GET /internal/companies/:companyId/company-users`, `GET /internal/companies/:companyId/receipt-users`, `GET /internal/companies/:companyId/resource-users`, `GET /internal/companies/:companyId/accounting-resource-users-with-role-info-by-company-id`. Guard: `internalServicesMiddleware()` — Basic auth with shared secret (`Authorization: Basic …`); optional bypass via internal-service config. Not intended for browser or public clients. |
| **Short Description** | For a valid `companyId`, returns company users with populated `user` documents; receipt users for that company; all company resource users limited to accounting bookkeeper / team leader / manager roles (populate `user`); or an aggregation of accounting resource users (bookkeeper, team leader, manager, payroll) joined to `resourceallocationroles` and `users` with projected role title, type, and user email. Invalid ObjectIds return `COMPANY_RESOURCE_USER.INVALID_QUERY`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Resource allocation**: `ResourceAllocationRole` types (`accounting-bookkeeper`, `accounting-team-leader`, `accounting-manager`, `accounting-payroll`). **Related internal company APIs** on the same controller: company search (`POST /internal/companies`, `GET /internal/findAllCompanies` with optional `include_company_users` aggregation into `companyusers` + `users`), accounting questionnaire routes — separate capabilities. **Downstream**: callers use results for permissions, routing, and accounting automation (not enumerated in these files). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyusers` (read; `CompanyUser.find` by `company`); `receiptusers` (read; `ReceiptUser.find` by `company`); `companyresourceusers` (read; `CompanyResourceUser.find` with `resource_role` in accounting roles); `resourceallocationroles` (read; role lookup and aggregation `$lookup`); `users` (read; populate and aggregation `$lookup`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which named internal services or jobs call each route is not listed in these files. Whether markets differ in role availability or receipt-user shape is not encoded here. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/internal-service/company-controller.js`

- **`internalServicesMiddleware()`** on all routes — internal server-to-server auth (Basic secret); see `middlewares/internal-services.js`.
- **`GET /internal/companies/:companyId/resource-users`** — Validates `companyId` as Mongo ObjectId; `companyResourceUserService.getCompanyResourceUsers(companyId)`.
- **`GET /internal/companies/:companyId/accounting-resource-users-with-role-info-by-company-id`** — Same validation; `companyResourceUserService.getAccountingCompanyResourceUsersWithRoleInfoByCompanyId(companyId)`.
- **`GET /internal/companies/:companyId/company-users`** — Same validation; `CompanyUser.find({ company })` with `populate(["user"])`.
- **`GET /internal/companies/:companyId/receipt-users`** — Same validation; `ReceiptUser.find({ company: companyId })`.
- **`GET /internal/findAllCompanies`** (optional related evidence) — When `include_company_users` is true, aggregates `$lookup` from `companyusers` and `users` for embedded company user lists on company search.

### `services/company-resource-user/company-resource-user-service.js`

- **`getCompanyResourceUsers(companyId)`** — Loads `ResourceAllocationRole` for types `accounting-bookkeeper`, `accounting-team-leader`, `accounting-manager`; `CompanyResourceUser.find` by `company` and `resource_role` in those roles; `populate("user")`.
- **`getAccountingCompanyResourceUsersWithRoleInfoByCompanyId(companyId)`** — Delegates to `getCompanyResourceUsersWithRoleInfoByCompanyId` with `validResourceAllocationRoles`: `accounting-bookkeeper`, `accounting-team-leader`, `accounting-manager`, `accounting-payroll`.
- **`getCompanyResourceUsersWithRoleInfoByCompanyId`** — Aggregation: `$lookup` `resourceallocationroles` as `company_resource_role`, `$lookup` `users` as `user_details`, `$match` on nested `company_resource_role.type`, `$project` fields including `resource_role_name`, `resource_role_type`, `user_email`.
- Other exports on the same service (`autoAllocateStaff`, `handleExternalUpdates`, UiPath queues, etc.) support broader resource-allocation and automation flows but are not invoked by these internal GET routes.

### `schemas/company-user.js`

- **Model `CompanyUser`** — `company` / `user` refs; role enum from `sharedData.companyUsers.role`; permissions (`can_invite`, `can_see_invoices`, `is_owner`, …); invitation and KYC-related fields; hooks to `pbacService.setDefaultPolicy` on save/delete (policy side effects when mutating company users — reads here do not trigger those write hooks beyond normal read path).

### `schemas/receipt-user.js`

- **Model `ReceiptUser`** — `company` ref; `emails`, `access_levels` (company receipts, expense claims, approve expense claims); `status` / `status_v2` for Sleek Receipts user lifecycle.

### `schemas/company-resource-user.js`

- **Model `CompanyResourceUser`** — `company`, `user`, `resource_role` → `ResourceAllocationRole`; `appointed_date`, `cessation_date`, `is_removed`; flexible `data` object for role-specific payloads.
