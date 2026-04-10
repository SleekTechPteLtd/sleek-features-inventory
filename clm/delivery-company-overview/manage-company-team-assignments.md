# Manage Company Team Assignments

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Company Team Assignments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Delivery Manager / Admin |
| **Business Outcome** | Ensures each client company has the right staff assigned to every delivery role, enabling accurate task ownership, auto-propagation of assignees to open tasks, and automated completion of role-gated tasks. |
| **Entry Point / Surface** | sleek-service-delivery-api > REST API `/team-assignments` (admin-authenticated) |
| **Short Description** | Delivery managers assign or reassign staff users to specific delivery role types (e.g. accountant, CS, compliance) for each client company. Assignments are propagated to open tasks and can trigger auto-mark-Done rules. Supports single-company, bulk multi-company, and admin-app sync flows. |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | sleek-back (admin app) — source for `retrieve-from-admin-app` sync; `tasks` service — assignees propagated via `updateTasksByCompanyAndRoleType`; `auto-mark-rules` service — evaluates Done rules on role assignment; BullMQ queues: `update-tasks-bulk`, `auto-mark-for-companies` |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | `team_assignments`, `companies`, `users`, `tasks`, `task_activities` (PostgreSQL via TypeORM) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which UI surface (admin app or internal ops tool) drives the manual single-assignment flow vs. the bulk-update flow? What role types are defined in `RoleType` enum and which are mandatory per company? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/team-assignments/controllers/team-assignments.controller.ts`
- `src/team-assignments/services/team-assignments.service.ts`
- `src/team-assignments/entities/team-assignment.entity.ts`
- `src/team-assignments/dto/retrieve-from-admin-app.dto.ts`

### Auth surface
- `@SleekBackAuth('admin')` on entire controller — restricted to admin users authenticated via sleek-back.

### Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/team-assignments` | Create or update a single company-role assignment (upsert by companyId + roleType) |
| POST | `/team-assignments/bulk-update` | Bulk upsert one role across many companies (supports `all` flag with filters) |
| POST | `/team-assignments/retrieve-from-admin-app` | Sync staff from sleek-back resource allocations; fills only unassigned roles |
| GET | `/team-assignments` | List all assignments, optionally filtered by `companyId` |
| GET | `/team-assignments/:id` | Get single assignment |
| PATCH | `/team-assignments/:id` | Update assignment (including unassign by passing empty `assignedUserId`) |
| DELETE | `/team-assignments/:id` | Remove assignment and unassign matching tasks |

### Key service behaviours
- **Task propagation**: every create/update/delete calls `tasksService.updateTasksByCompanyAndRoleType` to update assignee on all open tasks for that company and role.
- **Auto-mark Done**: after a role is assigned, `autoMarkRulesService.evaluateOnRoleAssigned` checks if any tasks should be auto-completed; audit logs written to `task_activities`.
- **Bulk update batching**: DB operations batched at 3,000 rows per query; downstream queue jobs chunked at 500 companies per job to avoid timeouts.
- **Admin app sync** (`retrieveFromAdminApp`): calls `sleekBackService.getCompanyResourceAllocations(company.external_ref_id)`, maps sleek-back resource allocation types to SDS `RoleType` via `RESOURCE_ALLOCATION_TO_SDS_ROLE_TYPES[platform]`; only fills unassigned roles.

### DB entity
- Table: `team_assignments`
- Unique index on `(companyId, roleType)` — one user per role per company.
- `assignedUserId` nullable — null means the role slot exists but is unoccupied.
- Cascade delete on company removal; SET NULL on user removal.
