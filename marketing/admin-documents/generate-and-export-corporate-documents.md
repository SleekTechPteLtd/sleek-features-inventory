# Generate and export corporate documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Generate and export corporate documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin operator (Sleek Admin session; same gate as other admin tools — unverified users redirected to `/verify/` via `getUser` in `documents.js`) |
| **Business Outcome** | Internal staff can merge a chosen template with live company and party data, review the result, and download a PDF for corporate communications without leaving the admin console. |
| **Entry Point / Surface** | Sleek Admin — **Document Templates** (`/admin/documents/`), **Generate Document** in the primary toolbar or **Generate** on a template row (`sidebarActiveMenuItemKey` `document-templates`; webpack entry `admin/documents` → `src/views/admin/documents.js`) |
| **Short Description** | Operators open the document generator, pick a template and (when required) a company via searchable admin company picker, complete binded fields (`companyId`, `directorId`, `shareholderId`, `companyStaffId`, `selectedDirectorIds`) and any custom variables defined on the template, set portrait or landscape, run **Preview Document** to merge via the API and show HTML in TinyMCE (unresolved `#{…}` tokens highlighted), then **Save as PDF** to download a kebab-cased filename via HTML-to-PDF. |
| **Variants / Markets** | Unknown — company and party fields are data-driven; no market gate in these views. |
| **Dependencies / Related Flows** | **Upstream:** Document templates and merge syntax are authored on the same page — see [Manage document templates](./manage-document-templates.md). **APIs:** `POST ${getBaseUrl()}/document-templates/:id/generate-doc-from-data` (`api.generateDocumentFromTemplate`, `admin: true`); `POST …/document-templates/convert-html-to-pdf` (`api.convertHtmlToPdf`). **Company context:** `GET …/companies/:id/company-users` via `getCompanyDirectors` / `getCompanyShareholders`; company search `api.getCompanies({ query: { name }, admin: true })` in binded-data. **Downstream:** merge resolution and PDF engine live in the backend behind those routes (not in sleek-website). |
| **Service / Repository** | **sleek-website:** `src/views/admin/documents.js`, `src/views/admin/documents/generate-document-form.js`, `src/views/admin/documents/generate-document-form-binded-data.js`, `src/views/admin/orientation.js`, `src/utils/api.js` |
| **DB - Collections** | Unknown — persistence for templates and generation is behind `/document-templates` (no Mongo schemas in this repo). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `generatePreview` is intended to send `documentOrientation` on every preview: `GenerateDocumentForm.launchGeneratePreview` calls `main.generatePreview` with three arguments while `generatePreview` accepts a fourth `documentOrientation` parameter (may be `undefined` in the JSON body). Exact production URL routing for `admin/documents` vs static `index.html` output. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/documents.js` (generator flow)

- **Enter generator:** `handleClickGenerateDocument` or `handleSelectAndClickGenerateDocument` sets `documentGeneratorVisible`, clears preview, optionally seeds `selectedTemplateId` and `documentOrientation` from the template.
- **Load template for generation:** `selectTemplateForGeneration` → `api.getDocumentTemplate(id, { admin: true })`; stores `templateVariables`, `templateCustomVariableConfigs`, `bindedData`, `orientation`.
- **Preview:** `generatePreview` → `api.generateDocumentFromTemplate` with body `{ bindedData, customFields, documentOrientation }`; applies red/yellow highlight spans to remaining `#{…}` matches in `htmlResult`.
- **PDF:** `handleClickSavePdf` → `api.convertHtmlToPdf` with `htmlToConvert` from preview state and `options: buildDocumentOrientation(htmlToConvert, orientation)`; blob download as `${kebabCase(templateName)}.pdf`.
- **Company-scoped lists:** `selectCompany` → `getCompanyDirectors` then `getCompanyShareholders` (both filter `GET …/companies/:id/company-users`).

### `src/views/admin/documents/generate-document-form.js`

- Toolbar template `<select>` calls `selectTemplateForGeneration`; form aggregates `getFormData()` → `bindedData` from child, `customVariables` from refs, `documentOrientation` from main state.
- **Preview Document** submit → `launchGeneratePreview` → `main.generatePreview(selectedTemplateId, bindedData, customVariables)`.
- Renders **Custom Variables** from `templateCustomVariableConfigs` (select, date via `DateInput`, textarea, text). **Save as PDF** shown when `documentPreviewContent` is non-empty.

### `src/views/admin/documents/generate-document-form-binded-data.js`

- **Company:** Blueprint `Select` with `fetchCompaniesList` → `api.getCompanies({ query: { name: selectCompanySearch }, admin: true })`; `handleSelectCompany` → `main.selectCompany(company._id)`.
- **`getBindedData()`** returns `companyId`, `shareholderId`, `directorId`, `selectedDirectorIds`, `companyStaffId` from refs/state.
- **`renderField`:** switches on `bindedData` keys from the template — director/shareholder/staff dropdowns; `selectedDirectorIds` uses `FormInput` `multipleselect` over directors.

### `src/views/admin/orientation.js`

- **`buildDocumentOrientation(docContent, documentOrientation)`** — A4, portrait or landscape, border insets (top border widened when `pageHeader` appears in HTML).

### `src/utils/api.js`

- `generateDocumentFromTemplate` → `POST ${getBaseUrl()}/document-templates/${documentTemplateId}/generate-doc-from-data`
- `convertHtmlToPdf` → `POST ${getBaseUrl()}/document-templates/convert-html-to-pdf`
