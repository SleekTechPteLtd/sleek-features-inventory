# Assign accounting resources to company users

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Assign accounting resources to company users |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Ensures each company has the correct internal staff mapped to accounting (and related) resource roles, with optional propagation to third-party accounting tools and a clear audit trail when assignments change. |
| **Entry Point / Surface** | Sleek Admin > Companies > company overview / staff & resource allocation (resource roles list and bulk update) |
| **Short Description** | Admins create, replace, remove, and bulk-update per-company assignments of users to resource allocation roles (e.g. accounting bookkeeper, team leader, manager). Reads return all non–stand-alone roles with assigned users. Optional feature flags enqueue UiPath jobs to add or revoke access in external systems (e.g. Xero, Hubdoc, Dext). Changes emit Kafka events for downstream consumers and write auditor logs (legacy and v2). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | App features (`accounting` / `companies` admin) for third-party access toggles and role catalogue; `AccountingQuestionnaire` for external update context; `external-uipath-service` (queued bots); `SleekBackKafkaService` topics `COMPANY_ASSIGNEE_HAD_CHANGED`, `COMPANY_ASSIGNEE_HAD_REMOVED`, and `syncCodingEngineCompanyData` on bulk update; `sleek-auditor-node` for structured audit on bulk PUT; group-level allocation via `CompanyResourceGroup` and `company-resource-group-allocation` routes (related). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyresourceusers`, `resourceallocationroles`, `companies`, `users`, `accountingquestionnaires`; `companyresourcegroups` where group allocation / auto-assign paths apply (service-level). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact Admin UI labels and navigation differ by tenant; markets served are not stated in these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### HTTP surface (`controllers/company-controller.js`)

- **POST** `/companies/:companyId/company-resource-allocation` — `userService.authMiddleware`, `accessControlService.can("companies", "full")`. Body: `userId`, `roleType`. Upserts `CompanyResourceUser`, optional third-party access sync via `handleExternalUpdates`, Kafka `SLEEK_BACK_KAFKA_TOPICS.COMPANY_ASSIGNEE_HAD_CHANGED`, `buildAuditLog` + `auditorService.saveAuditLog` with action context `"assigned resource role"`.
- **GET** `/companies/:companyId/company-resource-allocation` — `userService.authMiddleware`; delegated to `CompanyResourceAllocationHandler.get`.
- **DELETE** `/companies/:companyId/company-resource-allocation` — same guards as POST. Body: `userId`, `roleType`. `findOneAndDelete` on `CompanyResourceUser`, Kafka `COMPANY_ASSIGNEE_HAD_REMOVED`, optional `handleExternalUpdates` for revoke, auditor log `"unassigned resource role"`.
- **PUT** `/companies/:companyId/company-resource-allocations` — bulk update: body `resourceAllocation` object (role type → user id). Uses `hasExistingUpdates` / `isUpdateAllowed` to block or defer when UiPath bots are pending; loads role definitions from app feature `companies.admin.overview.new_ui.new_resource_allocation`; `saveAuditLogV2` with actions `staff-assined.assign` / `staff-assined.unassign`; `handleExternalUpdates` when enabled; `syncCodingEngineCompanyData` after updates.

### Handler (`controllers-v2/handlers/company-resource-allocation/index.js`)

- **GET** loads `Company` (excluding subscriptions field), all `CompanyResourceUser` for the company with `user` populated, and `ResourceAllocationRole` where `is_stand_alone` is null and `is_deleted` ≠ true. Builds sorted list of roles with optional assigned user summary (`userService.formatUserDataName`).

### Service (`services/company-resource-user/company-resource-user-service.js`)

- **Third-party queueing:** `buildPayload` / `handleExternalUpdates` call `addToQueue` (UiPath) for Xero, Hubdoc, Dext-style queue names from config; `hasExistingUpdates` uses `getOpenBots` to detect `IN_PROGRESS` / `QUEUED` work; `isUpdateAllowed` checks `allowedRoleTypes` vs role and open requests.
- **Resolution helpers:** `getResourceAllocationRole`, `getCompanyResourceUsers`, `getAccountingCompanyResourceUsersWithRoleInfoByCompanyId` (aggregates with `resourceallocationroles` and `users` collections).
- **Automation:** `autoAllocateStaff`, `saveUserResourceFromConfig`, `createAndSaveUserResource` support workflow-driven or config-driven assignment including **group** allocation via `CompanyResourceGroup` when `is_group_allocation` is set in tenant config.

### Schemas

- `schemas/company-resource-user.js` — `company`, `user`, `resource_role`, dates, `data` mixed (used for non-accounting resource types elsewhere).
- `schemas/resource-allocation-role.js` — `type`, `title`, `order`, `is_stand_alone`, `is_deleted`.
