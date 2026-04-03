# Accounting onboarding and finance reporting

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Accounting onboarding and finance reporting |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Bookkeeper, Operations User (subscription/onboarding triggers); System (workflows, sync, emails) |
| **Business Outcome** | Clients and staff collect finance, payroll, tax, and bank data in one place; bank accounts align with the bank-statement service; onboarding emails and workflow steps run; integrations receive updates; embedded analytics (Tableau) and accounting dashboards become available when setup finishes. |
| **Entry Point / Surface** | Sleek customer app / website — accounting setup and accounting onboarding questionnaire (`/accounting-setup`, `/accounting-onboarding-questionnaire` links from email); API `POST /companies/:companyId/accounting-questionnaire`, `GET /companies/:companyId/accounting-questionnaire-answers`, `POST /companies/:companyId/get-tableau-token` |
| **Short Description** | Persists the accounting questionnaire (finance, payroll, tax, files, e‑commerce, market-specific fields), syncs bank accounts to Sleek BSM when enabled, emits Kafka events to the coding engine and for accounting-tool changes, starts or continues the accounting onboarding workflow (Camunda or legacy WFE), optionally drives Zapier handoffs, and when the questionnaire is marked done launches the accounting dashboard entry and supports Tableau trusted tokens for embedded reporting. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Sleek workflow engine (`sleekWfeBaseUrl`) for `accountingonboarding` start/update; Camunda alternative path; Sleek BSM (`sleekBSM`) for bank accounts; Kafka topics `CompanyDataToCEUpdateReceived`, `sleek-back.company-status-had-changed` / assignee events, `accounting_tool_update` via `CompanyDataUpdateReceived`; optional Zapier via `sendPostAccountQuestionnaire` / `sendAccountQuestionnaire`; Xero / accounting ledger tool selection; `companyService.updateDashBoardLaunchedByCompanyWorkflow` for dashboard launch |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `accountingquestionnaires` (AccountingQuestionnaire schema), `companyusers` (questionnaire token, permitted pages), `companies` (e.g. `accounting_tools.accountingLedger`), `users` (tax number sync from questionnaire tax info via accounting-questionnaire-service) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact market gating per field is spread across tenant app features and schema; confirm whether all assignee Kafka paths are in scope for this capability vs. general company-user management. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`controllers/company-controller.js`**
  - `POST /companies/:companyId/accounting-questionnaire` — auth middleware; loads app features (onboarding meta, `bank_statement_engine`, PSG, accounting setup flags); validates bank statement sources via `accountingQuestionnaireService.validateBankStatementSource`; when BSM enabled, `getBanks`, `createAccountByCompanyId`, `updateAccountByCompanyId`, `deleteAccountByCompanyId` from `bank-statement-services`; creates/updates `AccountingQuestionnaire` with finance, payroll, tax, UK/AU fields, files, banks, progress statuses; audit via `auditorService.saveAuditLog` + `buildAuditLog`; `syncCodingEngineCompanyData` + questionnaire/banks payload; on finance/payroll “done”, updates contacts; `isTriggerAccountingWorkflow` → either `ACCOUNTING_QUESTIONNAIRE_UTILS.startCamundaWorkflowInstance` or `accountingOnboardingService.startAccountingOnboarding` after `getAllProcessRequest` / `getProcessesForAccountingOnboarding`; optional Zapier `sendPostAccountQuestionnaire` / `sendAccountQuestionnaire`; when status `DONE`, `companyService.updateDashBoardLaunchedByCompanyWorkflow(..., LIVE_DASHBOARD_ENTRYPOINTS.ACCOUNTING)`.
  - `GET /companies/:companyId/accounting-questionnaire-answers` — canManageCompany; merges BSM accounts via `getAccountByCompanyId` into questionnaire banks when BSM enabled.
  - `POST /companies/:companyId/get-tableau-token` — auth; `POST` to `config.sleekDashboard.baseUrl/trusted` with username/siteName; fallback `tableauNullToken` on failure.
  - On subscription flows, `companyUserService.sendAccountingOnboardingQuestionnaire` when accounting subscriptions match (referenced in same controller).
- **`services/accounting-questionnaire/accounting-questionnaire-service.js`** — `updateQuestionnaireFieldData` on `AccountingQuestionnaire`; `updateCompanyUserTFN` from tax_information to `User`; `validateBankStatementSource` against `BANK_STATEMENTS_SOURCE`.
- **`services/bank-statement-services.js`** — HTTP client to Sleek BSM: company accounts CRUD and bank list (`/api/bank/company-account/:id`, `/api/bank/account`, `/api/bank`).
- **`services/company-user-service.js`** — `sendAccountingOnboardingQuestionnaire`, `sendAccountingSetupEmail`, questionnaire tokens, permitted pages, mailer templates `ACCOUNTING_ONBOARDING_QUESTIONNAIRE_V2`, links to `sleekWebsite2BaseUrl` accounting setup / onboarding questionnaire; `AccountingQuestionnaire` create/update for recipients; `checkIfUserIsAccountingQuestionnaireContact`.
- **`services/sleek-back-kafka-service.js`** — `syncCodingEngineCompanyData` → `CompanyDataToCEUpdateReceived`; `triggerCompanyDataUpdateTopic`; topic constants including `COMPANY_ACCOUNTING_TOOLS_HAD_UPDATED`, assignee/status topics.
- **`controllers-v2/handlers/workflow/accounting-onboarding.js`** — `startAccountingOnboarding` → `POST` `${sleekWfeBaseUrl}/workflow/api/tasks/accountingonboarding/start/`; `updateAccountingOnboardingStep` maps task names (`complete_questionnaire`, `complete_xero_setup`, `complete_receipt_bank_setup`, `complete_verification`, `complete_onboarding`) to WFE task updates.
- **`modules/sleek-auditor-node/services/auditor-node-service.js`** — `saveAuditLog` POST to `sleekAuditorNode` audit-logs API (V2 pattern used elsewhere in `company-controller` with `buildAuditLogV2`; accounting questionnaire rows use legacy `auditorService`).
