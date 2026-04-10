# Configure Deliverable Templates

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Configure deliverable templates |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (via admin API; surface is sleek-billings frontend) |
| **Business Outcome** | Enables operators to define reusable delivery blueprints — each pairing a named deliverable with a set of task templates and subscription codes — so that the correct service tasks are automatically provisioned when a client subscription is activated. |
| **Entry Point / Surface** | Backend REST API (`/deliverable-templates`); consumed by Sleek Billings App > Delivery Configuration |
| **Short Description** | Provides full CRUD for deliverable templates and their nested task templates, including a bulk CSV import/export workflow with a preview-diff step. Templates carry `codes[]` that map them to subscription packages; the import pipeline validates role types, task frequencies, and auto-mark condition rules before upserting or deactivating records. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | sleek-billings-frontend (`delivery-config-form` module) — UI that calls these endpoints; sleek-billings subscription config API — resolves subscription codes to human-readable names; task-templates module (nested within deliverable templates); deliverables module (instances provisioned from templates) |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | `deliverable_templates`, `task_templates` (PostgreSQL via TypeORM) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. The `CreateDeliverableTemplateDto` still contains a singular `code: string` field while the entity stores `codes: string[]` — is the DTO stale or is single-code creation still supported via a separate path? 2. Markets/jurisdictions are not differentiated in templates or codes — are templates global or per-market? 3. `remove()` hard-deletes the record; is soft-delete via `recordStatus = DELETED` used elsewhere in this module for consistency? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Auth surface
- `@SleekBackAuth('admin')` applied at controller class level — all endpoints require admin-level service authentication.

### Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/deliverable-templates` | Create a single deliverable template |
| GET | `/deliverable-templates` | Paginated list (with `taskTemplates` and `deliverables` relations) |
| GET | `/deliverable-templates/deliverable-templates-list` | Full unpaginated list excluding DELETED records, with active task templates |
| GET | `/deliverable-templates/:id` | Fetch one template with its non-deleted task templates |
| PATCH | `/deliverable-templates/:id` | Update name, description, or codes |
| DELETE | `/deliverable-templates/:id` | Hard-delete a template |
| POST | `/deliverable-templates/import-csv/changes` | Parse uploaded CSV, compute new/updated/inactive diff without persisting |
| POST | `/deliverable-templates/import-csv` | Commit CSV import: upsert templates + task templates, deactivate omitted templates |
| POST | `/deliverable-templates/export-csv` | Stream all ACTIVE templates + tasks as a CSV download |

### Entity: `deliverable_templates`
- `name: varchar(255)` — deliverable name (e.g. "Annual Filing")
- `description: text` — optional description
- `codes: text[]` — subscription codes that activate this template
- Relations: `taskTemplates` (OneToMany `→ task_templates`), `deliverables` (OneToMany `→ deliverables`)
- Inherits `id`, `createdAt`, `updatedAt`, `recordStatus` from `SleekBase`

### Entity: `task_templates`
Key fields populated via CSV import:
- `name`, `description`, `frequency` (`TaskFrequency` enum: One-time / Weekly / Bi-weekly / Monthly / Quarterly)
- `roleAssigned` (`RoleType` enum)
- `dueDateRule` (`TaskDueDateRule` enum — e.g. `Subscription Start Date + {DURATION}`, `FYE + {DURATION}`, `{DAY} day of the following month`, plus UK-specific CIS/VAT/Companies House rules)
- `dueDateRuleValues: string[]`
- `isProofOfCompletionRequired: boolean`, `isMilestone: boolean`
- `autoMarkCondition: AutoMarkRuleDto[]` — JSON array of auto-mark rules with `rule` (AutoMarkRuleType), `trigger` (AutoMarkTrigger), `condition` (AutoMarkCondition), `value`

### CSV import pipeline (`importCsv` / `getCsvImportChanges`)
- Columns: `Deliverables`, `Deliverable Template ID`, `Codes`, `Tasks`, `Task Template ID`, `Instances (Frequency)`, `Proof of completion`, `Milestone`, `Role assigned`, `Due date rule`, `Due date rule value`, `Task description`, `Auto-mark Condition`
- Validation: RoleType, TaskFrequency, AutoMarkRuleType, AutoMarkTrigger, AutoMarkCondition, DuplicateTaskMatchBy — all checked before upsert
- Upserts use `id` as the conflict key; task templates not present in the CSV are soft-deleted (`recordStatus = DELETED`); deliverable templates not referenced in the CSV are set to `INACTIVE`
- `createdBy` is set to `'CSV_IMPORT'` on all upserted records

### Files
- `deliverable-templates/controllers/deliverable-templates.controller.ts` — route definitions, auth decorator, file-upload interceptors
- `deliverable-templates/services/deliverable-templates.service.ts` — business logic, CSV parse/validate/upsert, export streaming
- `deliverable-templates/entities/deliverable-template.entity.ts` — `deliverable_templates` table schema
- `deliverable-templates/dto/create-deliverable-template.dto.ts` — create payload (note: singular `code` field vs entity's `codes[]`)

### Related feature file
- `manage-deliverable-templates.md` — frontend (sleek-billings) perspective covering the same capability; documents UI flows, search, and the `ALLOW_EDITING = false` freeze.
