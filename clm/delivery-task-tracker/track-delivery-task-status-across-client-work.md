# Track Delivery Task Status Across Client Work

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Track Delivery Task Status Across Client Work |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Gives ops and delivery teams a single view of all tasks linked to client deliverables, so they can monitor workload, due dates, assignees, and completion status without switching between client accounts. |
| **Entry Point / Surface** | Sleek Admin App > Delivery > Task Tracker |
| **Short Description** | Paginated table (100 rows/page) listing every task across all client deliverables. Ops users can create new tasks linked to a deliverable and template, and reassign (or unassign) any task to a different team member in-line. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Deliverables (getAllDeliverables), Task Templates (getAllTaskTemplates), Users (getAllUsers), Company via `deliverable.subscription.company`; upstream: subscription and company onboarding flows |
| **Service / Repository** | sleek-billings-frontend, service-delivery-api (VITE_SERVICE_DELIVERY_API_URL) |
| **DB - Collections** | Unknown — frontend only; backed by service-delivery-api which owns the persistence layer |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which markets/regions use this tracker? 2. What service-delivery-api backend repo owns the `/tasks` endpoints? 3. Is `createdBy` always hard-coded to `"admin"` or should it reflect the logged-in user? 4. No delete/complete action visible in the UI — is task completion driven elsewhere (e.g. automated or via another screen)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/Delivery/TaskTracker.jsx` — React component; renders the task list, create dialog, and reassign dialog
- `src/services/service-delivery-api.js` — Axios wrapper for the `VITE_SERVICE_DELIVERY_API_URL` backend

### API calls made by this feature
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/tasks?page=&limit=100` | List all tasks (paginated) |
| POST | `/tasks` | Create a new task |
| PATCH | `/tasks/:id` | Reassign task (sets `assignedUserId`) |
| GET | `/deliverables?limit=100` | Populate deliverable picker in create dialog |
| GET | `/task-templates?limit=100` | Populate template picker in create dialog |
| GET | `/users?limit=2000` | Populate assignee pickers |

### Task fields visible in the UI
`id`, `name`, `deliverable.subscription.company.name` (company), `assignedUser.email`, `status` (PENDING / IN_PROGRESS / COMPLETED / CANCELLED / FAILED / ACTIVE), `dueDate`, `completedDate`, `actualHours`, `deliverableId`, `createdAt`

### Auth surface
- `Authorization: Bearer <JWT>` (OAuth) or raw token fallback
- `App-Origin: admin` (alternate login) or `admin-sso`
- No role guards visible on the frontend; assumed gated by admin portal auth

### Status colour coding
| Status | Badge colour |
|---|---|
| COMPLETED, ACTIVE | Green |
| PENDING | Yellow |
| IN_PROGRESS | Blue |
| CANCELLED, FAILED | Red |
