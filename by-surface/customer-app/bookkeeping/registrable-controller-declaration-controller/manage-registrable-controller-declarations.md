# Manage registrable controller declarations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage registrable controller declarations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Directors or main signees (writes); company users (read) |
| **Business Outcome** | The company keeps an accurate register of registrable controllers for statutory compliance. |
| **Entry Point / Surface** | Sleek App — company flows where RCD is captured (e.g. incorporation shares step); secretary / compliance areas that review and generate the declaration document |
| **Short Description** | Authenticated users with director/main-signee rights add, remove, mark review-complete, and generate a PDF summary of registrable controller entries for company members and non-members. Broader company users can load existing declaration data for the company. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | Company and company-user records; `Company` for folder resolution; PDF generation via `questionnaire-util.generatePaymentQuestionnairePDF` (HTML → PDF, upload to company `G - KYC` under Secretary); `fileService` / `pdfUtils` for document storage |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `registrablecontrollerdeclarations` (Mongoose model `RegistrableControllerDeclaration`); reads `companies` (via `Company` ref) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether non-SG markets ever reuse this module; exact app navigation labels for “review and complete” and generate-document in production UIs |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **HTTP surface** (`controllers/registrable-controller-declaration-controller.js`): `POST /companies/:companyId/registrable-controller-declaration` — `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("directorMainSignee")`; body validated for `companyId`, `authorId`, `isCompleted`, `isCompanyMember`, optional `userId`, `companyUserID`, `isCorporateShareholder`, `data`; calls `addRegistrableControllerDeclaration`. `authorId` may default from `req.user._id` when null (incorporation workflow log path). `DELETE /companies/:companyId/registrable-controller-declaration/:companyUserId` — same director/signee guard; `deleteCompanyMemberRegistrableControllerDeclaration` with `isNonCompanyMember`, `email`, `isNonCompanyMembersDeleted`. `PUT .../review-and-complete` — `updateRegistrableControllerDeclarationToReviewAndComplate`. `GET .../registrable-controller-declaration` — `canManageCompanyMiddleware("companyUser")`; `getRegistrableControllerDeclarationData`. `GET .../generate-document` — director/signee; `generateRCDDocument`.
- **Persistence** (`services/registrable-controller-declaration/registrable-controller-declaration-service.js`): `addRegistrableControllerDeclaration` saves sanitized payload; `deleteCompanyMemberRegistrableControllerDeclaration` deletes by `company` + `company_user` or non-member email / bulk non-members; `updateRegistrableControllerDeclarationToReviewAndComplate` sets `is_review_and_completed` on all rows for the company; `getRegistrableControllerDeclarationData` returns all declarations for the company; `generateRCDDocument` builds HTML tables for members vs non-members, calls `generateRcdPdf` which uses `questionnaireUtil.generatePaymentQuestionnairePDF` with filename `Registrable Controller Declaration.pdf`.
- **Schema** (`schemas/registrable-controller-declaration.js`): `company`, `user`, `author`, `company_user` refs; flags `is_removed`, `is_completed`, `is_corporate_shareholder`, `is_review_and_completed`, `is_company_member`; flexible `data` object; timestamps.
