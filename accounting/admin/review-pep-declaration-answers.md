# Review PEP declaration answers

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Review PEP declaration answers |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Sleek Admin with company-wide access) |
| **Business Outcome** | Authorized internal staff can read a client user’s politically exposed person (PEP) declaration responses for AML compliance, audits, and customer support without impersonating that user. |
| **Entry Point / Surface** | `sleek-back` HTTP API: `GET /v2/admin/users/:userId/pep-declaration/answers/:version` (authenticated + `accessControlService.can("companies", "full")`). Exact Sleek Admin UI path is not defined in these files. |
| **Short Description** | Resolves the user by `userId`, applies a version filter (legacy v1 vs explicit version), finds the most recently updated `CustomerAcceptanceForm` across all of that user’s company memberships, and returns the PEP questionnaire payload or `data: null`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Shared handler** with `GET /v2/users/:userId/pep-declaration/answers/:version` (owner-only via `canManageUserMiddleware("owner")`). **Related**: `GET /v2/company-users/:companyUserId/pep-declaration/answers` reads by company-user; PDF generation from the same stored answers (`createPDFUserPepDeclarationAnswers`, `pepDeclarationAnswer.generatePepDeclarationPDF`). See also `accounting/company-user/view-pep-declaration-answers-company-users.md`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | Reads `User`, `CompanyUser`, and `CustomerAcceptanceForm` (Mongoose default pluralised MongoDB collection names); no writes. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/admin.js`

- **`GET /users/:userId/pep-declaration/answers/:version`**: `buildAuthenticatedGetRoute` → `userService.authMiddleware`, `accessControlService.can("companies", "full")`, `getUserPepDeclarationAnswers`.

### `controllers-v2/handlers/pep-declaration/answers.js`

- **`getUserPepDeclarationAnswers`**: Comment documents admin path `/v2/admin/users/:userId/pep-declaration/answers/:version` vs user path. Loads `User` by `userId`; builds `versionFilter` (v1 or missing vs `version` > 1); `CompanyUser.find({ user: params.userId })`; `CustomerAcceptanceForms.findOne({ $and: [ { companyUser: { $in: … } }, versionFilter ] }).sort({ updatedAt: -1 }).limit(1).populate("companyUser")`. Returns `200` + `data` or `data: null`.

### `schemas/customer-acceptance-form.js`

- Model `CustomerAcceptanceForm`: nested PEP-related groups (`at_present`, `has_stepped_down`, `has_stepped_down_immediate_or_close`, `have_you_ever_been_convicted`, `pep_related`), optional `version`, refs to `company` and `companyUser`.

### Tests

- `tests/controllers-v2/user/get-user-pep-declaration-answers.js` — includes `GET /v2/admin/users/:userId/pep-declaration/answers/:version` with admin token (“Admin user should be able to GET another user's PEP declaration answers”).
