# Monitor Delivery Tasks Across Client Engagements

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor delivery tasks across client engagements |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Sleek internal staff managing client service delivery) |
| **Business Outcome** | Enables operations teams to identify overdue and upcoming delivery tasks across all client subscriptions in a single view, supporting workload prioritisation and preventing SLA breaches. |
| **Entry Point / Surface** | Sleek App > Delivery > Tasks (`/delivery/tasks`) |
| **Short Description** | A tabbed dashboard showing delivery tasks across all client subscriptions, segmented by due status (Overdue, Due Soon, Not Due, Completed). Operators can filter by assignee, company, role, label, delivery status, FYE, and task type; perform bulk status and date changes; and drill into individual task details. |
| **Variants / Markets** | SG, HK, AU (priority labels are market-specific; UK not evidenced in label enums) |
| **Dependencies / Related Flows** | Delivery Overview (`/delivery/overview`); Team Assignments (`/delivery/task-assignments`); Subscription Progress page; sleek-service-delivery API; sleek-billings-api (subscription lookup for upgrade/downgrade navigation) |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL tables: `tasks`, `deliverables`, `subscriptions`, `companies`, `task_templates`, `users`, `task_activities` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which markets (SG, HK, UK, AU) is this available in? UK not evidenced in priority-label enum — confirm. 2. Is there a dedicated Sleek App frontend entry point for UK/HK or is it the same UI with filtered data? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files (backend — sleek-service-delivery-api)
- `src/tasks/controllers/tasks.controller.ts` — `@Controller('tasks') @SleekBackAuth('admin')`: internal-only admin API; exposes `POST /tasks/search`, `GET /tasks`, `GET /tasks/:id`, `PATCH /tasks/:id`, `DELETE /tasks/:id`, `POST /tasks/change-task-status`, `POST /tasks/bulk-change-task-status`
- `src/tasks/services/tasks.service.ts` — `searchTasks()`: builds a TypeORM query joining `tasks → deliverables → subscriptions → companies → task_templates → assignedUser`; applies all filter dimensions
- `src/tasks/dto/search-tasks.dto.ts` — defines `SearchTasksDto` with: `searchTerm`, `taskDueStatus` (OVERDUE/DUE_SOON/NOT_DUE/COMPLETED), `assignedUserIds`, `assignedRoleTypes`, `filterByUnassigned`, `filterByAssigned`, `filterMilestoneTasks`, `taskStatuses`, `taskTemplateIds`, `subscriptionLabels`, `subscriptionDeliveryStatuses`, `serviceFyeYears`, `companyIds`, `filterBySubscriptionRefNumber`, `sortBy`
- `src/tasks/entities/task.entity.ts` — `@Entity('tasks')` PostgreSQL table; columns: `name`, `companyId`, `description`, `status` (TO_DO/NOT_REQUIRED/DONE/ARCHIVED), `dueDate`, `completedDate`, `deliverableId`, `templateId`, `assignedUserId`, `taskStartDate`, `taskEndDate`; virtual getters: `isProofOfCompletionRequired`, `isMilestone`

### Auth surface
`@SleekBackAuth('admin')` on the controller — all task endpoints require an internal Sleek admin token; not exposed to end clients.

### Database
- **Engine: PostgreSQL** (TypeORM entities with `@Entity` / `@Column` decorators — not MongoDB)
- **Tables joined in `searchTasks`:** `tasks`, `deliverables`, `subscriptions`, `companies`, `task_templates`, `users`
- **Indexed columns:** `(templateId, status)`, `(templateId, status, deliverableId)`, `deliverableId`, `companyId`, `assignedUserId`, `(status, dueDate)`, `(status, completedDate)`

### Due-status filter logic (backend)
| `taskDueStatus` | SQL condition |
|---|---|
| `OVERDUE` | `dueDate < today AND status = TO_DO` |
| `DUE_SOON` | `today < dueDate ≤ today + 14 days AND status = TO_DO` |
| `NOT_DUE` | `(dueDate IS NULL OR dueDate > today + 14 days) AND status = TO_DO` |
| `COMPLETED` | `status IN (DONE, NOT_REQUIRED)` |

