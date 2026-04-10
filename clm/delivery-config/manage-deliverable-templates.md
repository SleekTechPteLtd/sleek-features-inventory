# Manage Deliverable Templates

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage deliverable templates |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operators to define and maintain the task blueprints that govern service delivery for CLM clients — specifying what work is done, who does it, when it is due, and which subscription packages it applies to. |
| **Entry Point / Surface** | Sleek Billings App > Delivery Config (nav rail, icon "settings") → `/delivery-config`, `/delivery-config/edit/:id` |
| **Short Description** | Operators browse, search, and inspect all deliverable templates along with their nested task structures (role assignments, due date rules, auto-mark conditions, proof requirements) and applied subscription codes. Templates are currently read-only in the UI; bulk management is available via CSV import/export with a preview-diff step before committing changes. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | sleek-service-delivery (backend API for deliverable and task templates); sleek-billings (`getAllSubscriptionConfig` — resolves subscription codes applied to templates) |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery-api |
| **DB - Collections** | `deliverable_templates`, `task_templates` (PostgreSQL via TypeORM) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. `ALLOW_EDITING = false` is hard-coded in `DeliveryConfigForm.jsx:21` — the form is read-only and operators must request edits via the Billing Support Slack channel. Is this a temporary freeze or the intended long-term UX? 2. No market/jurisdiction differentiation visible — are templates global or per-market? 3. Task-level editing in `TaskConfigForm` has an Edit/Done toggle but no save API call is visible in the frontend code — is this wired up or still in progress? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/DeliveryConfig/DeliveryConfigList.jsx` — list view; debounced search across template name, task names, and applied codes; expandable rows showing nested task list and applied subscription codes; Export CSV and Import CSV (with preview-diff dialog showing new / updated / inactive counts before commit)
- `src/pages/DeliveryConfig/DeliveryConfigForm.jsx` — detail view for a single deliverable template; fields: Deliverable Name, Deliverable ID (always read-only), Status; shows nested `TaskTemplateList` and an Autocomplete of applied subscription codes resolved via `sleekBillingsApi.getAllSubscriptionConfig`; `ALLOW_EDITING = false` hard-coded, rendering a read-only info banner
- `src/pages/DeliveryConfig/TaskTemplateList.jsx` — table of task templates with columns: Order, Task Name, Frequency, Assigned Role, Due Date Rule, Additional Settings (description, proof required, milestone, auto-mark badges); opens `TaskConfigForm` in a right-side Drawer on "View details"
- `src/pages/DeliveryConfig/TaskConfigForm.jsx` — read/edit form for a single task template; fields: Task Name, Frequency, Assigned Role, Due Date Rule, Description, Proof of Completion toggle, Milestone toggle, Auto Mark Condition rules (grouped by trigger)

### API calls (via `sleekServiceDeliveryApi`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/deliverable-templates/deliverable-templates-list` | Load all templates for list view |
| GET | `/deliverable-templates/:id` | Load single template for detail view |
| PATCH | `/deliverable-templates/:id` | Update deliverable template name (disabled in UI) |
| POST | `/deliverable-templates/export-csv` | Export all templates to CSV download |
| POST | `/deliverable-templates/import-csv/changes` | Preview diff of a CSV import (new / updated / inactive) |
| POST | `/deliverable-templates/import-csv` | Commit CSV import |

### Cross-service calls
- `sleekBillingsApi.getAllSubscriptionConfig()` — fetches subscription config records (filtered to `clientType === "main"`) to map subscription codes to human-readable service names; invalid codes highlighted in red in both list and detail views

### Key data shape
- Deliverable template: `{ id, name, record_status (ACTIVE | INACTIVE | DELETED), taskTemplates[], codes[] }`
- Task template: `{ id, name, frequency, roleAssigned, dueDateRule, description, isProofOfCompletionRequired, isMilestone, autoMarkCondition[] }`
- Role options: `PORTFOLIO_LEAD`, `ACCOUNT_MANAGER`, `BOOKKEEPER`, `CORPORATE_SECRETARY`, `PAYROLL_EXECUTIVE`, `TAX_EXECUTIVE`
- CSV import diff shape: `{ newDeliverableTemplates[], updatedDeliverableTemplates[], inactiveDeliverableTemplates[] }`

