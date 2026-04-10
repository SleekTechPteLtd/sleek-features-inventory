# Bulk Assign Team Members Across Companies

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Bulk assign team members across companies |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Delivery Operator (internal admin) |
| **Business Outcome** | Lets delivery operators reassign a team member to a role across many companies at once, eliminating per-company manual updates when headcount changes or roles are reallocated. |
| **Entry Point / Surface** | Sleek Admin > Delivery > Team Assignments — context-menu "View all assigned / unassigned companies" → "Bulk update assignment" |
| **Short Description** | Operator views all companies where a given role is assigned to (or missing) a specific person, selects any subset or "select all matching" across all pages, chooses a new assignee, and submits one API call to reassign that role across the entire selection. After saving, task assignees and auto-mark Done rules are updated asynchronously via queue jobs. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Auto-assignment rules (per-role defaults); single-company assignment dialog (same page); auto-mark Done evaluation on role assignment; task bulk-update queue; retrieve-from-admin-app assignment sync |
| **Service / Repository** | sleek-billings-frontend; sleek-service-delivery-api |
| **DB - Collections** | team_assignments (upsert), companies (read/filter), users (validate), tasks (updated via queue), task_activities (auto-mark audit logs) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which markets/jurisdictions this operator tool covers is not indicated in the code. 2. Is there a UI-level audit trail for bulk operations beyond the auto-mark task_activities entries? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files (frontend — sleek-billings-frontend)
- `src/pages/Delivery/TeamAssignments.jsx` — main page component
- `src/services/service-delivery-api.js` — HTTP client wrapper

### Files (backend — sleek-service-delivery-api)
- `src/team-assignments/controllers/team-assignments.controller.ts` — REST controller
- `src/team-assignments/services/team-assignments.service.ts` — core business logic
- `src/team-assignments/dto/bulk-update-team-assignment-item.dto.ts` — request shape
- `src/team-assignments/dto/bulk-update-filters.dto.ts` — filter options
- `src/team-assignments/entities/team-assignment.entity.ts` — DB entity (`team_assignments` table)

### Auth surface
`@SleekBackAuth('admin')` guard on the entire `TeamAssignmentsController` — only internal admin users can call these endpoints.

### API endpoint
```
POST /team-assignments/bulk-update
```
Body: `{ roleType, assignedUserId, updatedBy, companyIds?, all?, excludedFromAllSelection?, filters? }`

Returns `{ succeeded: TeamAssignment[], failed: { companyId, message }[] }` — partial success is possible.

### Targeting modes
- **Explicit list**: `companyIds[]` — operator-selected rows
- **"Select all matching"**: `all: true` + optional `excludedFromAllSelection[]` — backend resolves IDs server-side using filter query

### Filters (applied when `all: true`)
- `assignedRoles` — companies that have these role types assigned
- `filterByUnassignedRoles` — companies missing an assignment for these role types
- `filterByUsers` — companies where specific users are currently assigned
- `filterByCompanyStatuses` — filter by company status enum

### DB write pattern (service.bulkUpdate)
1. Validate user (single query), validate companies (single query)
2. Load existing `(companyId, roleType)` assignments in one query
3. Upsert in batches of 3000 rows: bulk UPDATE existing rows via `whereInIds`, bulk INSERT new rows via query builder with `RETURNING id`
4. Return succeeded assignments with `company` and `assignedUser` relations loaded

### Async side effects (post-save)
- Companies batched into chunks of 500; per chunk:
  - `UpdateTasksBulkQueueService.addUpdateTasksBulkJob` — propagates new assignee to all tasks for that role/company
  - `AutoMarkForCompaniesQueueService.addAutoMarkForCompaniesJob` — evaluates auto-mark Done rules triggered by the role assignment
- Auto-mark evaluation writes `task_activities` rows (type `STATUS_CHANGE`) with `autoMarkReason` and audit content when tasks are auto-closed

### DB table
`team_assignments` — unique index on `(companyId, roleType)`, FK to `companies` (CASCADE) and `users` (SET NULL)

### Supported roles
Categories visible in UI: General (Team Lead, Support IC, CSS IC), Accounting (Onboarding IC, Manager, Accountant IC, Reviewer, Bookkeeper, Remediation Accountant), Audit (Onboarding IC, Manager, IC, Reviewer), Tax (IC, Manager, Reviewer, GST IC), Corporate Secretary IC.

### Bulk mode state (TeamAssignments.jsx:142–156)
```js
const [bulkMode, setBulkMode] = useState({
  active: false,
  type: "",          // "assigned" | "unassigned"
  role: "",          // ROLE_TYPES value
  currentAssignee: null,
  selectionMode: false,
});
const [bulkSelection, setBulkSelection] = useState(new Set());
const [hasSelectedAllMatching, setHasSelectedAllMatching] = useState(false);
const [excludedFromAllSelection, setExcludedFromAllSelection] = useState(new Set());
const [bulkSelectedUser, setBulkSelectedUser] = useState(null);
const [bulkSubmitting, setBulkSubmitting] = useState(false);
```

### UI flow
1. Operator right-clicks a role cell → context menu → "View all assigned companies for [user]" or "View all unassigned companies for [role]"
2. Page re-filters to show only matching companies; a blue banner describes the active bulk context.
3. Operator clicks "Bulk update assignment" → selection checkboxes appear on each row.
4. Operator selects rows individually, selects all on page, or clicks "Select all [N] matching" banner.
5. Operator picks a new assignee from the `AssigneeSelect` dropdown.
6. Submit → `POST /team-assignments/bulk-update` → success snackbar → list refreshes, selection resets.
