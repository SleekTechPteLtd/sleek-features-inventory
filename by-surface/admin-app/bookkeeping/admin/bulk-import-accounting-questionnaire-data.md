# Bulk import accounting questionnaire data

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Bulk import accounting questionnaire data |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Backfill or migrate accounting onboarding questionnaire answers from CSV files so client companies have correct bookkeeping setup data without manual re-entry. |
| **Entry Point / Surface** | Admin API: `POST /v2/admin/import-accounting-questionnaire-answers` (structured export-style CSV) and `POST /v2/admin/migration-hk-data-accounting-questionnaire` (Hong Kong migration CSV with human-readable column headers); both require authenticated users with `companies` full access. |
| **Short Description** | **Import answers** parses a fixed-column CSV (skip header row), validates company, user, and company–user linkage, then creates or updates `AccountingQuestionnaire` documents with normalized booleans, dates, currencies, and tenant-defined onboarding option values; returns per-row new, updated, and rejected records. **HK migration** maps a separate CSV layout (company name match, case-insensitive) to the same questionnaire model, creating or updating questionnaires for matched companies and returning saved documents. |
| **Variants / Markets** | SG (import path references ACRA, GST, IRAS-oriented fields and tenant onboarding options), HK (migration path and column mapping for HK-style exports) |
| **Dependencies / Related Flows** | Tenant config `onboarding_meta.accounting_onboarding_workflow` (feature gate and option lists for `accounting_software`, `method_to_invoice_clients`, `invoices_issued_per_month`, etc.); shared currency lists (`utils/currencies`, `utils/secondary-currencies`); accounting onboarding workflow elsewhere in product; internal company/questionnaire flows that read `AccountingQuestionnaire` |
| **Service / Repository** | sleek-back |
| **DB - Collections** | companies, users, companyusers, accountingquestionnaires |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether a dedicated admin UI calls these endpoints or usage is primarily scripts/Postman; HK migration skips unmatched company names without a rejection list; verify HK `getBooleanValueFromContext` semantics (truthy and falsy tokens both yield JavaScript `true` due to `||` chain—may be unintended). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router** (`controllers-v2/admin.js`): `POST /import-accounting-questionnaire-answers` — `userService.authMiddleware`, `accessControlService.can("companies", "full")`, `multer` single file `file`; `POST /migration-hk-data-accounting-questionnaire` — same auth and upload. Mounted under `/v2/admin` in `app-router.js`.
- **Import handler** (`importAccountingQuestionnaireCSV.js`): Returns `403` if `tenant.general.onboarding_meta.accounting_onboarding_workflow.enabled` is falsy; validates CSV type `text/csv`; uses `VALID_CSV_HEADERS` with `skipLines: 1`; loads `Company` by `record.company`, `User` by `record.user`, `CompanyUser` for pair; `AccountingQuestionnaire.findOne({ company })` then `buildAndSaveQuestionnaireData` (create or update) with `status` default `IN PROGRESS`; file fields in CSV are not persisted (commented “not included in this sprint”). Response: `{ newRecords, updatedRecords, rejectedRecords }`.
- **HK migration handler** (`migrationHKDataAccountingQuestionnaireCSV.js`): No accounting-onboarding feature flag; `csv()` without fixed headers; `csvHeaderMapping` from English column labels to internal fields; `Company.findOne({ name: { $regex: record.name, $options: 'i' } })` — unmatched companies skipped; `AccountingQuestionnaire.findOne({ company })` then `buildQuestionnaire` sets `customer_finance_contact` from first/last name, maps onboarding dropdowns via tenant `issued_sales_invoices_options`, persists `webinar_prompted`; response `{ questionnaires }`.
- **Schemas**: `schemas/company`, `schemas/user`, `schemas/company-user`, `schemas/accounting-questionnaire` (Mongoose model `AccountingQuestionnaire`).
- **Tests**: `tests/controllers-v2/admin/import-accounting-questionnaire-csv/import.js`, `tests/controllers-v2/admin/accounting-questionnaire/migration-hk-data-accounting-questionnaire.js`.
