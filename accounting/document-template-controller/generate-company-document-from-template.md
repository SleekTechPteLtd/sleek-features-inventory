# Generate company document from template

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Generate company document from template |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (admin API: `document_templates` permission `read`; code notes request is admin-driven—if non-admin callers are added later, per-company authorization should be enforced) |
| **Business Outcome** | Staff can produce company-specific HTML from a stored template in one step, using live registry and people data, so documents can be reviewed or issued without manual copy-paste. |
| **Entry Point / Surface** | Authenticated admin HTTP API: `POST /admin/document-templates/:templateId/generate-doc-from-data` (`userService.authMiddleware` + `accessControlService.can("document_templates", "read")`). Often paired with `POST /admin/document-templates/convert-html-to-pdf` for issuance. Exact Sleek admin UI path is not defined in the referenced files. |
| **Short Description** | Accepts optional `customFields` and `bindedData` (company id and optional officer selection ids). Loads the template, company record, and all company users (with `user` and `shareholder.corporate` populated), enriches bind context, and runs the template engine to return `{ htmlResult }` filled HTML. |
| **Variants / Markets** | SG, HK, UK, AU (company schema and template field builders encode multi-jurisdiction identifiers and roles; no single market flag on the generation request). |
| **Dependencies / Related Flows** | **Upstream**: document template CRUD and `getExtendedTemplateData` for variable hints (`manage-document-templates` in same module). **Service**: `document-template-service` (`constructFieldData`, `fillLoops`, `replaceFieldsWithData`, conditionals); may read `CompanyProfile` for extended company fields. **Downstream**: HTML→PDF conversion endpoint; SleekSign and workflows elsewhere consume the same service patterns. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | **Reads**: `documenttemplates` (template by id), `companies` (by `companyId`), `companyusers` (by company, populated). **During merge**: `companyprofiles` when `constructFieldData` loads profile for the company. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/document-template-controller.js`

- **`POST /admin/document-templates/:templateId/generate-doc-from-data`** — validates `customFields` (object), `bindedData` (object); if `bindedData` present, validates `companyId`, `shareholderId`, `directorId`, `companyStaffId`, `selectedDirectorIds` (with defaults). Loads `DocumentTemplate.findById(templateId)`, `Company.findById(companyId)`, `CompanyUser.find({ company }).populate(["user", "shareholder.corporate"])`. Formats user display names via `userService.formatUserDataName` on each populated user. Attaches `company` and `companyUsers` to `bindedData`. On missing template, rejects with `"DocumentTemplate not found"`. Calls `documentTemplateService.generateContentFromData(docTemplate.content, customFields, bindedData)` and returns `{ htmlResult: filledContent }`. Errors logged under `[generate-doc-from-data]` and returned as 422 JSON.

### `services/document-template-service.js`

- **`generateContentFromData(content, customFields, bindedData)`** — resolves `shareholder`, `director`, `companyStaff`, `selectedDirectors`, `main_poc` from `companyUsers` using ids in `bindedData`. Runs `constructFieldData(customFields, bindedData)` (async: company profile, role-based extracts, many `get*FieldData` mergers), `fillLoops(content, bindedData)`, then `replaceFieldsWithData` for final placeholder substitution.
- **`constructFieldData`** — enriches users with company-user roles from microservice where applicable; merges `customFields` with layout tokens (`PAGE_BREAK`, headers/footers); loads `CompanyProfile` for company-scoped fields; builds field maps for company, directors, shareholders, staff, loops, signers, share items, workflows, selected officers, etc.
- **`getExtendedTemplateData`** (related) — used by `GET /admin/document-templates/:templateId` to expose which `bindedData` keys and custom variables the template expects; supports UI binding before calling generate.

### `schemas/document-template.js`

- **`DocumentTemplate`** — `content` holds HTML with service-defined placeholders, loops, and structured field syntax; generation reads stored `content` only (no write).

### `schemas/company.js` / `schemas/company-user.js`

- **`Company`** — canonical company registry fields consumed by `getCompanyFieldData` and related builders (identifiers, addresses, status, shares, subscriptions, etc., per template variables).
- **`CompanyUser`** — links `company`, `user`, `director`, `shareholder`, roles, invitation/KYC metadata; populated for per-person template fields and `main_poc` resolution.
