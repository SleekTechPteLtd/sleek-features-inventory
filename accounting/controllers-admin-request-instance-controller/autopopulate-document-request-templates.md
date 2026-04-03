# Autopopulate document request templates

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Autopopulate document request templates |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Sleek Admin with `requests` full access) |
| **Business Outcome** | Filled HTML for incorporation and compliance document requests is produced from templates plus live company and workflow data so staff can preview, adjust overrides, and proceed toward review and e-signing. |
| **Entry Point / Surface** | Sleek Admin — company-scoped document / request instance workflows; HTTP `POST /admin/companies/:companyId/request-instances/:requestInstanceId/auto-populate` (used after a request instance and template are selected). |
| **Short Description** | Resolves template-specific `documentData` (directors, shareholders, registers, consent secretaries, share certificates, NORC, DRIW, etc.) via `setRequestInstanceDocumentData`, merges editable `document_fields`, optionally applies `html_result_override`, then runs `constructFieldData` → `fillLoops` → `replaceFieldsWithData` on `DocumentTemplate` HTML. Persists folder selection, signers, and naming on the request instance and returns `html_result`, signer list, and extended template metadata for preview. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | Incorporation / Camunda workflow document request template IDs (`config.workflows.incorporation.documentRequestTemplateIDs`); app features (`requestTemplate`, `incorp_transfer_workflow`); downstream `send-for-signature` routes that consume filled HTML and `getSignersWithTags`; `signature-service` for generated document names; auditor logging for Sleek Admin; optional `CompanyWorkflow` / `WorkflowInstance` for linked pre-incorp documents (e.g. consent-to-act pairing). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `requestinstances`, `documenttemplates`, `companies`, `files`, `companyusers`, `users`, `partners`, `companyworkflows`, `workflowinstances`, `companyhistories`, `companyresourceusers`, `resourceallocationroles` (subset used per template). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether non–Sleek Admin callers are supported for anything beyond the early `requestInstance` resolve (the handler short-circuits the populate pipeline when `isMember(..., "Sleek Admin")` is false). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### HTTP and auth

- **Route:** `POST /admin/companies/:companyId/request-instances/:requestInstanceId/auto-populate`
- **Guards:** `userService.authMiddleware`, `accessControlService.can("requests", "full")`
- **Pre-steps:** `documentInstanceAutopopulateService.updateShareCertificateTemplate` (optional share certificate template swap), `setRandomConsentActSecretariesForGeneric` (generic consent-to-act secretary template randomization)

### Controller (`controllers/admin/request-instance-controller.js`)

- Loads `RequestInstance` with `request_template`, `company` (and `partner`), file populations (`request_folder`, `signed_file`, `client_provided_document`, additional field files).
- For **Sleek Admin** members only: loads `DocumentTemplate` by `request_template.document_template`, applies `setRequestInstanceDocumentData` body to `documentInstanceAutopopulateService.setRequestInstanceDocumentData`, may refresh template after consent-template switch (`hasRequestTemplateUpdate`).
- Merges `documentData` with `req.company`, applies `excluded_company_users` filtering, sets `selected_folder_id`, `document_fields`, optional `html_result_override` / reset, director/shareholder/secretary/registrable-controller fields, `document_name` via `signatureService.generateDocumentName` and `overrideGeneratedDocumentName`.
- **Rendering:** `documentTemplateService.constructFieldData` → `fillLoops` on `html_result_override` or `documentTemplate.content` → `replaceFieldsWithData`.
- **Signers preview:** `documentTemplateService.getSignersWithTags(filledContent, documentData)`; maps to user list when present; `getExtendedTemplateData(documentTemplate)` for client metadata.
- **Audit:** `buildAuditLog` / `auditorService.saveAuditLog` for autopopulate use (Sleek Admin path).
- **Response shape:** `{ html_result, signers, extended_doc_template_data, ...requestInstance._doc }`.

### Document instance autopopulate (`services/document-instance-autopopulate-service.js`)

- **`setRequestInstanceDocumentData(customData, requestInstance)`:** Large `switch` on `documentRequestTemplateIDs` assembling `documentData` and `documentFields` from `CompanyUser`, `CompanyHistory`, `CompanyResourceUser`, `ResourceAllocationRole`, workflow-linked `RequestInstance` lists, partner vs Sleek secretary resolution (`getResourceSecretaryByRequestTemplate`), share certificate and NORC-specific branches, DRIW payloads, etc. Resolves signature folder via `getFolderIdByRequestTemplateID` or existing folders. Returns `[documentData, fileId, documentFields, hasRequestTemplateUpdate]` or rejects with validation `errorMessage` arrays.
- **Helpers exported for related flows:** `updateShareCertificateTemplate`, `setRandomConsentActSecretariesForGeneric`, `overrideGeneratedDocumentName`, `getResourceSecretaryByRequestTemplate`.

### Document template service (`services/document-template-service.js`)

- **`constructFieldData`:** Builds field map from `document_fields` and bound company/user data for `#{...}` placeholders.
- **`fillLoops` / `replaceFieldsWithData`:** Expands loop and conditional HTML segments and replaces variables (company, director, shareholder, custom structured fields, etc.).
- **`getSignersWithTags`:** Parses signer tags from HTML for e-sign routing.
- **`getExtendedTemplateData`:** Extra template metadata for consumers.
