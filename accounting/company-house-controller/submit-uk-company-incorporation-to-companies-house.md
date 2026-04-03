# Submit UK company incorporation to Companies House

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Submit UK company incorporation to Companies House |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authorized company user (`companyUser` with `canManageCompany`); system-driven refresh when polling Companies House status from the dashboard |
| **Business Outcome** | A UK incorporation application is assembled from the Sleek company profile, officers, share capital, and documents, then submitted to Companies House via the sleek-company-house service so the company can be formed and tracked through submission to approval or rejection. |
| **Entry Point / Surface** | Sleek customer app — UK incorporation / Companies House flows. API base: `POST /company-house/:companyId/send-application` (primary submit). Related: `GET /company-house/:id/get-company-status`, `POST /company-house/:companyId/get-company-document`, `PUT /company-house/:companyId/update-company-status`, `POST /company-house/send-acknowledgement` (exact UI labels not encoded in handlers). |
| **Short Description** | Builds application payload via `generateApplicationData`: company identity and registered office, SIC codes, statement of capital from share records, officers (directors, shareholders, PSCs, secretaries from internal API), optional same-day formation flag, supporting documents and custom articles as base64 from stored files, and merges optional `overrideData` from the client. Posts to the external sleek-company-house service. When the company is in `PROCESSING_INCORP_TRANSFER`, may advance status to `PROCESSING_BY_COMPANIES_HOUSE` (or `targetStatus`). Separate handlers poll status, fetch CH documents, update local company UEN/incorporation/auth code from CH callbacks, and send acknowledgements. |
| **Variants / Markets** | UK |
| **Dependencies / Related Flows** | **sleek-company-house** microservice (`config.sleekCompanyHouse.baseUrl`): `/api/send-application`, `/api/company-status/:id`, `/api/company-documents`, `/api/send-acknowledgement`, `/api/update-platform-status`. **Internal**: `company-shares-service.getCompanySharesByCompany`; `file-service.getFile` + `File` schema; `RequestInstance` for custom-articles file resolution; `GET {sleekApi}/companies/:id/company-resource-allocation/company-secretaries`. **Related**: `ltd-onboarding-service`, Camunda UK incorporation flows (`uk-incorporation-service`) also integrate `company-house-service`; `updateCompanyWorkflow` / `getCompanyStatus` tie into `CompanyWorkflow` data under `submit_to_companies_house`. |
| **Service / Repository** | sleek-back; sleek-company-house (external); Sleek API (company secretaries) |
| **DB - Collections** | `companies` (read application context; `updateCompany` sets `uen`, `incorporation_date`, `company_identifiers` including `chac`); `companyusers` (officers); `requestinstances` (custom articles file link); `files` (supporting docs); `companyworkflows` (CH transaction status, save history, doc keys); `accountingquestionnaires` (sync `company_house_auth_code` when CH auth code is stored) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether all clients use the same dashboard path for `get-company-status` with `id=false` vs transaction-specific ids; full mapping of Camunda vs direct `send-application` entry points per product SKU; behaviour when `supportingData` / `customArticles` arrays are empty vs malformed (name authorisation and custom mem/arts flags). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `modules/sleek-company-house/controller/company-house-controller.js`

- **`POST /:companyId/send-application`** — `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("companyUser")`. Loads `Company` by id, `loadSubscriptions()`. Calls `companyHouseService.generateApplicationData(req.user, company, req.body, reqQuery)`, deep-merges with `req.body.overrideData`, then `companyHouseService.sendApplication(applicationData)`. If `company.status == PROCESSING_INCORP_TRANSFER`, updates status via `companyService.updateStatus` to `req.body.targetStatus` or `PROCESSING_BY_COMPANIES_HOUSE` with optional `statusReason`. JSDoc documents `overrideData`, `targetStatus`, `statusReason`, `supportingData`, `customArticles`.
- **`GET /:id/get-company-status`** — authenticated; `companyHouseService.getCompanyStatus(id)`; if `id === 'false'`, calls `companyHouseService.updateCompanyWorkflow(companyHouseRes)` (dashboard refresh path).
- **`POST /:companyId/get-company-document`** — authenticated; forwards `doc_key`, `transaction_id` to `getCompanyDocument`.
- **`PUT /:companyId/update-company-status`** — authenticated; builds payload with `uen`, `incorporation_date`, `company_identifiers` (`chac` + authentication code) from body; `companyHouseService.updateCompany`.
- **`POST /send-acknowledgement`** — authenticated; `companyHouseService.sendAcknowledgement(reqBody)`.

### `modules/sleek-company-house/services/company-house-service.js`

- **`sendApplication`**: `POST` to `{sleekCompanyHouse.baseUrl}/api/send-application` with generated payload (includes `CompanyId`, `CompanyName`, officers, `StatementOfCapital`, `SICCodes`, `SupportingData`, `CustomMemArtsData`, etc.).
- **`generateApplicationData`**: Pulls share totals via `getShares` / `getCompanySharesByCompany`; `getOfficers` merges `CompanyUser` directors/shareholders/owners and company secretaries from Sleek API; maps addresses and CH-specific fields (`VerificationDetails`, `NatureOfControls`); optional same-day from subscription service string match; `NameAuthorisation` / `SupportingData` from `docs.supportingData`; `CustomMemArtsData` from `docs.customArticles` via `RequestInstance` + `getFiles`.
- **`getCompanyStatus`**, **`getCompanyDocument`**, **`sendAcknowledgement`**, **`updatePlatformStatus`**: HTTP wrappers to sleek-company-house APIs.
- **`updateCompanyWorkflow`**: On CH responses, updates `CompanyWorkflow` under `data.submit_to_companies_house.companies_house_data`, `_saveHistory`, and on accept calls `updateCompany` for company record; `updatePlatformStatus` with submission numbers.
- **`updateCompany`**: `Company.findByIdAndUpdate`; if `AccountingQuestionnaire` exists, sets `company_house_auth_code` from `chac` identifier.

### Unknown columns (reason)

- None — markets are UK-specific from country utilities, CH APIs, and incorporation context; any residual ambiguity is captured under Open Questions.
