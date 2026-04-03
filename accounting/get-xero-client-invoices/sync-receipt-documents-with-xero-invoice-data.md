# Sync receipt documents with Xero invoice data

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync receipt documents with Xero invoice data |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | After Hubdoc links a receipt to a Xero invoice, Sleek’s document record is updated from live Xero invoice line data so status, amounts, and category lines (account code plus name) match what was posted in Xero—keeping bookkeeping views aligned with the ledger. |
| **Entry Point / Surface** | Backend batch script `src/scripts/get-xero-client-invoices.js` (Mongo connect + `main()`); intended for scheduled or operator execution, not an end-user Sleek App screen. Optional CLI second argument enables resync mode for in-books documents missing categories. |
| **Short Description** | For up to 10 companies per run, resolves Xero tenant id via BigQuery (`xero_tenants` by normalized company name), loads up to 30 document events per company that are Hubdoc-linked (`hubdoc_data.xero_actions_remote_object_id`) and in `processing` (normal) or `in_books` without categories (resync). Calls Xero Accounting API `getInvoices` for those invoice IDs, maps each line’s account code to account name via BigQuery (`xero_accounts` joined to tenant), then persists invoice fields and line-level categories onto `DocumentDetailEvent` via `updateDocumentEventDetailsByDocumentId`, setting status to `in_books`. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | Hubdoc integration supplying `xero_actions_remote_object_id` on document events (`updateDocumentEventHubdocData`); Xero OAuth refresh via `XeroAuthCredential`; Google BigQuery datasets `xero_tenants`, `xero_accounts` (region `asia-southeast1`); downstream UI/list views consuming `DocumentDetailEvent` (`getAllDocumentEventsByCompanyId`, etc.). Related pattern: Coding Engine Xero invoice sync from BigQuery (`getXeroInvoiceByInvoiceId`) is available but this script uses the live Xero API. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (read/update `DocumentDetailEvent`); `xeroauthcredentials` (read/update OAuth token set for Xero client) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Production schedule and alerting for this script are not defined in the repository; whether non-SG Xero orgs rely on the same BigQuery name-matching and company-name normalization is not verified in code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Batch script (`src/scripts/get-xero-client-invoices.js`)

- **`getCompanyDetails` / `getDocumentEvents`:** `DocumentDetailEvent` aggregate/find where `status === PROCESSING`, `hubdoc_data.xero_actions_remote_object_id` present, company name set, not deleted/archived; caps 10 companies and 30 documents per company (`$limit`, `.limit(30)`), sorted by `submission_date`.
- **`getCompanyDetailsResync` / `getDocumentEventsResync`:** same limits but targets `IN_BOOKS` with empty or missing `category` (backward compatibility for older documents).
- **`mapLineItemsWithAccountNames`:** for each Xero line item `AccountCode`, calls `getAccountNameByTenantId` and builds `category_name` as `{AccountCode} - {Name}` plus `AccountName` on the line object.
- **`updateDocumentEventByXeroData`:** `findOne` by `hubdoc_data.xero_actions_remote_object_id === InvoiceID`; merges supplier from existing `hubdoc_data`; calls `updateDocumentEventDetailsByDocumentId` with `status: IN_BOOKS`, `document_type`, dates, reference, currency, totals, `category: mappedLineItems`, etc.
- **`main`:** `initializeXero()`, `authBQ()`, iterates companies; `getTenant(BQInstance, DB_NAME, formatCompanyName(company_name))`; collects `invoiceIDs` from document events; `xero.accountingApi.getInvoices(tenants.xeroTenantId, …, invoiceIDs, …, 1)`; `updateDocumentEventByXeroData`. Per-company errors log Xero response body. `process.argv[2]` selects resync queries.
- **`formatCompanyName`:** uppercases and strips trailing Singapore-style suffixes (`PTE. LTD.`, `PRIVATE LIMITED`, `PTE LTD`, etc.) before BigQuery tenant lookup.

### Xero client (`src/xero/xero-utilities.js`)

- **`initializeXero`:** builds `XeroClient` from env (`XERO_CREDENTIALS`, `XERO_REDIRECT_URI`, `XERO_SCOPES`), loads token from `XeroAuthCredential.findOne()`, refreshes if expired and `updateOne` persists new token set.

### BigQuery (`src/bigquery/bigquery-utilities.js`)

- **`authBQ`:** `BigQuery` with `BQPROJECTID`, `GOOGLE_APPLICATION_CREDENTIALS` / `BQkey.json`, dataset `BQDATASET` → `DB_NAME` for qualified table names.
- **`getTenant`:** `SELECT * FROM …xero_tenants WHERE UPPER(orgName) LIKE "%{companyName}%" ORDER BY createdAt DESC` (first row).
- **`getAccountNameByTenantId`:** join `xero_tenants` and `xero_accounts` on `tenant_id`, filter by tenant `_id` and account `Code`.

### Document updates (`src/services/document-event-service.js`)

- **`updateDocumentEventDetailsByDocumentId`:** validates ObjectId, `computeDocumentEventDetails` (e.g. `converted_total_amount` when `IN_BOOKS`), `validateDuplicateDocuments`, `DocumentDetailEvent.updateOne` with `$set`.
- **`computeDocumentEventDetails`:** for `IN_BOOKS`, derives `converted_total_amount` / `converted_total_tax_amount` from `total_amount`, `total_tax_amount`, and `currency_rate` when present.

### Schema (`src/schemas/document-detail-event.js`)

- **Model `DocumentDetailEvent`:** fields include `status`, `hubdoc_data`, `category` (array/object), monetary and reference fields used by the sync; collection name follows Mongoose default for this model.
