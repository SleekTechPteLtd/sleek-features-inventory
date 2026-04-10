# Manage Deliverable Templates

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage deliverable templates |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operators to define and maintain the task blueprints that govern service delivery for CLM clients — specifying what work is done, who does it, when it is due, and which subscription packages it applies to. |
| **Entry Point / Surface** | Sleek Billings App > Delivery Configuration (`/delivery-config`, `/delivery-config/edit/:id`) |
| **Short Description** | Operators browse, search, and inspect all deliverable templates along with their nested task structures (role assignments, due date rules, auto-mark conditions, proof requirements). Templates can be individually updated by name or bulk-managed via CSV import/export with a preview-diff step before changes are committed. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | sleek-service-delivery (backend API for deliverable and task templates); sleek-billings (subscription config — `getAllSubscriptionConfig` — to resolve and validate subscription codes applied to templates) |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery (backend, inferred) |
| **DB - Collections** | Unknown (frontend only; collections live in sleek-service-delivery backend) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. `ALLOW_EDITING = false` is hard-coded in `DeliveryConfigForm.jsx` — the form is currently read-only and changes must be requested via the Billing Support Slack channel. Is this a temporary freeze or the intended long-term UX? 2. Markets/jurisdictions are not differentiated in the UI — are deliverable templates global or per-market? 3. The `TaskConfigForm` "Done" button on edit mode does not appear to persist task-level changes back to the API — is task-level editing wired up or still in progress? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/DeliveryConfig/DeliveryConfigList.jsx` — list view; debounced search across template name, task names, and applied codes; expandable rows showing nested task list and applied subscription codes; Export CSV and Import CSV (with preview-diff dialog)
- `src/pages/DeliveryConfig/DeliveryConfigForm.jsx` — detail/edit view for a single deliverable template; fields: Deliverable Name, Deliverable ID (read-only), Status; shows nested `TaskTemplateList` and an Autocomplete of applied subscription codes (resolved against `sleekBillingsApi.getAllSubscriptionConfig`)
- `src/pages/DeliveryConfig/TaskTemplateList.jsx` — table of task templates with columns: Order, Task Name, Frequency, Assigned Role, Due Date Rule, Additional Settings (description, proof required, milestone, auto-mark badges); opens `TaskConfigForm` in a right-side Drawer on "View details"
- `src/pages/DeliveryConfig/TaskConfigForm.jsx` — read/edit form for a single task template; fields: Task Name, Frequency, Assigned Role (PORTFOLIO_LEAD, ACCOUNT_MANAGER, BOOKKEEPER, CORPORATE_SECRETARY, PAYROLL_EXECUTIVE, TAX_EXECUTIVE), Due Date Rule, Description, Proof of Completion toggle, Milestone toggle, Auto Mark Condition rules (grouped by trigger)

### API calls (via `sleekServiceDeliveryApi`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/deliverable-templates/deliverable-templates-list` | Load all templates for list view |
| GET | `/deliverable-templates/:id` | Load single template for detail view |
| PATCH | `/deliverable-templates/:id` | Update deliverable template name |
| POST | `/deliverable-templates/export-csv` | Export all templates to CSV download |
| POST | `/deliverable-templates/import-csv/changes` | Preview diff of a CSV import (new / updated / inactive) |
| POST | `/deliverable-templates/import-csv` | Commit CSV import |

### Cross-service calls
- `sleekBillingsApi.getAllSubscriptionConfig()` — fetches subscription config records (filtered to `clientType === "main"`) to map subscription codes to human-readable names; invalid codes are highlighted in red

### Key data shape
- Deliverable template: `{ id, name, record_status (ACTIVE | INACTIVE | DELETED), taskTemplates[], codes[] }`
- Task template: `{ id, name, frequency, roleAssigned, dueDateRule, description, isProofOfCompletionRequired, isMilestone, autoMarkCondition[] }`
- CSV import diff: `{ newDeliverableTemplates[], updatedDeliverableTemplates[], inactiveDeliverableTemplates[] }`

### Notable constraints
- `ALLOW_EDITING = false` is hard-coded in `DeliveryConfigForm.jsx:21` — the UI shows a read-only banner directing operators to Billing Support Slack for edits
- Drag-and-drop reordering of tasks is rendered in edit mode but not wired to an API call
- Task-level editing in `TaskConfigForm` has an Edit/Done toggle but no save API call is visible in the frontend code
