# Manage document templates

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage document templates |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin operator (Sleek Admin session; unverified users redirected to `/verify/`) |
| **Business Outcome** | Lets internal operators maintain reusable HTML document templates and generate or export PDFs populated with company, shareholder, director, and staff data using a documented merge-field syntax, so client-facing paperwork stays consistent and can be produced on demand. |
| **Entry Point / Surface** | Sleek Admin — **Document Templates** (`sidebarActiveMenuItemKey` `document-templates`; webpack entry `admin/documents` → `src/views/admin/documents.js`) |
| **Short Description** | Admins list document templates (name, created date), create new templates in TinyMCE with portrait or landscape orientation, edit HTML content, and delete templates with confirmation. The editor sidebar documents merge syntax for `company.*`, `shareholder.*` (including indiv/corp/resolved variants), `director.*`, `company_staff.*`, list blocks (`START shareholders` / `START directors`), conditionals, headers/footers, page breaks, and custom fields. **Generate Document** selects a template and company, loads directors/shareholders for binding, supports custom variable forms, previews merged HTML via the API (with unresolved merge tokens highlighted), and can save the preview as PDF through HTML-to-PDF conversion. |
| **Variants / Markets** | Unknown (registration-number label comes from CMS `company_meta` via `getAppFeatureProp`; not hard-coded per market in this UI) |
| **Dependencies / Related Flows** | **Upstream:** `getPlatformConfig` / `getAppFeatureProp` for `company_meta` labels in the helper; `api.getUser` for session. **Template CRUD & generation:** REST under `${getBaseUrl()}/document-templates` (`GET` list, `POST` create, `GET`/`PUT`/`DELETE` by id, `POST …/generate-doc-from-data`, `POST …/convert-html-to-pdf`) with `{ admin: true }` on requests. **Company data for generation:** `api.getCompanyDirectors`, `api.getCompanyShareholders` when a company is selected. **Downstream:** merge resolution, persistence, and PDF rendering are implemented in the API service backing those routes (not in this repo). |
| **Service / Repository** | `sleek-website` — `src/views/admin/documents.js`, `src/views/admin/documents/generate-document-form.js`, `src/views/admin/documents/generate-document-form-binded-data.js` (referenced), `src/views/admin/orientation.js`, `src/utils/api.js` |
| **DB - Collections** | Unknown (templates and generation persist in the service behind `/document-templates`; no Mongo schemas in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact public URL path for the admin page depends on deployed routing (webpack outputs `admin/documents/index.html`; path not verified in-repo). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/documents.js`

- **Layout:** `AdminLayout` with `hideDrawer`, `sidebarActiveMenuItemKey="document-templates"`.
- **Template list:** `getTemplates` → `api.getDocumentTemplates({ admin: true })`; table with Generate / Edit / Delete per row.
- **Create / update:** `handleClickSaveTemplate` → `api.createDocumentTemplate` or `api.updateDocumentTemplate` with JSON body `{ name, content, orientation }` (`orientation` from `DOCUMENT_ORIENTATIONS` / portrait–landscape select).
- **Delete:** confirmation dialog → `api.deleteDocumentTemplate(id, { admin: true })`.
- **Editor:** TinyMCE config (plugins, fonts, pagebreak); `renderEditorHelper()` lists merge-field syntax for company, shareholder, director, company_staff, lists, conditionals, header/footer, `PAGE_BREAK`, and custom field types (`select`, `date`, `textarea`).
- **Generation:** `selectTemplateForGeneration` → `api.getDocumentTemplate` (loads `customVariableNames`, `customVariableConfigs`, `bindedData`, `orientation`); `generatePreview` / `generateDocumentFromTemplate` → `api.generateDocumentFromTemplate` → `POST …/document-templates/:id/generate-doc-from-data`; preview highlights remaining `#{…}` tokens in red/yellow.
- **PDF:** `handleClickSavePdf` → `api.convertHtmlToPdf` with `htmlToConvert` and `buildDocumentOrientation` from `orientation.js` (A4, portrait/landscape borders).
- **Company binding:** `selectCompany` → `api.getCompanyDirectors` then `api.getCompanyShareholders` (sorted by `createdAt`).

### `src/views/admin/documents/generate-document-form.js`

- Template dropdown, orientation control, **Generate Preview** calling `main.generatePreview` with binded data and custom variables; dynamic inputs for custom variables from `templateCustomVariableConfigs` (select, date, textarea, text).

### `src/views/admin/orientation.js`

- `buildDocumentOrientation(html, documentOrientation)` returns PDF options (`format: A4`, orientation, borders) for `convertHtmlToPdf`.

### `src/utils/api.js`

- `getDocumentTemplates` → `GET ${getBaseUrl()}/document-templates`
- `createDocumentTemplate` → `POST …/document-templates`
- `getDocumentTemplate` / `updateDocumentTemplate` / `deleteDocumentTemplate` → `GET`/`PUT`/`DELETE …/document-templates/:id`
- `generateDocumentFromTemplate` → `POST …/document-templates/:id/generate-doc-from-data`
- `convertHtmlToPdf` → `POST …/document-templates/convert-html-to-pdf`
