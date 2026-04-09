# Manage document templates

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage document templates |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (admin API with `document_templates` permission: `full` for create/update/delete and PDF conversion inputs, `read` for list/get/preview generation) |
| **Business Outcome** | Standardized HTML templates (including page orientation) stay curated in one place so corporate and compliance documents can be generated consistently from company and officer data. |
| **Entry Point / Surface** | Authenticated admin HTTP API on sleek-back: `POST /admin/document-templates`, `GET /admin/document-templates`, `GET /admin/document-templates/:templateId`, `PUT /admin/document-templates/:templateId`, `DELETE /admin/document-templates/:templateId`, `POST /admin/document-templates/:templateId/generate-doc-from-data`, `POST /admin/document-templates/convert-html-to-pdf` (`userService.authMiddleware` + `accessControlService.can("document_templates", …)`). Exact Sleek admin UI navigation label is not defined in the referenced files. |
| **Short Description** | Create and store reusable HTML templates with name, body content, and orientation. List and retrieve templates (non-deleted); updates merge validated fields. Preview merges template HTML with optional custom fields and bound company/officer context to return rendered HTML. A separate endpoint sanitizes HTML and converts it to a PDF download using shared PDF defaults and safe option whitelisting. |
| **Variants / Markets** | Unknown (template engine supports jurisdiction-style variables in the service layer; no market flag on the schema in the referenced files). |
| **Dependencies / Related Flows** | **Data binding for preview**: reads `Company` and `CompanyUser` (populated) when generating HTML from a template. **PDF**: `pdfUtils.wrapHTMLContent`, `pdfUtils.createPDFBufferFromHtml` with `config.pdfFormat` merged with sanitized options. **Downstream**: workflows and request-template flows elsewhere in the repo consume `DocumentTemplate` and `document-template-service`; not exhaustively listed here. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `documenttemplates` (Mongoose model `DocumentTemplate`; fields `name`, `content`, `orientation`, `is_deleted` default false, timestamps). **Related reads for preview only (not template CRUD persistence)**: `companies`, `companyusers` (and populated refs). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `GET` lists templates with `is_deleted: { $ne: true }`, but `DELETE` uses `deleteOne` (hard delete)—whether soft-delete is used elsewhere or `is_deleted` is legacy should be confirmed. Whether all markets use the same admin surface. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/document-template-controller.js`

- **`POST /admin/document-templates`** — `can("document_templates", "full")`; validates `name`, `content`, `orientation` (strings, required); `new DocumentTemplate(bodyCleaned).save()`.
- **`GET /admin/document-templates`** — `can("document_templates", "read")`; `DocumentTemplate.find({ is_deleted: { $ne: true } }).sort({ _id: "asc" })`.
- **`GET /admin/document-templates/:templateId`** — `can("document_templates", "read")`; `DocumentTemplate.findById`; response via `documentTemplateService.getExtendedTemplateData` (adds `bindedData` hints, custom variable names/configs from template content).
- **`PUT /admin/document-templates/:templateId`** — `can("document_templates", "full")`; optional `name`, `content`, `orientation`; `DocumentTemplate.updateOne({ _id: templateId }, reqBody)`.
- **`DELETE /admin/document-templates/:templateId`** — `can("document_templates", "full")`; `DocumentTemplate.deleteOne({ _id: templateId })`.
- **`POST /admin/document-templates/:templateId/generate-doc-from-data`** — `can("document_templates", "read")`; optional `customFields`, `bindedData` with `companyId`, `shareholderId`, `directorId`, `companyStaffId`, `selectedDirectorIds`; loads template, company, company users; `documentTemplateService.generateContentFromData`; returns `{ htmlResult }`.
- **`POST /admin/document-templates/convert-html-to-pdf`** — `can("document_templates", "read")`; `htmlToConvert` + optional `options`; sanitizes body; whitelists PDF option keys; merges `config.pdfFormat`; strips dangerous keys; `sanitize-html` on HTML; `pdfUtils.createPDFBufferFromHtml`; responds with PDF bytes.

### `schemas/document-template.js`

- **Model `DocumentTemplate`** — `name`, `content`, `orientation` (strings), `is_deleted` boolean default false, `timestamps: true`.

### `services/document-template-service.js`

- **`getExtendedTemplateData(docTemplate)`** — derives `customVariableNames`, structured field configs (`parseAllStructuredFields` / `STRUCTURED_FIELD_REGEX`), and `bindedData` array (e.g. `companyId`, `directorId`, `selectedDirectorIds`, `shareholderId`, `companyStaffId`) based on which variable families appear in content; merges onto `docTemplate._doc`.
- **`generateContentFromData(content, customFields, bindedData)`** — resolves shareholder/director/company staff/selected directors from `companyUsers`; `constructFieldData`, `fillLoops`, `replaceFieldsWithData` to produce filled HTML.
- Large keyword/loop/conditional replacement surface (`#{…}` placeholders, company/director/shareholder loops, etc.) supports rich corporate document patterns.
