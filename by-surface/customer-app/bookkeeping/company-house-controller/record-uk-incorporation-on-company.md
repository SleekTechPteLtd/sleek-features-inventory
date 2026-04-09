# Record UK incorporation on the company

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Record UK incorporation on the company |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated user (manual save via API); System / dashboard refresh path when status is polled (`id=false`) and Companies House returns an approved application |
| **Business Outcome** | The Sleek company record holds the registered UK legal identity (Companies House company number, incorporation date, and authentication code) so accounting, compliance, and downstream integrations use the correct entity. |
| **Entry Point / Surface** | Sleek customer app — UK Companies House incorporation journey. **API**: `PUT /company-house/:companyId/update-company-status` (authenticated). **Related**: `GET /company-house/:id/get-company-status` — when `id` is the string `false`, the service refreshes workflow from Companies House and, on approval, persists the same company fields. Exact UI labels are not encoded in these handlers. |
| **Short Description** | Persists Companies House **company number** onto `uen`, **incorporation date**, and **authentication code** as a `company_identifiers` entry with type `chac`. The same shape is applied when users submit via the update endpoint and when an approved response is processed from the Companies House integration (workflow refresh). `updateCompany` also copies the auth code into `accountingquestionnaires.company_house_auth_code` when a questionnaire exists. |
| **Variants / Markets** | UK |
| **Dependencies / Related Flows** | **sleek-company-house** (HTTP) for application send, status, documents, acknowledgement, platform status — this feature’s **persist** path uses `company-house-service.updateCompany` (MongoDB) and workflow updates. **Related**: `sleek-companies-house-extractor` (company schema hooks reference bulk sync by `uen`); Camunda / UK incorporation services consume company data elsewhere. |
| **Service / Repository** | sleek-back; sleek-company-house (microservice for upstream CH API calls, not for the `updateCompany` Mongo write) |
| **DB - Collections** | `companies`; `companyworkflows` (when `updateCompanyWorkflow` runs); `accountingquestionnaires` (conditional sync of `company_house_auth_code`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `PUT /company-house/:companyId/update-company-status` is intentionally limited to `authMiddleware` only (no `canManageCompanyMiddleware`); product-facing copy and screen for manual vs automatic capture. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `modules/sleek-company-house/controller/company-house-controller.js`

- **`PUT /:companyId/update-company-status`** — `userService.authMiddleware` only. Body maps `company_number` → `uen`, `incorporation_date`, `authentication_code` → `company_identifiers: [{ type: "chac", id: ... }]`. Calls `companyHouseService.updateCompany(payload, companyId)`.
- **`GET /:id/get-company-status`** — `userService.authMiddleware`. `companyHouseService.getCompanyStatus(id)`; if `id == 'false'`, `companyHouseService.updateCompanyWorkflow(companyHouseRes)` to reconcile workflow and company from CH responses.

### `modules/sleek-company-house/services/company-house-service.js`

- **`updateCompany(payload, companyId)`** — `Company.findByIdAndUpdate`. Logs `uen`, `incorporation_date`, `company_identifiers`. If `AccountingQuestionnaire` exists for the company, sets `company_house_auth_code` from the `chac` identifier (`COMPANY_IDENTIFIER_TYPES.CHAC`).
- **`updateCompanyWorkflow(responses)`** — On `chResponse.ACCEPT`, `$set` on `Company` includes `uen`, `incorporation_date`, `company_identifiers` (`chac`), matching the manual payload shape; updates `CompanyWorkflow` embedded paths under `data.submit_to_companies_house.companies_house_data.*`; calls `updatePlatformStatus` with submission numbers.

### `app-router.js`

- Router mount: **`/company-house`** → `company-house-controller`.

### `schemas/company.js`

- Fields: `uen`, `incorporation_date`, `company_identifiers` (indexed / sparse uniqueness on `uen` documented in schema comments).