### Market evidence
`SubscriptionPriorityLabel` enum in `subscription.entity.ts` has explicit market comments:
- SG: AGM_DUE_SOON, CLIENT_ESCALATION, HIGH_TRANSACTION_VOLUME, SLEEK_ND, UNRESPONSIVE_CLIENT
- HK: PTR_RECEIVED, COURT_SUMMONS_RECEIVED, PENALTIES_RECEIVED
- AU: ATO_DUE_SOON, BAS_DUE_SOON, COMPLIANCE_ACTION_REQUIRED, CRITICAL_BUSINESS_EVENT, BACKLOG_WORK, COMPLEX_TRANSACTIONS
- UK: not represented in label enum

### API calls (via `sleekServiceDeliveryApi`)
| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/tasks/search` | Paginated task search with due-status filter, multi-dimension filters, sort, and search term |
| `GET` | `/users?limit=2000` | Populate assignee filter options |
| `GET` | `/companies?page=1&limit=100[&assignedUserIds=]` | Populate company filter options (all / assigned-to-me modes) |
| `GET` | `/deliverable-templates` | Populate task-template filter (task name search) |
| `POST` | `/tasks/change-task-status` | Single task status change (complete / not-required / reopen) |
| `POST` | `/tasks/bulk-change-task-status` | Bulk status change across selected tasks |

Also calls `sleekBillingsApi.getCustomerSubscriptionsByCompanyId` when navigating to a replacement subscription from an upgraded/downgraded discontinued subscription row.

### Files (frontend — sleek-billings-frontend)
- `src/pages/DeliveryTasks/TasksDashboard.jsx` — top-level dashboard; hosts filter drawer, tab bar, search inputs, renders `TasksList` per tab
- `src/pages/DeliveryTasks/TasksList.jsx` — paginated, sortable task table with bulk-select toolbar

### Route
- Registered in `src/App.jsx:211`: `<Route path="delivery/tasks" element={<TasksDashboard />} />`
- Linked from `DeliveryOverview.jsx` and `TeamAssignments.jsx` with pre-filled `?search=` and `?subscriptionRefNumber=` query params

### Tab / due-status segmentation
`TasksDashboard` renders four `TasksList` instances, each with a `dueStatus` prop:

| Tab label | `dueStatus` value |
|---|---|
| Overdue | `OVERDUE` |
| Due soon (Next 2 weeks) | `DUE_SOON` |
| Not Due | `NOT_DUE` |
| Completed | `COMPLETED` |

Default active tab on load: `OVERDUE`.

### Task table columns
Select checkbox, Company name (link to Delivery Overview), Labels (priority labels), Task name, Task status (actionable), Task due date (actionable, overdue badge), Task completion date (completed/all views), Assignee (link to Team Assignments), Subscription name, Delivery status (with tooltip for discontinued/deactivated/upgraded states), Subscription period, Service FYE.

### Filter dimensions
Assignee (user, unassigned, assigned), Company, Role type, Priority label, Subscription delivery status (`toBeStarted`, `active`, `toOffboard`, `discontinued`, `deactivated`), Service FYE year, Milestone tasks toggle, Task template (name search), Task status (To Do, Done, Not Required).

### Bulk actions (floating toolbar on selection)
- Change status (via `BulkChangeStatusModal`)
- Edit due date (via `BulkEditDueDateModal`)
- Edit completion date — shown only when all selected tasks are Done or Not Required (via `BulkEditCompletionDateModal`)

### Default filters on load
- `filterByUsers`: logged-in user's ID (self-filtered by default, cleared if URL has a `?search=` param)
- `filterByDeliveryStatuses`: `toBeStarted`, `active`
- `filterByServiceFYEs`: current year − 1, current year
