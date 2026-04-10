# Manage Company Role Assignments

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Company Role Assignments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Delivery Operator (internal admin user) |
| **Business Outcome** | Ensures every client company has the right internal team members assigned across all service disciplines, so work is routed to responsible owners and nothing falls through the cracks. |
| **Entry Point / Surface** | Sleek Admin App > Delivery > Team Assignments |
| **Short Description** | Delivery operators see a paginated, searchable list of all companies with their current team member assignments across 18 roles grouped into General, Accounting, Audit, Tax, and Corporate Secretary categories. From the same view, operators can assign or update a team member for any role on any company via a modal dialog. On the backend, each assignment is stored as a `(companyId, roleType)` record; saving one cascades to re-assign all open tasks for that role and triggers auto-mark Done rule evaluation. |
| **Variants / Markets** | SG, HK (platform-aware via `billingConfig.platform`; company status options are market-specific) |
| **Dependencies / Related Flows** | Bulk Assign Team Members Across Companies (bulk mode embedded in same page); Configure Auto-Assignment Rules by Role (auto-assignment drawer, same page); Sync Role Assignments from Admin App (per-company sync action); TasksService.updateTasksByCompanyAndRoleType (cascades assignee onto open tasks); AutoMarkRulesService.evaluateOnRoleAssigned (auto-mark Done on role assignment); BullMQ queues: UpdateTasksBulkQueue, AutoMarkForCompaniesQueue |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL tables: `team_assignments` (unique on `companyId + roleType`), `companies`, `users`, `tasks`, `task_activities` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Are any markets beyond SG/HK supported? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Component
`src/pages/Delivery/TeamAssignments.jsx`

**Role categories and roles (lines 43–81):**
- **General**: Team Lead, Support I/C, CSS I/C
- **Accounting**: Accounting Onboarding I/C, Accounting Manager, Accountant I/C, Accountant Reviewer, Bookkeeper, Remediation Accountant
- **Audit**: Audit Onboarding I/C, Audit Manager, Audit I/C, Audit Reviewer
- **Tax**: Tax I/C, Tax Manager, Tax Reviewer, GST I/C
- **Corporate Secretary**: Corp Sec I/C

Role type values sourced from `src/lib/constants.jsx` `ROLE_TYPES` (lines 360–379).

**Data loading (lines 183–261):**
- `fetchCompanies()` calls `sleekServiceDeliveryApi.getAllCompanies()` with `page`, `limit`, `sortBy`, `sortOrder`, `search`, `assignedUserIds`, `unassignedRoles`, `statuses`, `assignedRoles` query params.
- Default sort: `sortBy=unassignedRolesCount DESC` — surfaces companies with the most gaps first.
- Server-side pagination (default 20 per page).

**Single assignment flow (lines 545–688):**
- `handleAssignClick(company, role)` opens a modal pre-populated with the current assignee.
- `handleAssignSubmit()`: checks for an existing `teamAssignment`; calls `updateTeamAssignment(id, { assignedUserId, updatedBy })` (PATCH) if one exists, otherwise `createTeamAssignment({ companyId, roleType, assignedUserId, createdBy })` (POST).
- After save, refreshes only the affected company row via `sleekServiceDeliveryApi.getCompanyById(id)`.

**Filtering (lines 158–531):**
- Filter drawer supports filtering by: assigned user(s), unassigned roles, company status.
- URL search param (`?search=`) persists and restores search state across navigation.

**Auto-assignment (lines 290–311):**
- `fetchAutoAssignments()` → `GET /auto-assignments`; results displayed in a sidebar drawer for default-per-role configuration.

**Sync (lines 907–911):**
- `handleFetchStaffAssigned()` → `sleekServiceDeliveryApi.retrieveFromAdminApp({ companyId, platform })` → `POST /team-assignments/retrieve-from-admin-app`.

### Backend API — sleek-service-delivery-api

**Controller:** `src/team-assignments/controllers/team-assignments.controller.ts`
**Auth guard:** `@SleekBackAuth('admin')` — admin-only access on all routes.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/team-assignments` | Create or upsert a single role assignment (idempotent by `companyId + roleType`) |
| POST | `/team-assignments/bulk-update` | Bulk upsert across many companies; partial success supported; enqueues BullMQ jobs |
| POST | `/team-assignments/retrieve-from-admin-app` | Sync from sleek-back resource allocations; only fills unassigned roles |
| GET | `/team-assignments` | List all assignments, optional `?companyId` filter |
| GET | `/team-assignments/:id` | Get single assignment |
| PATCH | `/team-assignments/:id` | Update assignee (pass `assignedUserId: ""` to unassign) |
| DELETE | `/team-assignments/:id` | Remove assignment; unassigns all open tasks for that role |

**Entity:** `src/team-assignments/entities/team-assignment.entity.ts`
- PostgreSQL table `team_assignments`; unique index on `(companyId, roleType)`
- `assignedUserId` nullable (SET NULL on user delete); cascades on company delete

**Role types** (`src/common/enums/role-type.enum.ts`):
Team Lead, Accounting Manager, Bookkeeper, Corp Sec I/C, Tax Reviewer, Support I/C, Audit Onboarding I/C, Audit Manager, Audit I/C, Audit Reviewer, CSS I/C, Accountant I/C, Accountant Reviewer, Tax I/C, Tax Manager, Accounting Onboarding I/C, GST I/C, Remediation Accountant (18 roles).

**Side effects on assignment change** (`TeamAssignmentsService`):
1. `TasksService.updateTasksByCompanyAndRoleType()` — re-assigns all open tasks for the role to the new user (or null on unassign/delete).
2. `AutoMarkRulesService.evaluateOnRoleAssigned()` — checks auto-mark Done rules; if a rule fires, tasks are updated to `DONE` and audit `task_activities` rows are created.
3. Bulk path enqueues `UpdateTasksBulkJob` and `AutoMarkForCompaniesJob` via BullMQ (batches of 500 companies, DB batches of 3000 rows).

**External dependency:** `SleekBackService.getCompanyResourceAllocations()` — called only by `retrieve-from-admin-app` to pull sleek-back resource allocation data mapped to SDS role types via `RESOURCE_ALLOCATION_TO_SDS_ROLE_TYPES`.

### Service
`src/services/service-delivery-api.js`

**Auth (lines 5–17):** Bearer JWT (OAuth) or raw token from `localStorage`. `App-Origin: admin` or `admin-sso`.

**Relevant API calls:**
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/companies` | Paginated company list with assignment data |
| GET | `/companies/:id` | Single company refresh after assignment update |
| GET | `/team-assignments` | Fetch all assignments |
| POST | `/team-assignments` | Create new role assignment |
| PATCH | `/team-assignments/:id` | Update existing role assignment |
| POST | `/team-assignments/bulk-update` | Bulk assign across multiple companies |
| POST | `/team-assignments/retrieve-from-admin-app` | Sync assignments from admin app |
| DELETE | `/team-assignments/:id` | Remove assignment |
| GET | `/auto-assignments` | Fetch default per-role assignments |
| POST | `/auto-assignments` | Create auto-assignment rule |
| PATCH | `/auto-assignments/:id` | Update auto-assignment rule |
| DELETE | `/auto-assignments/:id` | Remove auto-assignment rule |
| GET | `/users` | Fetch assignable internal users (limit 2000) |
