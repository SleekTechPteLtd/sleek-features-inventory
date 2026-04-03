# Maintain invoice customers and products

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Maintain invoice customers and products |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User |
| **Business Outcome** | Teams can reuse customers and line-item products while composing invoices, hide obsolete customers, drop unused catalogue products, and load bank text shown on invoices from stored company bank settings. |
| **Entry Point / Surface** | Sleek App invoicing / invoice composer (API tag `invoice` on acct-coding-engine); exact in-app navigation path Unknown |
| **Short Description** | Authenticated users search invoice customers (email and/or name) and products (name autocomplete) scoped to a company; archive customers or delete products; fetch bank account detail text by company and bank account id for display on invoices. Data lives on the Sleek Receipts Mongo connection. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Company membership** validated via `InvoiceService.validateUserBelongsToCompany` on most routes (see Evidence). **Invoice settings** (`GET invoice-settings/:companyId`) returns `bank_account_id` so the client can call bank-account-details; **sending invoices** creates/updates customers and can upsert products from line items (`InvoiceProductService.saveProductsFromLineItems` — not exposed as standalone HTTP in the listed files). |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | MongoDB `DBConnectionName.SLEEK_RECEIPTS`: `invoicecustomers`, `invoiceproducts` (Mongoose defaults for `InvoiceCustomer` / `InvoiceProduct` schemas); `bank_account_details` (explicit collection on `BankAccountDetails` schema) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `DELETE invoice/company/:companyId/products/:productId` does not call `validateUserBelongsToCompany` in the controller—confirm whether protection is enforced elsewhere or should align with other routes. Swagger text for `find-products` mentions “at least 2 characters” but `FindProductsDto` enforces `MinLength(1)`—which is authoritative for clients? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/invoice/invoice.controller.ts`

- **`GET invoice/bank-account-details/:companyId/:bankAccountId`** — `AuthGuard`; validates user belongs to company; delegates to `invoiceService.getBankAccountDetails`; `400` if not found (`BadRequestException`).
- **`GET invoice/find-customer`** — query `FindCustomersDto`; `AuthGuard`; company validation; `invoiceService.findCustomers`.
- **`GET invoice/find-products`** — query `FindProductsDto`; `AuthGuard`; company validation; `invoiceService.findProducts`. `@ApiOperation` description says at least 2 characters for search; DTO requires at least 1 (see `find-products.dto.ts`).
- **`DELETE invoice/company/:companyId/products/:productId`** — `AuthGuard`; `invoiceService.deleteProductById` (no explicit `validateUserBelongsToCompany` in this handler).
- **`PATCH invoice/company/:companyId/customers/:customerId/archive`** — `AuthGuard`; company validation; `invoiceService.archiveInvoiceCustomerById`.

### `src/invoice/services/invoice-customer.service.ts`

- **Model**: `@InjectModel(InvoiceCustomer.name, DBConnectionName.SLEEK_RECEIPTS)`.
- **`findCustomers`**: `company_id` + `is_archived` not true; optional case-insensitive regex on `email` and `name` (`escapeRegExp`); `.limit(findCustomerDto.limit)`; `.lean()`.
- **`archiveInvoiceCustomerById`**: `findByIdAndUpdate` sets `is_archived: true`; `NotFoundException` / `InternalServerErrorException` on failure paths.

### `src/invoice/services/invoice-product.service.ts`

- **Model**: `@InjectModel(InvoiceProduct.name, DBConnectionName.SLEEK_RECEIPTS)`.
- **`findProducts`**: filters by `company_id` and case-insensitive regex on `name`; sort by `name` ascending; limit.
- **`deleteProductById`**: `findOneAndDelete` matching `company_id` and `_id`; `NotFoundException` if missing.
- **`saveProductsFromLineItems`** (downstream of invoicing): `bulkWrite` upsert by `company_id` + `name`, updates `unit_price` and `updated_by` — keeps product catalogue in sync when invoices are saved (not a direct HTTP entry in the listed controller excerpt).

### `src/invoice/services/bank-account-details.service.ts`

- **Model**: `@InjectModel(BankAccountDetails.name, DBConnectionName.SLEEK_RECEIPTS)`.
- **`getBankAccountDetails`**: `findOne` by `company_id` and `bank_account_id`; returns `null` on error (controller maps missing row to `400`).
- **`upsertBankDetails` / `ensureBankAccountDetails`**: `findOneAndUpdate` with upsert for `bank_account_details` string payload — used elsewhere when bank copy is ensured; not directly wired to the HTTP handler in the files above.

### Schemas

- **`invoice-customer.schema.ts`**: `email`, `company_id`, optional address fields, `is_archived`, `updated_by`; text indexes for search.
- **`invoice-product.schema.ts`**: `name`, `unit_price`, `company_id`; unique index on `(name, company_id)`.
- **`bank_account_details.schema.ts`**: `@Schema({ collection: 'bank_account_details' })` — `company_id`, `bank_account_id`, `bank_account_details` string.
