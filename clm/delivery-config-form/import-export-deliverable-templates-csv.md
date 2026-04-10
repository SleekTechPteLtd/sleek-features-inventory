# Import and Export Deliverable Templates via CSV

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Import and Export Deliverable Templates via CSV |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operators to bulk-manage delivery configurations at scale by importing and exporting deliverable templates as CSV files, with a diff preview before committing changes. |
| **Entry Point / Surface** | Sleek Billings App > Delivery Configuration > Export CSV / Import CSV buttons |
| **Short Description** | Operators export the current set of deliverable templates as a CSV file, edit it offline, then re-import it. Before committing, a preview dialog shows exactly how many templates will be new, updated, or inactivated, with expandable rows to inspect task changes. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Delivery Configuration list (DeliveryConfigList); Task template detail (DeliveryConfigForm / TaskConfigForm); Subscription config codes lookup (sleek-billings-api `getAllSubscriptionConfig`); sleek-service-delivery backend API |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery (backend, inferred) |
| **DB - Collections** | Unknown (frontend only; deliverable template data stored in sleek-service-delivery backend) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which markets use delivery configurations? What is the CSV schema (column names, required fields)? Is there validation server-side beyond the diff preview? Who owns the sleek-service-delivery backend? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry file
`src/pages/DeliveryConfig/DeliveryConfigList.jsx`

### Key interactions
| Action | Handler | API call |
|---|---|---|
| Export CSV | `handleClickExportCSV` | `POST /deliverable-templates/export-csv` → triggers browser download of `deliverable-templates.csv` |
| Select CSV file for import | `handleGetCSVImportChanges` (via hidden `<input type="file">`) | `POST /deliverable-templates/import-csv/changes` (multipart/form-data) |
| Preview diff dialog | `renderCsvImportChangesDialogContent` | Renders `newDeliverableTemplates`, `updatedDeliverableTemplates`, `inactiveDeliverableTemplates` counts + expandable rows |
| Commit import | `handleImportCSV` (Save Changes button) | `POST /deliverable-templates/import-csv` (multipart/form-data) |
| Load current list | `fetchDeliverableTemplates` | `GET /deliverable-templates/deliverable-templates-list` |
| Resolve service code labels | `fetchSubscriptionConfig` | `sleekBillingsApi.getAllSubscriptionConfig()` filtered to `clientType === "main"` |

### Service layer
`src/services/service-delivery-api.js` — `sleekServiceDeliveryApi` object:
- `getDeliverableTemplatesList()`
- `exportDeliverableTemplatesToCSV()`
- `importDeliverableTemplatesFromCSV(formData)`
- `getCSVImportChanges(formData)`

### Preview dialog state
- `csvImportChanges` — `{ newDeliverableTemplates[], updatedDeliverableTemplates[], inactiveDeliverableTemplates[] }`
- Save Changes is disabled when all three arrays are empty (no-op import guard)
- Dialog blocks backdrop-click dismissal to prevent accidental cancellation

### Related pages
- `src/pages/DeliveryConfig/DeliveryConfigForm.jsx` — individual template edit
- `src/pages/DeliveryConfig/TaskConfigForm.jsx` — task-level configuration
- `src/pages/DeliveryConfig/TaskTemplateList.jsx` — reused in preview rows to display task templates
