# Track Companies House incorporation progress

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Track Companies House incorporation progress |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client (authenticated user); company users with manage rights on `send-application` (`canManageCompanyMiddleware("companyUser")`) |
| **Business Outcome** | UK incorporation stays visible and accurate: users see Companies House application status, obtain incorporation documents for a transaction, and—when they refresh from the dashboard—workflow and company records update to match Companies House accept or reject outcomes. |
| **Entry Point / Surface** | Sleek customer app — UK Ltd / Companies House incorporation flows (exact screen labels not in these handlers); API: `sleek-back` routes under `/company-house` (mounted in `app-router.js`). Dashboard “refresh” uses `GET /company-house/:id/get-company-status` with `id=false`. |
| **Short Description** | Proxies to the `sleek-company-house` service for submission, status, documents, acknowledgement, and platform status updates. Status refresh from the dashboard loads CH responses and runs `updateCompanyWorkflow`, which patches `CompanyWorkflow` (submit-to-Companies-House data, history) and, on acceptance, updates the `Company` and linked accounting questionnaire auth code. |
| **Variants / Markets** | UK |
| **Dependencies / Related Flows** | **External**: `config.sleekCompanyHouse.baseUrl` (send-application, company-status, company-documents, send-acknowledgement, update-platform-status). **Internal**: `company-service` (status on submit path), `company-shares-service` (application payload), `sleekApiBaseUrl` company secretaries, `file-service` / `File` for supporting docs. **Related**: Camunda `CompanyWorkflow` shape `data.submit_to_companies_house.companies_house_data`; `ltd-onboarding` and UK incorporation services (other call sites). |
| **Service / Repository** | sleek-back; sleek-company-house (HTTP integration) |
| **DB - Collections** | `companies`; `companyworkflows`; `companyusers`; `accountingquestionnaires`; `requestinstances`; `files` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether non-dashboard clients call `get-company-status` with a real transaction id vs only workflow automation; product copy for dashboard refresh vs per-company status. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `modules/sleek-company-house/controller/company-house-controller.js`

- **`POST /:companyId/send-application`** — `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("companyUser")`. Loads `Company`, `companyHouseService.generateApplicationData`, merges `overrideData`, `companyHouseService.sendApplication`. If company is `PROCESSING_INCORP_TRANSFER`, may `companyService.updateStatus` toward `PROCESSING_BY_COMPANIES_HOUSE` (or `targetStatus` / `statusReason` from body).
- **`GET /:id/get-company-status`** — `userService.authMiddleware`. `companyHouseService.getCompanyStatus(id)`; if `id === 'false'` (dashboard CH refresh), `companyHouseService.updateCompanyWorkflow(companyHouseRes)`.
- **`POST /:companyId/get-company-document`** — `userService.authMiddleware`. Body `doc_key`, `transaction_id` → `companyHouseService.getCompanyDocument`.
- **`PUT /:companyId/update-company-status`** — `userService.authMiddleware`. Sets `uen`, `incorporation_date`, `company_identifiers` (type `chac`) → `companyHouseService.updateCompany`.
- **`POST /send-acknowledgement`** — `userService.authMiddleware`. `companyHouseService.sendAcknowledgement`.

### `modules/sleek-company-house/services/company-house-service.js`

- **HTTP to sleek-company-house**: `postResource` / `getResource` to `/api/send-application`, `/api/company-status/:id`, `/api/company-documents`, `/api/send-acknowledgement`, `/api/update-platform-status`.
- **`generateApplicationData`**: Builds payload from `Company`, `getCompanySharesByCompany`, officers from `CompanyUser` + company secretaries API, SIC, addresses, optional same-day formation, supporting/custom article files via `File` / `fileService.getFile`.
- **`updateCompanyWorkflow`**: Maps CH accept/reject (`chResponse`, `chStatus`) into `CompanyWorkflow` updates on `data.submit_to_companies_house.companies_house_data.transaction_id`; `_saveHistory` with `requestTracer.getUser()`; on accept, `updateCompany` for `workflow.company`; `updatePlatformStatus(submission_numbers)` after batch.
- **`updateCompany`**: `Company.findByIdAndUpdate`; if `AccountingQuestionnaire` exists, syncs `company_house_auth_code` from `company_identifiers` type `CHAC`.
