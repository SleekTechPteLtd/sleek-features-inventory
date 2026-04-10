# Sync Role Assignments from Admin App

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Sync Role Assignments from Admin App |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Delivery Operator (manual trigger); System (automated hourly scheduler) |
| **Business Outcome** | Eliminates manual data entry when onboarding a company by pulling authoritative staff role allocations from the admin app (sleek-back) into the delivery platform, keeping team assignments in sync without operator effort. |
| **Entry Point / Surface** | Sleek Billings App > Delivery > Team Assignments > [Select Company] > "Retrieve from Admin App" button; also triggered automatically every hour via BullMQ scheduler on app startup |
| **Short Description** | Fetches staff resource allocations from sleek-back for a given company, maps them to SDS role types using a platform-specific mapping (SG/HK/AU/UK), and creates or updates team assignment records for any unassigned roles. Runs both on-demand (operator action) and automatically (hourly, for companies with recently updated allocations). |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | sleek-back admin app (`getCompanyResourceAllocations`, `getCompanyIdsWithUpdatedCompanyResourceUsers`); TasksService (propagates assignee to open tasks); AutoMarkRulesService (auto-marks tasks Done on role assignment); BullMQ queues: team-assignment-sync-queue, update-tasks-bulk-queue, auto-mark-for-companies-queue |
| **Service / Repository** | sleek-service-delivery-api, sleek-billings-frontend, sleek-back (admin app, external source) |
| **DB - Collections** | team_assignments, companies, users, tasks, task_activities (PostgreSQL) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Sync is additive — only fills unassigned roles; does the hourly scheduler use the PLATFORM_REGION env var correctly across all deployment regions? Sleek-back users not found in SDS are silently skipped — is this gap reported anywhere? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### UI — `pages/Delivery/TeamAssignments.jsx` (sleek-billings-frontend)

- `syncingCompanyId` state (line 115): tracks which company is mid-sync to drive loading/disabled state on the button.
- `handleFetchStaffAssigned` (line 901–929): handler triggered by the "Retrieve from Admin App" button.
  - Guards against missing `selectedCompany.id`.
  - Reads `billingConfig.platform` from localStorage (defaults to `"sg"`).
  - Calls `sleekServiceDeliveryApi.retrieveFromAdminApp({ companyId, platform })`.
  - On success, calls `updateCompanyAssignments()` to refresh the local company state without a full table reload.
  - Surfaces success/error snackbar notifications.
- `updateCompanyAssignments` (line 618–640): fetches the company by ID via `getCompanyById`, then rebuilds `roleAssignments` map and `unassignedRolesCount` from the updated `teamAssignments` array.
- Button render (line 1594–1604): labelled "Retrieve from Admin App", outline/primary style, disabled and shows loading spinner while `syncingCompanyId === selectedCompany?.id`.

### Service — `services/service-delivery-api.js` (sleek-billings-frontend)

- `retrieveFromAdminApp` (line 547–555): `POST /team-assignments/retrieve-from-admin-app` with `{ companyId, platform }` payload.
- Auth headers: `Authorization: Bearer <token>` (OAuth) or raw token; `App-Origin: "admin"` or `"admin-sso"`.
- Related team-assignment endpoints on the same client: `getAllTeamAssignments`, `createTeamAssignment`, `updateTeamAssignment`, `bulkUpdateTeamAssignments`, `deleteTeamAssignment`.

### API — `team-assignments/controllers/team-assignments.controller.ts` (sleek-service-delivery-api)

- `POST /team-assignments/retrieve-from-admin-app` — `@SleekBackAuth('admin')` guard; body: `RetrieveFromAdminAppDto { companyId: UUID, platform: 'sg'|'hk'|'au'|'uk' }`; returns `{ message: string }`.
- `createdBy` resolved from `req.user?.uuid ?? 'system'`.

### Core logic — `team-assignments/services/team-assignments.service.ts` (`retrieveFromAdminApp`)

1. Validates company exists via `companyRepository`.
2. Calls `sleekBackService.getCompanyResourceAllocations(company.external_ref_id)` — fetches current allocations from admin app.
3. Loads existing `team_assignments` for the company.
4. For each allocation, maps `allocation.type` → SDS `RoleType[]` using `RESOURCE_ALLOCATION_TO_SDS_ROLE_TYPES[platform]`.
5. Resolves sleek-back `user._id` → SDS user ID via `users.external_ref_id`; skips if not found.
6. **Additive only** — skips roles that already have an `assignedUserId` set.
7. Calls `create()` / `update()` for each unassigned slot, which also triggers `tasksService.updateTasksByCompanyAndRoleType` and `evaluateAutoMarkDoneOnRoleAssignment`.

### Role mapping — `team-assignments/constants/resource-allocation-to-role-mapping.constant.ts`

Platform-specific mapping (sleek-back allocation type → SDS RoleType):

| sleek-back type | SG | HK | AU | UK |
|---|---|---|---|---|
| accounting-payroll | TEAM_LEAD | — | — | — |
| accounting-team-leader | ACCOUNTANT_IC | TEAM_LEAD | ACCOUNTANT_IC | ACCOUNTANT_REVIEWER |
| accounting-manager | ACCOUNTING_MANAGER | ACCOUNTING_MANAGER | TEAM_LEAD + ACCOUNTING_MANAGER | TEAM_LEAD + ACCOUNTING_MANAGER |
| cs-in-charge | CORPORATE_SECRETARY_IC | CORPORATE_SECRETARY_IC | CORPORATE_SECRETARY_IC | CORPORATE_SECRETARY_IC |
| css-in-charge | SUPPORT_IC | SUPPORT_IC | SUPPORT_IC | SUPPORT_IC |
| customer-champion | CSS_IC | — | CSS_IC | — |
| auditor | — | AUDIT_IC | — | — |
| accounting-bookkeeper | — | ACCOUNTANT_IC | — | ACCOUNTANT_IC |
| tax-executive | TAX_IC | TAX_IC | TAX_IC | TAX_IC |

### Automated scheduler — `team-assignments/team-assignment-sync.scheduler.ts` + `team-assignment-sync.processor.ts`

- `TeamAssignmentSyncScheduler.onModuleInit()`: registers a repeatable BullMQ job (every hour) on app startup.
- `TeamAssignmentSyncProcessor` (concurrency 1):
  - `enqueue-companies` job: calls `sleekBackService.getCompanyIdsWithUpdatedCompanyResourceUsers(oneHourAgo)`, maps external IDs to SDS company IDs, enqueues one `sync-company` job per company (jobId prevents duplicates).
  - `sync-company` job: reads `PLATFORM_REGION` env var, calls `teamAssignmentsService.retrieveFromAdminApp({ companyId, platform }, masterUser.id)`.

### DB tables touched

- `team_assignments` — upserted; unique index on `(companyId, roleType)`.
- `companies` — read by `id` and `external_ref_id`.
- `users` — read by `external_ref_id` (to resolve sleek-back user IDs) and `isMasterUser` (scheduler auth).
- `tasks` — updated via `TasksService.updateTasksByCompanyAndRoleType` when a role slot is filled.
- `task_activities` — audit log rows written when tasks are auto-marked Done.
