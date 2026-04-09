# Internal company lookup and search

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Internal company lookup and search |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Internal Sleek services and support tooling can resolve companies by id or filters and, when needed, load related accounting questionnaire data, company users, and subscription context for orchestration and investigations without using customer-facing app surfaces. |
| **Entry Point / Surface** | `sleek-back` internal HTTP routes under `/internal/...`, guarded by `internalServicesMiddleware` (Basic auth with configured internal secret; optional bypass for local/dev). Not for web or mobile clients. |
| **Short Description** | Exposes read APIs to fetch a single company by id, search companies by name, UEN, id(s), date range on `updatedAt`, and receipt status, with pagination. The aggregate endpoint can optionally join accounting questionnaires and company users (plus user documents), and enrich results with subscription validation when requested. Additional routes on the same controller return resource users, company users, receipt users, and accounting questionnaire answers per company. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | **`validateCompaniesSubscriptions`**: for `microservice_enabled` companies, loads subscriptions via `SubscriptionService.getSubscriptionListByCompanyIds` (sleek-subscription module). For legacy companies, merges `subscriptions` on the company document with `BillingConfig`, `billingConfigService.getXeroItems`, and `xeroInvoiceCodes` to attach `serviceType`, display flags, and filters. **`companyResourceUserService`** for resource-user listings. **`accountingQuestionnaireService`** for questionnaire field updates (other-currency path). Mongo `$lookup` to `accountingquestionnaires`, `companyusers`, `users`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (Mongoose `Company`), `accountingquestionnaires`, `companyusers`, `users`, `receiptusers` (routes that query `ReceiptUser`); `AccountingQuestionnaire` reads/writes for questionnaire endpoints; `BillingConfig` when subscription validation runs the non-microservice path. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/internal-service/company-controller.js`

- **`internalServicesMiddleware()`** on all exported routes; auth is Basic `Authorization` with internal secret (`middlewares/internal-services.js`).
- **`GET /internal/companies/:companyId`**: validates `companyId` as ObjectId; `Company.findById(companyId)`; returns `{ company }`.
- **`POST /internal/companies`**: body filters `name` (case-insensitive regex), `uen`, `company_id`, `start_date`/`end_date` on `updatedAt`, `skip`/`limit`; `Company.find(queryParams).skip().limit()`.
- **`GET /internal/findAllCompanies`**: query params as above plus `company_ids`, `include_accounting_questionnaire`, `include_company_users`, `include_subscriptions`, `subscription_service_type`, `receipt_system_status`; builds `Company.aggregate` with `$match`, `$skip`, `$limit`; optional `$lookup`/`$unwind` for `accountingquestionnaires`; optional `$lookup` to `companyusers` and `users`; if `include_subscriptions`, calls `validateSubscriptionService.validateCompaniesSubscriptions(company, subscription_service_type)`.
- **`GET /internal/companies/:companyId/resource-users`**, **`.../accounting-resource-users-with-role-info-by-company-id`**: delegate to `companyResourceUserService`.
- **`GET /internal/companies/:companyId/company-users`**: `CompanyUser.find({ company }).populate("user")`.
- **`GET /internal/companies/:companyId/receipt-users`**: `ReceiptUser.find({ company: companyId })`.
- **`GET /internal/companies/:companyId/accounting-questionnaire-answers`**: `AccountingQuestionnaire.findOne({ company })`.
- **`PUT /internal/companies/:companyId/accounting-questionnaire/other-currency`**: Joi body `other_currency`; `accountingQuestionnaireService.updateQuestionnaireFieldData`.
- **`GET /internal/get-all-banks-in-accounting-questionnaire`**: questionnaires with multiple banks, optional `company_id` filter, populate `company`.

### `services/subscriptions/validate-subscriptions.js`

- **`validateCompaniesSubscriptions(companies, serviceType)`**: normalizes to array; branches on `microservice_enabled` vs embedded `subscriptions`; uses `SubscriptionService.getSubscriptionListByCompanyIds` for microservice companies; otherwise enriches/filters using `BillingConfig`, `billingConfigService`, `tenant`/`xeroInvoiceCodes` flags (inactive filtering, dormant plan, optional `serviceType` filter on enriched `serviceType`).

### `schemas/company.js`

- **Mongoose model `Company`**: large company document including `subscriptions` / `old_subscriptions`, `microservice_enabled`, `receipt_system_status`, `partner`, identifiers (`uen`, etc.), and multi-jurisdiction fields (comments reference SG, HK, AU, UK). Pre-save hooks clear `subscriptions` when `microservice_enabled` is true; other hooks touch SleekSign, workflows, UK Companies House sync — not specific to internal lookup but explain stored shape.
