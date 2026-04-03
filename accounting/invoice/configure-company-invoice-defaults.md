# Configure company invoice defaults

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Configure company invoice defaults |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Admin |
| **Business Outcome** | Each company can define how invoices look and what payment and identity information appears, so outgoing PDFs and previews stay consistent with branding and bank instructions. |
| **Entry Point / Surface** | Sleek App > Invoicing / invoice settings (company-scoped); API surface `invoice` (`acct-coding-engine`) |
| **Short Description** | Authenticated users load and save per-company invoice defaults: optional logo upload to object storage, default payment terms (due in days), linked bank account with optional inline details, and footer-related fields (visibility plus website, phone, address, primary business identifier). Settings feed PDF generation and preview (logo as base64; bank line resolved from linked account when present). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Amazon S3** (`S3Service` from feedback module) for logo upload, delete, and base64 fetch for preview/PDF; **Bank account details** (`BankAccountDetailsService`) upsert/read when `bank_account_id` is supplied; **Invoice PDF pipeline** (`InvoiceService.generateInvoicePdfWithPDFmake`, `buildFooterContent`) consumes `getInvoiceSettingsWithBankDetails`; separate `GET invoice/bank-account-details/:companyId/:bankAccountId` for full bank row. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `invoicesettings` (Mongoose model `InvoiceSettings`, connection `SLEEK_RECEIPTS`); `bank_account_details` when saving linked bank account |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Controller/Swagger copy refers to a `footer` field; the persisted model uses `show_footer` plus structured fields (`website`, `phone`, `address`, `primary_identifier`, `primary_identifier_type`) rather than one free-text footer—confirm product copy vs API. Exact in-app navigation labels may differ by product skin. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/invoice/invoice.controller.ts`

- **Auth**: `AuthGuard` on settings routes; `validateUserBelongsToCompany` before read/write.
- **GET `invoice/invoice-settings/:companyId`**: `getInvoiceSettings` → `invoiceService.getInvoiceSettingsForPreview(companyId)`. `@ApiOperation` documents `bank_account_id`, `logo_preview_url`, `show_footer`, and notes frontend should load bank details separately by id.
- **POST `invoice/invoice-settings/:companyId`**: `FileInterceptor('logo', logoMulterOptions)`, `@ApiConsumes('multipart/form-data')`, body `InvoiceSettingsDto`, optional `UploadedFile` logo → `invoiceService.upsertInvoiceSettings(userId, companyId, dto, logo)`.

### `src/invoice/services/invoice-settings.service.ts`

- **MongoDB**: `InjectModel(InvoiceSettings.name, DBConnectionName.SLEEK_RECEIPTS)`; `findOne` / `findOneAndUpdate` by `company_id`.
- **Logo**: `uploadInvoiceLogo` → `S3Service.uploadFileOnS3` under `invoice-logos/{companyId}/logo/invoice-logo.{ext}`; `remove_logo === 'true'` without new file deletes prior logo via `deleteFileFromS3URL`.
- **Bank**: If `bank_account_id` in DTO, `bankAccountDetailsService.upsertBankDetails(companyId, id, bank_account_details)`.
- **Preview**: `getInvoiceSettingsForPreview` returns `logo_preview_url` from `getFileBase64StringFromS3URL`, plus ids, payment due days, footer flags and contact fields, and `bank_account_details` string from stored document.
- **PDF path**: `getInvoiceSettingsWithBankDetails` merges bank line from `BankAccountDetails` when `bank_account_id` is set.

### `src/invoice/dto/invoice-settings.dto.ts`

- Fields: `bank_account_id`, `payment_due_date`, `bank_account_details`, `remove_logo`, `show_footer` (multipart boolean via `Transform`), `website`, `phone`, `address`, `primary_identifier`, `primary_identifier_type` (length-validated strings).

### `src/invoice/config/logo-multer.config.ts`

- **Limits**: `LOGO_UPLOAD_LIMIT` (2MB from `invoice.constants.ts`).
- **Types**: `ALLOWED_LOGO_MIME_TYPES` / `ALLOWED_LOGO_EXTENSIONS` (jpeg, jpg, png); invalid uploads get `HttpException` 400.

### `src/invoice/models/invoice-settings.schema.ts`

- **Index**: `{ company_id: 1 }`.
- **Stored fields** include `logo_uri`, `logo_url`, `payment_due_date`, `bank_account_id`, `bank_account_details`, `show_footer`, contact and identifier fields, `updated_by`, timestamps.

### `src/invoice/invoice.service.ts` (consumption)

- `generateInvoicePdfWithPDFmake` calls `getInvoiceSettingsWithBankDetails` for logo base64 and passes settings to `buildFooterContent` when `show_footer` is true (website, phone, address, labeled primary identifier).
