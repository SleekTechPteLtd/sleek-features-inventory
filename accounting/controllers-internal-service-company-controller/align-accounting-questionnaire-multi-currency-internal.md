# Align accounting questionnaire multi-currency with bank coverage (internal)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Align accounting questionnaire multi-currency with bank coverage (internal) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (internal services / integrations calling internal-only APIs) |
| **Business Outcome** | Internal systems can read onboarding questionnaire answers and merge **other-currency** lists with currencies implied by linked bank accounts so multi-currency accounting setup stays consistent with actual bank coverage without relying on the customer-facing app for every adjustment. |
| **Entry Point / Surface** | **Internal service API only** (not Sleek App): routes on **`controllers/internal-service/company-controller.js`** behind **`internalServicesMiddleware`** (Basic auth against configured internal secret; optional bypass in non-prod per **`middlewares/internal-services.js`**). Relevant paths: **`GET`** **`/internal/companies/:companyId/accounting-questionnaire-answers`**, **`PUT`** **`/internal/companies/:companyId/accounting-questionnaire/other-currency`**, **`GET`** **`/internal/get-all-banks-in-accounting-questionnaire`**, and optional questionnaire join on **`GET`** **`/internal/findAllCompanies`** via **`include_accounting_questionnaire`**. |
| **Short Description** | **GET** returns the full **`AccountingQuestionnaire`** document for a company (or **`{}`** if missing). **PUT** appends a requested currency to **`other_currency`**, unions it with distinct bank **`currency`** values (excluding the functional currency), deduplicates, and persists via **`updateQuestionnaireFieldData`**. **GET all banks** lists questionnaires that have at least two banks, with company populated, for operational visibility. **`findAllCompanies`** can **`$lookup`** **`accountingquestionnaires`** when the include flag is set. |
| **Variants / Markets** | Unknown (questionnaire schema carries SG/HK/UK-style fields globally; these routes do not branch by market) |
| **Dependencies / Related Flows** | **Upstream** — whichever internal jobs or services call these routes (not named in these files). **Related** — **`accountingQuestionnaireService.updateQuestionnaireFieldData`** also supports **`tax_information`** updates that sync **`User.tax_number`** (not exercised by the other-currency route). **Data model** — **`Company`**, bank rows on the questionnaire. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | **`accountingquestionnaires`** (Mongoose **`AccountingQuestionnaire`**: **`findOne`**, **`find`**, **`findOneAndUpdate`** via service). **`companies`** (aggregate **`$lookup`** from **`findAllCompanies`**; **`populate("company")`** on list-banks). **`users`** — only when **`updateQuestionnaireFieldData`** is called with **`tax_information`** (side path in shared service). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which internal integration(s) call **`other-currency`** and **get-all-banks** in production; whether **`findOneAndUpdate`** with **`returnOriginal: true`** in **`updateQuestionnaireFieldData`** is intended to return the pre-update document to callers. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/internal-service/company-controller.js`

- **`GET /internal/findAllCompanies`** — query **`include_accounting_questionnaire`**; when true, aggregation **`$lookup`** from **`accountingquestionnaires`** on **`company`**, **`$unwind`** with **`preserveNullAndEmptyArrays: true`**.
- **`GET /internal/companies/:companyId/accounting-questionnaire-answers`** — validates **`companyId`** ObjectId; **`AccountingQuestionnaire.findOne({ company: companyId })`**; empty **`{}`** if none else full document JSON.
- **`PUT /internal/companies/:companyId/accounting-questionnaire/other-currency`** — Joi body **`{ other_currency: string }`**; loads questionnaire; builds **`otherCurrency`** array (append new value); **`company_functional_currency`** and **`banks`**; **`nonExistedCurrencies`** from distinct bank currencies excluding functional currency; **`finalOtherCurrencies`** = union of **`otherCurrency`** and **`nonExistedCurrencies`** (deduped with **`Set`**); **`accountingQuestionnaireService.updateQuestionnaireFieldData(companyId, { other_currency: finalOtherCurrencies })`**.
- **`GET /internal/get-all-banks-in-accounting-questionnaire`** — query **`skip`**, **`limit`**, optional **`company_id`**; **`find`** with **`banks.1` exists** (at least two banks); **`populate("company")`**; maps to **`company_id`**, **`company_name`**, **`company_uen`**, **`company_address`**, **`banks`**.

### `services/accounting-questionnaire/accounting-questionnaire-service.js`

- **`updateQuestionnaireFieldData(companyId, setConstructedProperties)`** — optional **`updateCompanyUserTFN`** when **`tax_information`** present; **`AccountingQuestionnaire.findOneAndUpdate`** **`$set`** with **`returnOriginal: true`**.
- **`validateBankStatementSource`** — validates **`bankStatementSource`** against **`BANK_STATEMENTS_SOURCE`** (not invoked by the internal company routes above).

### `schemas/accounting-questionnaire.js`

- Mongoose model **`AccountingQuestionnaire`** — fields used by this capability include **`company`**, **`company_functional_currency`**, **`other_currency`** (**`[String]`**), **`banks`** ( **`currency`**, **`bankStatementSource`**, etc.), plus the broader onboarding questionnaire surface returned by **GET** answers.
