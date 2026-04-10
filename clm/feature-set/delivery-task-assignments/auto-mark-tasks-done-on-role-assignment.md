# Auto-mark tasks done on role assignment

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Auto-mark tasks done on role assignment |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Keeps delivery progress current automatically — when a required company role is filled, qualifying tasks are immediately marked Done without manual updates. |
| **Entry Point / Surface** | Internal system trigger — fires on `POST /team-assignments`, `PATCH /team-assignments/:id`, and `POST /team-assignments/bulk-update` whenever a non-null `assignedUserId` is set. All endpoints are guarded by `@SleekBackAuth('admin')`; no direct end-user UI surface. |
| **Short Description** | When a role is assigned to a company (individually or in bulk), the platform evaluates `ON_ROLE_ASSIGNED` + `AUTO_MARK_DONE` rules on that company's TO_DO tasks. Tasks whose template conditions are satisfied (e.g., company now has a required role, or a duplicate task exists across subscriptions) are transitioned to Done and an audit activity record is written. For bulk operations the evaluation is offloaded to a BullMQ queue (`auto-mark-for-companies`) to avoid blocking the HTTP response. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `AutoMarkRulesService` (rule evaluation — `COMPANY_HAS_ROLE`, `DUPLICATE_TASK_EXISTS`); `AutoMarkForCompaniesQueueService` / BullMQ (async bulk path); `TasksService` (task assignee propagation by role type); `SleekBackService` (sleek-back resource allocation sync via `retrieve-from-admin-app`); task template `autoMarkCondition` JSONB column (rule storage) |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | `team_assignments`, `tasks`, `task_activities`, `deliverables`, `task_templates` (PostgreSQL via TypeORM) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which role types are configured with `ON_ROLE_ASSIGNED` auto-mark rules in production task templates? Are there markets where this rule is suppressed or conditional? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Trigger paths
- **Single assignment (create/upsert):** `TeamAssignmentsService.create()` — calls `evaluateAutoMarkDoneOnRoleAssignment(companyId, roleType)` synchronously after saving, if `assignedUserId` is non-null. (`team-assignments/services/team-assignments.service.ts:107–112`, `135–140`)
- **Single assignment (update):** `TeamAssignmentsService.update()` — same call when `assignedUserId` changes to a non-null value. (`team-assignments/services/team-assignments.service.ts:490–495`)
- **Bulk update:** `TeamAssignmentsService.bulkUpdate()` — enqueues `AutoMarkForCompaniesQueueService.addAutoMarkForCompaniesJob({ companyIds, roleType })` per 500-company chunk; BullMQ processor (`AutoMarkForCompaniesProcessor`, concurrency 5) calls `runAutoMarkForCompanies()` → `evaluateAutoMarkDoneOnRoleAssignment()` for each company, continuing on individual failures. (`team-assignments/services/team-assignments.service.ts:305–317`; `team-assignments/queues/auto-mark-for-companies-queue.service.ts`; `team-assignments/queues/auto-mark-for-companies.processor.ts`)

### Core evaluation logic (`evaluateAutoMarkDoneOnRoleAssignment`)
1. Calls `AutoMarkRulesService.evaluateOnRoleAssigned(companyId, roleType)`.
2. Queries `tasks` JOIN `deliverables` JOIN `subscriptions` for tasks where:
   - `subscription.companyId = companyId`
   - `task.status = TO_DO`
   - `template.autoMarkCondition` has at least one rule with `trigger = ON_ROLE_ASSIGNED` and `rule = AUTO_MARK_DONE`
3. For each candidate task, evaluates the matching rule condition:
   - **`COMPANY_HAS_ROLE`** — checks `team_assignments` for a non-null `assignedUserId` for the required role → reason: `ROLE_ASSIGNED`
   - **`DUPLICATE_TASK_EXISTS`** (match by `TASK_TEMPLATE_ID`) — checks `tasks` for same template in a different subscription of the same company with status `TO_DO` or `DONE` → reason: `DUPLICATE_TASK`
4. For each qualifying task: updates `tasks.status = DONE`, sets `completedDate`, writes a `task_activities` record with `activityType = STATUS_CHANGE`, `previousStatus = TO_DO`, `newStatus = DONE`, `autoMarkReason`, and `createdBy = 'system'`.

### Key files
- `src/team-assignments/services/team-assignments.service.ts` — orchestration, `evaluateAutoMarkDoneOnRoleAssignment` (private), `runAutoMarkForCompanies` (public, called by processor)
- `src/team-assignments/queues/auto-mark-for-companies-queue.service.ts` — BullMQ job enqueue; jobs kept 7 days on success, 4 weeks on failure
- `src/team-assignments/queues/auto-mark-for-companies.processor.ts` — BullMQ worker, concurrency 5
- `src/team-assignments/queues/auto-mark-for-companies.queue.ts` — queue name constant
- `src/auto-mark-rules/services/auto-mark-rules.service.ts` — `evaluateOnRoleAssigned`, `evaluateCondition`, `checkCompanyHasRole`, `findDuplicateTask`

### Database tables
| Table | Role in this feature |
|---|---|
| `team_assignments` | Read to check if company has required role; written on role assignment |
| `tasks` | Queried for TO_DO candidates; `status` + `completedDate` updated to Done |
| `task_activities` | Audit log written per auto-marked task (STATUS_CHANGE, system actor) |
| `deliverables` | Joined to link tasks → subscriptions → companyId |
| `task_templates` | JSONB `autoMarkCondition` column queried for matching trigger/rule/condition |