### Notable constraints
- `ALLOW_EDITING = false` is hard-coded at `DeliveryConfigForm.jsx:21` — the UI shows a read-only info banner ("To make edits, submit a request via the Billing Support Slack channel")
- Drag-and-drop reordering of tasks is rendered in edit mode (`DragIndicator` icon) but not wired to an API call
- Task-level editing in `TaskConfigForm` has an Edit/Done toggle but no save API call is visible in the frontend code

---

## Backend evidence (`sleek-service-delivery-api`)

### Auth surface
- `@SleekBackAuth('admin')` applied at controller class level — all endpoints are internal/admin-only; no end-user JWT auth visible.

### Controller endpoints
`src/deliverable-templates/controllers/deliverable-templates.controller.ts`

| Method | Route | Purpose |
|---|---|---|
| POST | `/deliverable-templates` | Create a deliverable template |
| GET | `/deliverable-templates` | List all templates (paginated) |
| GET | `/deliverable-templates/deliverable-templates-list` | Full list with task templates (used by frontend) |
| GET | `/deliverable-templates/:id` | Get single template with task templates |
| PATCH | `/deliverable-templates/:id` | Update a deliverable template |
| DELETE | `/deliverable-templates/:id` | Hard-delete a template |
| POST | `/deliverable-templates/import-csv/changes` | Preview CSV diff (multipart upload) |
| POST | `/deliverable-templates/import-csv` | Commit CSV import |
| POST | `/deliverable-templates/export-csv` | Export all active templates as CSV download |

### Database tables
`src/deliverable-templates/entities/deliverable-template.entity.ts`

**`deliverable_templates`** — one row per template
- `id` (UUID, PK), `name` (varchar 255), `description` (text, nullable)
- `codes` (text[], nullable) — subscription service codes applied to this template
- `recordStatus` (ACTIVE | INACTIVE | DELETED) — soft-delete via base entity

**`task_templates`** — one row per task within a template
- `id` (UUID, PK), `name`, `description`, `deliverableTemplateId` (FK)
- `frequency` (enum: One-time | Weekly | Bi-weekly | Monthly | Quarterly)
- `roleAssigned` (enum: RoleType — PORTFOLIO_LEAD, ACCOUNT_MANAGER, BOOKKEEPER, etc.)
- `isProofOfCompletionRequired` (bool), `isMilestone` (bool)
- `dueDateRule` (varchar) — one of 12 rule patterns (e.g. `Subscription Start Date + {DURATION}`, `FYE + {DURATION}`, `Last day of the following month`)
- `dueDateRuleValues` (text[]) — rule parameter values
- `autoMarkCondition` (jsonb) — array of `AutoMarkRuleDto` objects; each rule has `rule` (AutoMarkRuleType), `trigger` (AutoMarkTrigger), `condition` (AutoMarkCondition), and `value`

### CSV import logic
`src/deliverable-templates/services/deliverable-templates.service.ts`

- **Preview diff** (`getCsvImportChanges`): parses CSV, groups rows by deliverable name, compares `name`/`codes` and task fields against existing DB records; returns `{ newDeliverableTemplates[], updatedDeliverableTemplates[], inactiveDeliverableTemplates[] }`. Templates absent from the CSV but active in DB are flagged as inactive.
- **Commit** (`importCsv`): upserts new/updated templates and task templates by UUID; soft-deletes tasks no longer in the CSV (`recordStatus = DELETED`); deactivates deliverable templates absent from the CSV (`recordStatus = INACTIVE`). `createdBy` is stamped as `'CSV_IMPORT'`.
- **Validation** (`validateBeforeImportCsv`): enforces valid `RoleType`, `TaskFrequency`, and `AutoMarkRuleDto` shape (including `AutoMarkRuleType`, `AutoMarkTrigger`, `AutoMarkCondition`, `DuplicateTaskMatchBy` enums) per CSV row.
- **Export** (`exportCsv`): streams all ACTIVE templates as `deliverable-templates.csv`; columns include Deliverable Template ID, Task Template ID, Codes, Instances (Frequency), Proof of completion (Y/N), Milestone (Y/N), Role assigned, Due date rule, Due date rule value, Task description, Auto-mark Condition (JSON).

### External service calls
None — no Kafka, Redis, Xero, or other external integrations in this module.
