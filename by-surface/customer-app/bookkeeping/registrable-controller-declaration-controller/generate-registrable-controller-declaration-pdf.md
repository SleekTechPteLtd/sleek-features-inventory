# Generate Registrable Controller Declaration PDF

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Generate Registrable Controller Declaration PDF |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Director or main signee (authenticated user with `directorMainSignee` company permission) |
| **Business Outcome** | Directors or signees obtain a formal PDF register of registrable controller declarations for internal records and regulatory filing. |
| **Entry Point / Surface** | Sleek App — company registrable controller declaration area; backend `GET /companies/:companyId/registrable-controller-declaration/generate-document` (exact in-app navigation path not defined in these files). |
| **Short Description** | Builds HTML tables of company members and non–company members from stored declaration rows, renders a PDF named `Registrable Controller Declaration.pdf`, and uploads it to the company’s file tree under **Secretary > G - KYC**. The same handler also returns the HTML payload in the JSON response for immediate use. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | **Upstream** — `POST`/`GET`/`PUT`/`DELETE` on `/companies/:companyId/registrable-controller-declaration` to capture and review declaration data. **Internal** — `pdf-utils` (HTML wrap + PDF stream), `file-service` (`findOrCreateFolderByName`, `uploadAndCreateFile`), `questionnaire-util.generatePaymentQuestionnairePDF` (shared PDF upload path with pre/post-payment questionnaires). **Storage** — company `root_folder` / `secretary_folder` graph for KYC document placement. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `registrablecontrollerdeclarations` (Mongoose model `RegistrableControllerDeclaration`; default pluralized name — not overridden in schema), `companies` (read for company document and folder refs) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `generateRCDDocument` calls both `generateRcdHtml` and `generateRcdPdf` (which loads data and generates HTML again); confirm intentional duplication or consolidation opportunity. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/registrable-controller-declaration-controller.js`

- **`GET /companies/:companyId/registrable-controller-declaration/generate-document`** — `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("directorMainSignee")`; body `payload` `{ companyId }`; calls `generateRCDDocument(payload, res)`.

### `services/registrable-controller-declaration/registrable-controller-declaration-service.js`

- **`generateRCDDocument`**: `RegistrableControllerDeclaration.find({ company: companyId })`; builds HTML via `generateRcdHtml`; calls `generateRcdPdf(companyId)`; returns `res.json({ message: "Successfully Generated the PDF!", htmlToConvert })`.
- **`generateRcdHtml`**: splits rows into company members vs non–company members; sections “1. Company Members” and “2. Non-Company Members”; table columns include name, role or email, share percentage for members.
- **`generateRcdPdf`**: `Company.findOne({ _id: companyId })`; `RegistrableControllerDeclaration.find({ company })`; `questionnaireUtil.generatePaymentQuestionnairePDF(htmlContent, "Registrable Controller Declaration.pdf", company)`.
- **`createHtmlListFromRcd` / `renderRcdPercentageOfShares`**: inline HTML table generation for PDF content.

### `controllers-v2/handlers/utilities/questionnaire-util.js`

- **`generatePaymentQuestionnairePDF(htmlContent, fileName, company)`**: resolves or creates `Secretary` then `G - KYC` under company folders; `pdfUtils.wrapHTMLContent` → `pdfUtils.createPDFStreamFromHtml` with `config.pdfFormat`; `fileService.uploadAndCreateFile` with `replaceFile: true`.

### `schemas/registrable-controller-declaration.js`

- **`RegistrableControllerDeclaration`**: refs `Company`, `User`, `CompanyUser`; `data` mixed; flags `is_completed`, `is_review_and_completed`, `is_company_member`, etc.
