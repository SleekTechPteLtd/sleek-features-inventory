# Manage Delivery Task Assignments

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Delivery Task Assignments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Delivery Manager (admin) |
| **Business Outcome** | Enables delivery managers to create execution tasks from templates linked to client deliverables and transfer ownership between team members, ensuring every piece of client work has a clear, accountable assignee. |
| **Entry Point / Surface** | Sleek Admin App > Delivery > Task Tracker |
| **Short Description** | A paginated task tracker where managers create tasks by selecting a deliverable and a task template, set due dates and initial assignees, and reassign tasks inline to a different team member at any time. Status lifecycle spans PENDING → IN_PROGRESS → COMPLETED / CANCELLED. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Deliverables (tasks must be linked to one); Task Templates (tasks created from a template); Users list (assignment/reassignment target); Task Activities (audit trail); Company/Subscription chain (company name derived from deliverable.subscription.company); Task Analytics (`/analytics/tasks`, `/analytics/task-distribution/*`) |
| **Service / Repository** | sleek-billings-frontend (UI), service-delivery-api (backend, `VITE_SERVICE_DELIVERY_API_URL`) |
| **DB - Collections** | Unknown (backend not in scope; frontend calls REST API only) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `createdBy` is hardcoded to `"admin"` in the create form — placeholder or intentional? No visible role/permission guard — is access restricted to delivery managers at the API level? No market-specific logic observed — which markets use this? DB collections unknown (backend not inspected). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### UI — `pages/Delivery/TaskTracker.jsx`

- **`TaskTracker` component** (line 141): top-level page rendered at the Delivery > Task Tracker route.
- **Create task flow** (`handleCreate` / `handleSubmit`, lines 220–258):
  - Required fields: `name`, `deliverableId`, `templateId`.
  - Optional: `description`, `status` (default `PENDING`), `dueDate`, `actualHours`, `assignedUserId`, `createdBy` (hardcoded `"admin"`).
  - Calls `sleekServiceDeliveryApi.createTask(payload)` → `POST /tasks`.
- **Reassign task flow** (`handleReassign` / `handleReassignSubmit`, lines 260–285):
  - Triggered by inline **Reassign** button in the Assigned User column.
  - Shows a dialog with current assignee and a user select (up to 2 000 users fetched).
  - Supports "None (Unassign)" option — sets `assignedUserId: null`.
  - Calls `sleekServiceDeliveryApi.updateTask(id, { assignedUserId })` → `PATCH /tasks/:id`.
- **Table columns**: ID, Name, Company (`item.deliverable.subscription.company.name`), Assigned User + Reassign button, Status (colour-coded badge), Due Date, Completed Date, Actual Hours, Deliverable ID, Created At.
- **Pagination**: 100 items/page via `getAllTasks({ page, limit: 100 })`.
- **Supporting lookups on mount**: `getAllDeliverables({ limit: 100 })`, `getAllTaskTemplates({ limit: 100 })`, `getAllUsers({ limit: 2000 })`.

### API client — `services/service-delivery-api.js`

- Base URL: `VITE_SERVICE_DELIVERY_API_URL` (separate service-delivery backend).
- Auth: Bearer JWT (OAuth) or raw token; `App-Origin: admin | admin-sso`.
- **Task endpoints used by this feature**:
  - `GET  /tasks` — paginated list (line 254)
  - `POST /tasks` — create (line 272)
  - `PATCH /tasks/:id` — update / reassign (line 281)
- **Additional task endpoints present in service** (not directly used by TaskTracker but part of the same capability surface):
  - `GET  /tasks/:id`, `DELETE /tasks/:id`
  - `POST /tasks/search` (line 570)
  - `POST /tasks/change-task-status` (line 598)
  - `POST /tasks/bulk-change-task-status` (line 607)
- **Task template endpoints**: `GET/POST/PATCH/DELETE /task-templates` (lines 155–198).
- **Task activity endpoints**: `GET/POST/PATCH/DELETE /task-activities`, `/task-activities/upload` (lines 615–689) — audit/comment trail per task.
- **Analytics**: `GET /analytics/tasks` (line 760); `GET /analytics/task-distribution/*` (lines 901–963).
