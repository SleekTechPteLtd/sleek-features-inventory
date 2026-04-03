# Manage e-sign and document circulation in workflows

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage e-sign and document circulation in workflows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, company user (signers); Camunda pilot / internal callers for `generate-documents` and related pilot-only routes |
| **Business Outcome** | Lets teams produce incorporation and workflow documents, send them for electronic signature via SleekSign, and reset or re-queue document circulation so Camunda workflows can advance. |
| **Entry Point / Surface** | Sleek App and workflow tooling against API base `POST /v2/sleek-workflow` — signing: `/sleeksign/create`, `/sleeksign/:requestInstanceId/send`; document generation queue: `/generate-documents`; recirculation: `/documents/recirculate`, `/recirculate-documents` |
| **Short Description** | Creates request instances from templates, fills HTML from company data, converts HTML to PDF, creates a SleekSign/PandaDoc document with tagged signers, and stores signing URLs on the request. Separate handlers trigger SG/HK incorporation document generation and manual or auto recirculation (reset selected docs, analyze queue, message Camunda). |
| **Variants / Markets** | SG, HK (auto-circulation entrypoints and tenant gates in `AUTO_CIRCULATION`); other markets Unknown for this slice |
| **Dependencies / Related Flows** | Camunda (DMN / `postResource` via incorporation document analyzer), SleekSign website + PandaDoc (`signature-service` / `signature-vendor`), `document-template-service`, PDF utils, `request-instance-service` (folders), incorporation `CompanyWorkflow` data and auto-circulate queues |
| **Service / Repository** | sleek-back |
| **DB - Collections** | requestinstances, companies, companyusers, partners; companyworkflows (and related incorporation workflow state); files/refs as used by request instances and folders |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact product surface labels in the Sleek app for these API routes; AU/UK coverage for the same handlers beyond SG/HK auto-circulation constants. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routes (`controllers-v2/camunda-workflow.js`, mounted at `/v2/sleek-workflow`)

- `POST /sleeksign/create` → `generateDocumentTaskSign` — `userService.authMiddleware`
- `POST /sleeksign/:requestInstanceId/send` → `sendToSleekSign` — `userService.authMiddleware`
- `POST /generate-documents` → `handleDocumentGeneration` — `camundaPilotMiddleware` (in development, no auth; otherwise `userService.authMiddleware`)
- `POST /documents/recirculate` → `handleRecirculateDocuments` — `userService.authMiddleware`
- `POST /recirculate-documents` → `recirculateDocuments` (handler in `recirculate-documents.js`) — `userService.authMiddleware`

### `sleeksign-workflow.js`

- `generateDocumentTaskSign`: `RequestInstance.create` (status `processing_by_sleek`), `requestInstanceService.createRequestFolder`, `Company.findById`, `CompanyUser.find` with optional `excludedCompanyUsers`, `documentTemplateService.generateContentFromData` into `html_result`.
- `sendToSleekSign`: validates `htmlToConvert` + optional PDF options; loads `RequestInstance` by `requestInstanceId`, rejects if `document_to_sign_url` already set; `documentTemplateService.getSignersWithTags`, `pdfUtils.createPDFStreamFromHtml`, `Partner.findOne`, `signatureService.createDocumentFromPDF`; persists `pandadoc_id`, `document_id`, `document_to_sign_url` (SleekSign URL), `status` → `waiting_for_signatures`, `is_sleek_sign: true`.

### `generate-document.js`

- `camundaPilotMiddleware`: dev bypasses auth; prod uses `userService.authMiddleware`.
- `handleDocumentGeneration`: body `documentsToBeGenerated`, `companyId` → `IncorporationDocumentGenerator.generateDocument` (SG/HK incorporation document pipeline).
- `handleRecirculateDocuments`: `companyId`, `selectedDocumentsToReset` → service `recirculateDocuments` from `incorporation-document-generator.js`.

### `recirculate-documents.js`

- `recirculateDocuments`: body `companyId`, `entrypoint`; requires `CAMUNDA_WF_CONST.AUTO_CIRCULATION[tenant]` and valid `entrypoint` in tenant entrypoints; fires `analyzeDocumentForSending` (async, returns 200 immediately) from `incorporation-document-analyzer-multitenant`.

### External / cross-cutting

- E-sign creation path uses `config.sleeksign.websiteUrl` and PandaDoc identifiers on the request instance (`pandadoc_id`, `document_id`).
