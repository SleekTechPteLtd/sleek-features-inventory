# Generate workflow e-signatures and compliance documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Generate workflow e-signatures and compliance documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (admin users with `manage_workflows` read/edit) |
| **Business Outcome** | Lets operations staff create ad hoc e-signature packages from document templates, send them through SleekSign, and render AML-related artefacts (PEP declaration, pre- and post-payment questionnaire answers) as HTML for clients and internal review. |
| **Entry Point / Surface** | Admin workflow API mounted at `/v2/admin/workflow` — SleekSign: `POST /api/sleeksign/create`, `POST /api/sleeksign/:requestInstanceId/send`; PEP HTML: `GET /api/pep-declaration/download/html/:companyUserId`, `GET /api/pep-declaration/:version/download/html/:companyUserId`; questionnaires: `GET /api/pre-payment-questionnaire/view/:companyId`, `GET /api/post-payment-questionnaire/view/:companyId` |
| **Short Description** | Creates a request instance from a template, fills HTML from company and company-user data, and on send converts HTML to PDF and creates a PandaDoc-backed SleekSign document with tagged signers. Separate GET handlers return Customer Acceptance Form–style PEP HTML (versions 1 and 2), a tenant-aware “Pre-payment answers” HTML view from `Company` (and optional `CompanyProfile` for crypto questions in PDF path), and “Post-payment answers” from `CompanyQuestionnaireForm` (post-payment view also generates a PDF via shared questionnaire utilities). |
| **Variants / Markets** | Tenant-driven (`sharedData.tenant`, `app-features`); localization strings reference SG/HK-style fields (e.g. proposed company names, financial year). Broader AU/UK coverage for these specific admin routes not confirmed in code — list as **SG, HK** with other markets **Unknown** unless product confirms. |
| **Dependencies / Related Flows** | `document-template-service` (content + signers), `signature-service` / PandaDoc (`createDocumentFromPDF`), `pdf-utils`, `request-instance-service` (folders), `Partner` SleekSign URL config; Camunda/WFE completion helpers in the same `sleeksign-workflow.js` module for webhook-driven flows (not mounted on these admin routes). Questionnaire PDF helpers: `questionnaire-util.generatePaymentQuestionnairePDF`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | requestinstances, companies, companyusers, partners, files (SleekSign path); customeracceptanceforms (PEP); companyprofiles (pre-payment HTML/PDF extended path); companyquestionnaireforms (post-payment) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact Sleek Admin UI labels and navigation for these endpoints; whether every `GET` to post-payment questionnaire should regenerate the PDF; full market list beyond SG/HK for questionnaire field visibility. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Router mount

- `app-router.js`: `router.use("/v2/admin/workflow", require("./controllers/admin/new-workflow-controller.js"))`.

### Auth surface (`new-workflow-controller.js`)

- GET routes: `userService.authMiddleware` + `accessControlService.can("manage_workflows", "read")`.
- POST routes (including SleekSign): `userService.authMiddleware` + `accessControlService.can("manage_workflows", "edit")`.

### SleekSign (`controllers-v2/handlers/workflow/sleeksign-workflow.js`)

- `generateDocumentTaskSign`: `RequestInstance.create` (`status: processing_by_sleek`), `requestInstanceService.createRequestFolder`, `Company.findById`, `CompanyUser.find` with optional `excludedCompanyUsers`, `documentTemplateService.generateContentFromData` → `html_result` on response.
- `sendToSleekSign`: validates `htmlToConvert` + PDF options; loads `RequestInstance` by `requestInstanceId`; rejects if `document_to_sign_url` exists; `documentTemplateService.getSignersWithTags`, `pdfUtils.createPDFStreamFromHtml`, `Partner.findOne`, `signatureService.createDocumentFromPDF`; persists `pandadoc_id`, `document_id`, `document_to_sign_url` (tenant feature `admin_sleek_sign_url_version` vs legacy `config.sleeksign.websiteUrl`), `status` → `waiting_for_signatures`, `is_sleek_sign: true`.
- Same module exports webhook helpers (`completeTaskAfterSigning`, `completeEmbeddedWorkflowRequestsTaskAfterSigning`, Camunda/WFE `postResource`) for signed-document completion — used outside this admin router.

### PEP declaration (`pep-declaration-download.js`)

- `generatePepDeclarationHtml`: `CompanyUser` + `company`, `user`; `CustomerAcceptanceForms.findOne` by `companyUser` and optional `version` (v1 default / v2 adds conviction question); builds inline HTML “CUSTOMER ACCEPTANCE FORM” with PEP Yes/No fields from stored answers.

### Pre-payment questionnaire (`pre-payment-questionnaire.js`)

- `generatePrePaymentQuestionnaire`: loads `Company`, builds “Pre-payment answers” HTML from incorporation/source-of-funds/objectives/hear-about-us/business-account fields; optional Web3 flag from company; `res.json({ html })`.
- Also exports `generatePrePaymentQuestionnaireHTML` / `generatePrePaymentQuestionnairePDF` (PDF path uses `CompanyProfile` for crypto-related questions when enabled).

### Post-payment questionnaire (`post-payment-questionnaire.js`)

- `generatePostPaymentQuestionnaire`: `generatePostPaymentQuestionnaireHTML` from `CompanyQuestionnaireForm` + partner `post_payment` app-feature props; then `generateQuestionnairePDF` → `questionnaireUtil.generatePaymentQuestionnairePDF` (“Post-payment answers.pdf”); `res.json({ html })`.

### File paths

- `controllers/admin/new-workflow-controller.js`
- `controllers-v2/handlers/workflow/sleeksign-workflow.js`
- `controllers-v2/handlers/pep-declaration/pep-declaration-download.js`
- `controllers-v2/handlers/pre-payment-questionnaire-view/pre-payment-questionnaire.js`
- `controllers-v2/handlers/post-payment-questionnaire-view/post-payment-questionnaire.js`
