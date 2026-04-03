# Complete KYC company questionnaires

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Complete KYC company questionnaires |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client (company user) via authenticated API; Partner-app users where `isPartner` applies; Operations (admin workflow preview routes) |
| **Business Outcome** | Collect incorporation and due diligence answers (PEP, criminal history, business geography, referrals, declarations) and persist PDF snapshots under the company’s **G - KYC** document area for compliance and audit. |
| **Entry Point / Surface** | **Client API** (Sleek / Partner apps — exact screen labels not in these files): `GET` / `POST /companies/:companyId/company-questionnaire-form` with `userService.authMiddleware`. **Admin preview HTML** (`controllers/admin/new-workflow-controller.js`): `GET .../api/pre-payment-questionnaire/view/:companyId` and `GET .../api/post-payment-questionnaire/view/:companyId` with `userService.authMiddleware` and `accessControlService.can("manage_workflows", "read")` (full path prefix depends on how the workflow router is mounted, e.g. tests use `/v2/admin/workflow`). |
| **Short Description** | Clients retrieve and submit the **company questionnaire form** (post-payment KYC fields stored on `CompanyQuestionnaireForm`). On create/update, audit logs are written. If admin app feature `generate_pre_post_answer_pdf` is enabled, the backend asynchronously generates **Post-payment answers.pdf** from the saved form; for **partner** submissions it also generates **Pre-payment answers.pdf** from `Company` (and related) onboarding fields. PDFs are created via HTML → PDF and uploaded into **Secretary → G - KYC** on the company file tree. |
| **Variants / Markets** | SG, HK (tenant-specific question copy and optional fields, e.g. proposed company names for HK); Partner vs non-partner (relaxed vs strict validation; partner-only pre-payment PDF from this POST path). |
| **Dependencies / Related Flows** | **File storage**: `fileService.findOrCreateFolderByName` → `Secretary` → `G - KYC`; `fileService.uploadAndCreateFile` with `replaceFile: true`. **Partner config**: `getPartnerByCompanyId`, `app-features` (`post_payment.company_questionnaire.declaration`, etc.). **Related**: Other flows (e.g. onboarding / invoice services) may call `generatePrePaymentQuestionnairePDF` outside this controller; accounting onboarding is a separate questionnaire (`AccountingQuestionnaire` on `/companies/:companyId/accounting-questionnaire`). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | Mongoose models `Company`, `CompanyQuestionnaireForm`, `CompanyProfile` (pre-payment HTML path for crypto-related onboarding fields when enabled), `File`; default MongoDB pluralised collection names. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/company-controller.js`

- **`GET /companies/:companyId/company-questionnaire-form`**: `userService.authMiddleware`; loads `Company` by id; `CompanyQuestionnaireForm.findOne({ company })`; returns the document or `{}`.
- **`POST /companies/:companyId/company-questionnaire-form`**: `userService.authMiddleware`; validates body with partner vs non-partner rules (`nameOfCountries`, `hasPoliticallyExposedPerson`, `intendedNameOfCompanyUsers`, `hasUserWithCriminalConvictions`, `chargesOfUsers`, `howDidYouHearAboutUs`, `hasDeclaredInformationIsTrueAndCorrect`, `isPartner`). Creates or updates `CompanyQuestionnaireForm`, sets `user` to `req.user._id`, `auditorService.saveAuditLog` with `buildAuditLog` for create/update.
- **PDF triggers** (after save): reads `appFeatureUtil.getAppFeaturesByName("generate_pre_post_answer_pdf", "admin")`. If `enabled`: `postPaymentQuestionnaire.generateQuestionnairePDF(companyId)` (fire-and-forget). If `isPartner` and same flag: `prePaymentQuestionnaire.generatePrePaymentQuestionnairePDF(companyId)`.

### `controllers-v2/handlers/post-payment-questionnaire-view/post-payment-questionnaire.js`

- **`generateQuestionnairePDF(companyId)`**: Loads `Company`; builds HTML via `generatePostPaymentQuestionnaireHTML` from `CompanyQuestionnaireForm` + partner app-features (`post_payment` / `company_questionnaire` / `declaration`); calls `questionnaireUtil.generatePaymentQuestionnairePDF(html, "Post-payment answers.pdf", company)`.
- **`generatePostPaymentQuestionnaireHTML`**: Renders PEP/criminal questions, country list (wording differs when `sharedData.tenant.name === "sg"`), optional declaration block, “How did you hear about us?” list.
- **`generatePostPaymentQuestionnaire`**: Express handler returning JSON `{ html }` and invoking PDF generation (admin workflow view).

### `controllers-v2/handlers/pre-payment-questionnaire-view/pre-payment-questionnaire.js`

- **`generatePrePaymentQuestionnairePDF(companyId)`**: Loads `Company`; `generatePrePaymentQuestionnaireHTML(company)` includes company name, business activity, source of funds, incorporation reasons, optional SBA/business-account fields, Web3/crypto blocks when app-features enabled (`CompanyProfile` for crypto answers in full HTML path), HK-specific fields; `questionnaireUtil.generatePaymentQuestionnairePDF(..., "Pre-payment answers.pdf", company)`.
- **`generatePrePaymentQuestionnaire`**: Express handler returning HTML preview JSON for admin workflow.

### `controllers-v2/handlers/utilities/questionnaire-util.js`

- **`generatePaymentQuestionnairePDF(htmlContent, fileName, company)`**: Ensures `Secretary` and **`G - KYC`** folders under `company.root_folder`; wraps HTML with `pdfUtils.wrapHTMLContent`, `pdfUtils.createPDFStreamFromHtml`, `fileService.uploadAndCreateFile` with `replaceFile: true` (comment in code: upload to G - KYC).

### `schemas/company-questionnaire-form.js`

- Model `CompanyQuestionnaireForm`: `company`, `nameOfCountries`, `hasPoliticallyExposedPerson`, `intendedNameOfCompanyUsers`, `hasUserWithCriminalConvictions`, `chargesOfUsers`, `howDidYouHearAboutUs[]`, `hasDeclaredInformationIsTrueAndCorrect`, `user`; `timestamps: true`.

### `controllers/admin/new-workflow-controller.js`

- **`buildAuthenticatedGetRoute`**: `GET /api/pre-payment-questionnaire/view/:companyId` → `generatePrePaymentQuestionnaire`; `GET /api/post-payment-questionnaire/view/:companyId` → `generatePostPaymentQuestionnaire` (returns JSON `{ html }`; post-payment handler also triggers PDF generation for the company).
