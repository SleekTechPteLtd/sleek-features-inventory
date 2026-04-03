# Send documents for e-signature

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Send documents for e-signature |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Sleek Admin; `requests` permission `full` or `edit` for name generation) |
| **Business Outcome** | Client-facing corporate and compliance documents are routed for electronic execution by the correct signatories (directors, shareholders, nominees, company secretaries, and configured custom signers) and tracked on the request until signing completes. |
| **Entry Point / Surface** | Sleek Admin — document request workflows for a company: send generated HTML as PDF to Sleek Sign, send a client-uploaded PDF to Sleek Sign, or (legacy) send via PandaDoc direct view URL. |
| **Short Description** | Operations users trigger outbound e-sign flows from admin APIs: either upload path (`send-file-for-signature`) loads a client PDF from file storage and creates a Sleek Sign document with signers derived from company users (directors/shareholders/owners, excluding nominee directors where filtered), or HTML path (`send-for-signature`) renders HTML to PDF, resolves signers from template tags and extensive per-template rules, then creates a document in Sleek Sign (default) or PandaDoc (`send-for-signature/pandadoc`). Completed documents update the request instance and file store via webhooks handled in `signature-service`. |
| **Variants / Markets** | SG, HK (multi-template incorporation/compliance flows; partner “MS” client query param where applicable); other markets not explicitly enumerated in these handlers. |
| **Dependencies / Related Flows** | Sleek Sign (`signature-vendor.createDocumentFromPDF` → Sleek Sign API, webhooks); PandaDoc OAuth tokens in `Local` for `createDocumentFromPDF_pandadoc`; `sleekWebsite2BaseUrl` / `pandadoc.documentViewBaseUrl` for signer URLs; company sub-status updates (`company-service.updateSubStatus`); optional auto-circulate / auto-sign consent (`document-signing-consent-service`); file microservice vs legacy (`@sleek-sdk/sleek-files`); mailer for CS notifications after all signatures (`NOTIFY_ASSIGNED_RESOURCE_WHEN_DOCUMENT_ALL_SIGNED`). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `requestinstances`, `companyusers`, `files`, `partners`, `locals` (PandaDoc tokens), `documenttemplates` / `requesttemplates` (populate), `companyworkflows` (some template branches) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether all tenants still use the PandaDoc-only route in production; full list of markets served by the same admin UI beyond SG/HK evidence in template IDs. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routes (`controllers/admin/request-instance-controller.js`)

- **`POST /admin/request-instances/generate-document-name`** — `userService.authMiddleware`, `accessControlService.can("requests", "edit")`. Uses `signatureService.getDateFormatInDocumentName`, `signatureService.generateDocumentName` for naming preview.
- **`POST /admin/request-instances/:companyId/send-file-for-signature`** — `can("requests", "full")`. Body: `client_provided_document`, `document_name`, `selected_folder_id`. Creates `RequestInstance` (`status: processing_by_sleek`), `requestInstanceService.createRequestFolder`, loads PDF via `fileService.getFile`, builds signers with `documentTemplateService.getSignersWithTags(null, documentData, true)` (client-provided mode), then `signatureService.createDocumentFromPDF` with `{ value: Body, options: { filename } }` shape. Sets `pandadoc_id` / `document_id`, `document_to_sign_url` to `${sleekWebsite2BaseUrl}/sleek-sign/send-document/?uid=...` with optional `&client=MS` for partner companies, `status: waiting_for_signatures`, `is_sleek_sign: true`.
- **`POST /admin/request-instances/:requestInstanceId/send-for-signature`** — `can("requests", "full")`. Body: `htmlToConvert`, optional `options`, `selectedFolderId`, `autoCirculate`. Loads `RequestInstance` with template/company; rejects if `document_to_sign_url` already set. Large `switch` / feature-flag branches adjust `companyUsers` and `customSigners` per `request_template` (incorporation, risk assessment, nominee/secretary templates, HK/MS variants, etc.). `documentTemplateService.getSignersWithTags(html, documentData)`; `pdfUtils.wrapHTMLContent` + `pdfUtils.createPDFStreamFromHtml`; `signatureService.createDocumentFromPDF(stream, signers, ..., partner, autoCirculate)`. Response: `{ url, document_id }`. Also calls `companyService.updateSubStatus` after save.
- **`POST /admin/request-instances/:requestInstanceId/send-for-signature/pandadoc`** — same auth; uses `signatureService.createDocumentFromPDF_pandadoc` and sets `document_to_sign_url` to `config.pandadoc.documentViewBaseUrl + documentId` (no `is_sleek_sign` flag in this handler).
- **`GET /admin/request-instance/:documentId`** — lookup by `document_id` for Sleek Sign client (comment: “TO be used only for sleek-sign”).

### `services/signature-service.js`

- **`createDocumentFromPDF`** — maps signers to recipients (email, names, `role` from `uniqueIndex`, optional `autoSign` when `autoCirculate` + `isUserAutoSignedEnabled`), delegates to `signatureVendor.createDocumentFromPDF` (Sleek Sign).
- **`createDocumentFromPDF_pandadoc`** — PandaDoc REST upload via `getAccessToken` + `signatureVendor.createDocumentFromPDF_pandadoc`.
- **`generateDocumentName`**, **`getDateFormatInDocumentName`** — shared naming rules using `sharedData` template lists and `moment` formats.
- **Webhook-side** — `allSignaturesSigned` / `applyEventOnDocument`: downloads completed PDF (`downloadDocument` vs `downloadDocument_pandadoc`), `fileService.uploadAndCreateFile`, optional move to `selected_folder_id`, `companyService.updateSubStatus`, notifications via `sleekSignService` / `notifyAfterAllSignaturesSigned`.

### `services/document-template-service.js`

- **`getSignersWithTags(document, bindedData, clientProvidedDocument)`** — merges `customSigners`, assigns signature/datepicker/initials tag indices (`setCompanyUserTagData`), `getUniqueMembers` for director/shareholder/custom roles; filters signers either by tags present in HTML or, for client PDFs, any signer with a `signature` tag placeholder (`clientProvidedDocument === true`).

### `utils/pdf-utils.js`

- **`wrapHTMLContent`** — injects CSS/fonts, wraps body; hides `{signature:`, `{i:`, `{datepicker:`, `{dynamic:` in white for PDF output.
- **`createPDFStreamFromHtml`** — `html-pdf` stream generation with merged `config.pdfFormat` and request options.

### `services/file-service.js`

- **`getFile`** — used to load client PDF bytes for `send-file-for-signature` (delegates to legacy or `@sleek-sdk/sleek-files` per microservice toggle).
- **`uploadAndCreateFile`**, **`moveFile`**, **`moveFileAsUser`** — used downstream when signed PDFs are persisted (via `signature-service` webhook path).

### External systems

- **Sleek Sign** — primary path for new admin sends (`signature-vendor` payload includes `apiToken`, webhook `endpointURL`, `companyFolderSelected`, optional `partner_id` for managed service).
- **PandaDoc** — OAuth in `Local`; used for `.../pandadoc` route and for downloads when `!reqInstance.is_sleek_sign` in webhook handling.
