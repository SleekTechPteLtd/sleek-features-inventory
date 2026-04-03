# Create client request instances from templates

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Create client request instances from templates |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Staff can open a new client servicing request from a standard or automated template, capture the data the template needs, place the output in the right company folder, and hand off a persisted request instance for downstream processing. |
| **Entry Point / Surface** | Sleek Admin > Requests > **New Request** (`NewRequestView`, `sidebarActiveMenuItemKey="requests"`; back link to `/admin/requests/`) |
| **Short Description** | Admin picks a manual or automated request template (grouped in the UI), selects a client company (searchable), and—once both are set—enters a generated or edited document name, chooses a company folder under the Secretary tree (with optional default from platform config), fills template variables and additional fields (text, number, date, or file), optionally checks **Use custom document** and uploads a client-provided file, then submits. Files upload to the company root via the files service; creation is `POST /companies/:companyId/request-instances`. |
| **Variants / Markets** | Unknown (tenant may shape `platformConfig` defaults such as `incorp_transfer_workflow` / `pre_incorp_document_data` folder mapping; not fixed to SG/HK/AU in this view) |
| **Dependencies / Related Flows** | Request templates (`GET /request-templates`, `GET /request-templates/:id`); company search (`GET /companies` with `admin: true`); folder listing (`GET` files API, recursive folders under `/companies/:id/Secretary/`); document name suggestion (`POST /admin/request-instances/generate-document-name` when `admin: true`); file upload (`POST` to files base URL via `viewUtil.uploadFile`); success redirects to `/admin/requests/`. Backend persists request instances and document generation—out of repo. |
| **Service / Repository** | `sleek-website`: `src/views/admin/requests/new.js`, `src/utils/api.js` (`getRequestTemplates`, `getRequestTemplate`, `getCompanies`, `getFiles`, `generateDocumentName`, `createRequestInstance`, `getFileBaseUrl`). Main API and Files microservice (config-driven base URLs). |
| **DB - Collections** | Unknown (request instances, templates, companies, files metadata handled by APIs not in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact auth rules on `POST /companies/:companyId/request-instances` vs admin-only routes; backend validation for template/company pairing; whether `[AUTOMATED]` naming convention is documented for template authors. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/requests/new.js`

- **Layout:** `AdminLayout` with `sidebarActiveMenuItemKey="requests"`, primary toolbar back to `/admin/requests/` (lines 72–98).
- **Templates:** `fetchRequestTemplates` → `api.getRequestTemplates()`; split into `manualRequestTemplates` vs `automatedRequestTemplates` by first word `[AUTOMATED]` in template name (lines 684–689). `onTemplateSelectChange` → `fetchSelectedRequestTemplate` → `api.getRequestTemplate(id)` (lines 652–655, 692–694).
- **Company:** `getCompanies` with `query: { name }`, `admin: true` (lines 354–366). Selection triggers `generateDocumentName` and `fetchFolderByCompanyList` (lines 344–351).
- **Document name:** `api.generateDocumentName({ admin: true, body: JSON.stringify({ companyName, requestTemplateName, requestTemplateId }) })`; name can follow CMS `customRequestTemplateName` for specific template IDs (`getAppFeatureProp` chain) (lines 242–268).
- **Folders:** `getFiles` in a loop with `type: folder`, `is_recursive: true`, `local_path: /companies/${selectedCompanyId}/Secretary/` (lines 369–392). `renderCompanyFoldersSelect` maps options and can auto-select folder from `platformConfig.cmsAppFeatures.incorp_transfer_workflow.props.pre_incorp_document_data` (lines 307–336).
- **Form:** Renders `document_template.customVariableNames` as text inputs; `additional_fields` by type (string/number, date `DateInput`, file); optional `use_custom_document` and `client_provided_document` (lines 395–511).
- **Submit:** `handleFormSubmit` requires `selectedFolderId`; uploads file inputs via `uploadFile` → `viewUtil.uploadFile(file, companyRootFolderId, { maxMb: 5 })` (lines 552–639). Payload: `request_template_id`, `document_fields`, `additional_fields`, `client_provided_document`, `document_name`, `selected_folder_id` via `api.createRequestInstance(selectedCompanyId, { body: JSON.stringify(...) })` (lines 607–615). Success message then navigates to `/admin/requests/` (lines 616–626).
- **Query:** Optional `?cid=` stores `company_id` in `store` (lines 55–68).

### `src/utils/api.js`

- **`createRequestInstance`:** `POST ${getBaseUrl()}/companies/${companyId}/request-instances` (lines 620–623).
- **`generateDocumentName`:** `POST ${getBaseUrl()}/request-instances/generate-document-name` via `postResource` (admin prefix when `options.admin === true`) (lines 1215–1217).
- **`getRequestTemplates`:** `GET ${getBaseUrl()}/request-templates` (lines 1150–1153).
- **`getRequestTemplate`:** `GET ${getBaseUrl()}/request-templates/${requestTemplateId}` (lines 1155–1158).
- **`getCompanies`:** `GET ${getBaseUrl()}/companies` with query (lines 377–383).
- **`getFiles`:** `GET` against file service base from `getFileBaseUrl()` (lines 926–928).
- **`getFileBaseUrl`:** Resolves Files microservice vs main API from platform config and env (lines 56–84). Exported for download links in file lists (used in `renderFormFileList`, lines 514–536 in `new.js`).
