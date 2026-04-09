# View PEP declaration answers for company users

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | View PEP declaration answers for company users |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Compliance (Sleek Admin); Company member (when viewing their own company-user record) |
| **Business Outcome** | Compliance and authorized staff can read a company member’s politically exposed person (PEP) declaration responses to support AML screening and audit. |
| **Entry Point / Surface** | `sleek-back` HTTP API: `GET /v2/company-users/:companyUserId/pep-declaration/answers` (`userService.authMiddleware` + Sleek Admin **or** logged-in user matches that company user). Related read APIs in the same handler module: `GET /v2/users/:userId/pep-declaration/answers/:version` and `GET /v2/admin/users/:userId/pep-declaration/answers/:version` (user-scoped, versioned). Exact Sleek app / Admin UI labels are not defined in these files. |
| **Short Description** | Loads the `CompanyUser` for `companyUserId`, then returns the linked `CustomerAcceptanceForm` document (PEP questionnaire fields) or `data: null` if none exists. Access is restricted to Sleek Admin or the individual whose company-user record is requested. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Data model**: PEP answers live on `CustomerAcceptanceForm` (per `companyUser`), not a separate PEP-only store. **Related**: `PUT /v2/users/:userId/pep-declaration/create-pdf` generates a PDF from the same form data (`pepDeclarationAnswer.generatePepDeclarationPDF`); authenticated HTML download routes under legacy `/api/pep-declaration/...` (`pep-declaration-download`). User-scoped GET endpoints share `getUserPepDeclarationAnswers` for admin vs owner-managed user routes. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | Mongoose models `CompanyUser` and `CustomerAcceptanceForm` (MongoDB default pluralised collection names); reads only for this GET handler. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/handlers/pep-declaration/answers.js`

- **`getPepDeclarationAnswers`**: `CompanyUser.findOne({ _id: params.companyUserId }).populate(["company", "user"])`. On missing company user → `ERROR_CODES.USERS.DOES_NOT_EXISTS`. Then `CustomerAcceptanceForms.findOne({ companyUser: companyUser._id })`. Returns `200` with `data: null` or `data: customerAnswers`.
- **`getUserPepDeclarationAnswers`**: Resolves `User` by `userId`; builds query over all `CompanyUser` rows for that user, combines with `version` filter (version 1 vs legacy `$exists: false`, or explicit version > 1), `CustomerAcceptanceForms.findOne(...).sort({ updatedAt: -1 }).limit(1).populate("companyUser")`. Used from user and admin routers (see below).
- **`createPDFUserPepDeclarationAnswers`**: Same form lookup pattern as user GET, then `pepDeclarationAnswer.generatePepDeclarationPDF(companyId, user, customerAnswers)` — separate surface from the company-user GET but same stored answers.

### `controllers-v2/company-user.js`

- **`GET /:companyUserId/pep-declaration/answers`**: `buildAuthenticatedAdminOrCompanyUserGetRoute` → `userService.authMiddleware`, then `adminOrLoggedCompanyUserAuthMiddleware`: **Sleek Admin** **or** logged-in user id matches the `CompanyUser`’s `user` (else `401`). Mounted at `/v2/company-users` (`app-router.js`).

### `controllers-v2/user.js`

- **`GET /:userId/pep-declaration/answers/:version`**: `userService.authMiddleware`, `userService.canManageUserMiddleware("owner")`, `getUserPepDeclarationAnswers`.

### `controllers-v2/admin.js`

- **`GET /users/:userId/pep-declaration/answers/:version`**: `buildAuthenticatedGetRoute` with `accessControlService.can("companies", "full")`, `getUserPepDeclarationAnswers`.

### `schemas/company-user.js`

- Model `CompanyUser`: links `company` and `user`; KYC and onboarding fields; used as the join for which acceptance form applies to which membership.

### `schemas/customer-acceptance-form.js`

- Model `CustomerAcceptanceForm`: `company`, `companyUser`, optional `version`; nested groups `at_present`, `has_stepped_down`, `has_stepped_down_immediate_or_close`, `have_you_ever_been_convicted`, `pep_related` (booleans plus free-text PEP details). `timestamps: true`.

### Tests

- `tests/controllers-v2/company-user/get-company-user-pep-declaration-answers.js` — `GET /v2/company-users/:companyUserId/pep-declaration/answers`.
- `tests/controllers-v2/user/get-user-pep-declaration-answers.js` — user and admin PEP answer routes.
