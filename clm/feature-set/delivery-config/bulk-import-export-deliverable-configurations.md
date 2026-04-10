# Bulk Import and Export Deliverable Configurations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Bulk Import and Export Deliverable Configurations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operations teams to make large-scale changes to delivery configuration at once by exporting the full deliverable template catalogue to CSV, editing offline, and importing back with a diff preview to review new, updated, and inactivated templates before committing. |
| **Entry Point / Surface** | Sleek Billings App > Delivery Configuration > Export CSV / Import CSV buttons |
| **Short Description** | Operations users export all deliverable templates as a CSV file, make bulk edits offline, then re-import the file. Before changes are applied, a modal diff preview categorises affected templates as New, Updated, or Inactive (with expandable task-level rows), and blocks commit when no changes are detected. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Delivery Configuration list (`DeliveryConfigList`); individual template editing (`DeliveryConfigForm`); task template detail (`TaskConfigForm`); subscription config codes lookup via `sleekBillingsApi.getAllSubscriptionConfig` (filtered to `clientType === "main"`); sleek-service-delivery backend API |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery-api |
| **DB - Collections** | `deliverable_templates`, `task_templates` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which markets use delivery configurations? Note: an earlier doc for the same capability exists at `clm/delivery-config-form/import-export-deliverable-templates-csv.md` — consider consolidating. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry file
`src/pages/DeliveryConfig/DeliveryConfigList.jsx`

### Key user interactions
| Action | Handler | API call |
|---|---|---|
| Export CSV | `handleClickExportCSV` | `POST /deliverable-templates/export-csv` → triggers browser download of `deliverable-templates.csv` |
| Select CSV for import | `handleGetCSVImportChanges` (hidden `<input type="file" accept=".csv">`) | `POST /deliverable-templates/import-csv/changes` (multipart/form-data) — returns diff |
| Preview diff dialog | `renderCsvImportChangesDialogContent` | Renders `newDeliverableTemplates`, `updatedDeliverableTemplates`, `inactiveDeliverableTemplates` with expandable task rows |
| Commit import | `handleImportCSV` ("Save Changes" button) | `POST /deliverable-templates/import-csv` (multipart/form-data) |
| Load current list | `fetchDeliverableTemplates` | `GET /deliverable-templates/deliverable-templates-list` |
| Resolve service code labels | `fetchSubscriptionConfig` | `sleekBillingsApi.getAllSubscriptionConfig()` filtered to `clientType === "main"` |

### Service layer (`src/services/service-delivery-api.js` — `sleekServiceDeliveryApi`)
- `getDeliverableTemplatesList()`
- `exportDeliverableTemplatesToCSV()`
- `importDeliverableTemplatesFromCSV(formData)`
- `getCSVImportChanges(formData)`

### Diff preview state shape
```
csvImportChanges: {
  newDeliverableTemplates[],
  updatedDeliverableTemplates[],
  inactiveDeliverableTemplates[]
}
```
- "Save Changes" disabled when all three arrays are empty (no-op guard)
- Dialog blocks backdrop-click dismissal to prevent accidental cancellation

### Deliverable template data model (from list columns)
- `id` — Deliverable ID
- `name` — Deliverable Name
- `record_status` — `ACTIVE` | `INACTIVE` | `DELETED`
- `taskTemplates[]` — nested task template list
- `codes[]` — applied Xero service codes

### Related files
- `src/pages/DeliveryConfig/DeliveryConfigForm.jsx` — individual template create/edit
- `src/pages/DeliveryConfig/TaskConfigForm.jsx` — task-level configuration
- `src/pages/DeliveryConfig/TaskTemplateList.jsx` — reused in preview rows to display task templates inline

---

### Backend — `sleek-service-delivery-api`

**Controller** `src/deliverable-templates/controllers/deliverable-templates.controller.ts`
- Auth: `@SleekBackAuth('admin')` on the whole controller — all endpoints require an admin back-channel token
- `POST /deliverable-templates/import-csv/changes` — multipart/form-data, returns `GetCsvImportChangesResponseDto` with three arrays: `newDeliverableTemplates`, `updatedDeliverableTemplates`, `inactiveDeliverableTemplates`
- `POST /deliverable-templates/import-csv` — multipart/form-data, applies the changes; returns `void`
- `POST /deliverable-templates/export-csv` — streams `deliverable-templates.csv` (`StreamableFile`, `text/csv`)

**Service** `src/deliverable-templates/services/deliverable-templates.service.ts`

`getCsvImportChanges(file)`:
1. Parses CSV via `csv-parse/sync` (columns by header name, trims whitespace)
2. Groups rows by `Deliverables` column (last-name carry-forward for multi-task rows)
3. Matches existing templates by `Deliverable Template ID`; classifies each as **new** (no DB match), **updated** (field diff detected), or **inactive** (present in DB but absent from CSV)
4. Change detection: `checkDeliverableTemplateChanges` compares `name` + `codes`; `checkTaskTemplatesChanges` compares `id`, `name`, `frequency`, `isProofOfCompletionRequired`, `isMilestone`, `roleAssigned`, `description`, `dueDateRule`, `dueDateRuleValues`, `autoMarkCondition`

`importCsv(file)`:
- Calls `getCsvImportChanges` then applies: upserts new/updated templates via `deliverableTemplateRepository.upsert(['id'])`; soft-deletes removed task templates (`recordStatus = DELETED`); upserts new task templates; marks absent deliverable templates `INACTIVE`
- `createdBy` stamped as `'CSV_IMPORT'`

`exportCsv()`:
- Fetches all `ACTIVE` deliverable templates with `taskTemplates` ordered by `createdAt ASC`
- Emits CSV with 13 columns: `Deliverables`, `Deliverable Template ID`, `Codes`, `Tasks`, `Task Template ID`, `Instances (Frequency)`, `Proof of completion`, `Milestone`, `Role assigned`, `Due date rule`, `Due date rule value`, `Task description`, `Auto-mark Condition`
- Multi-task deliverables → one row per task; `Deliverables`/`ID`/`Codes` cells blank on continuation rows
- `autoMarkCondition` serialised as JSON array per cell

**Validation** `validateBeforeImportCsv` (row-level, applied during diff computation):
- `Role assigned` must be a valid `RoleType` enum value
- `Instances (Frequency)` must be a valid `TaskFrequency` enum value
- `Auto-mark Condition` must be a valid JSON array; each rule validated for `rule` (`AutoMarkRuleType`), `trigger` (`AutoMarkTrigger`), `condition` (`AutoMarkCondition`), and `value` (context-dependent: `RoleType` for `COMPANY_HAS_ROLE`, `DuplicateTaskMatchBy` for `DUPLICATE_TASK_EXISTS`)

**DB tables** (TypeORM, PostgreSQL)
| Table | Entity | Key columns |
|---|---|---|
| `deliverable_templates` | `DeliverableTemplate` | `id` (uuid PK), `name`, `codes` (text[]), `recordStatus`, `createdAt` |
| `task_templates` | `TaskTemplate` | `id` (uuid PK), `deliverableTemplateId` (FK), `name`, `frequency`, `isProofOfCompletionRequired`, `isMilestone`, `roleAssigned`, `dueDateRule`, `dueDateRuleValues` (text[]), `autoMarkCondition` (jsonb), `recordStatus` |
