# Invoice customers and manage delivery

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Invoice customers and manage delivery |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Operations User |
| **Business Outcome** | Businesses can issue numbered sales invoices, produce professional PDFs, optionally collect payment via Stripe, record documents in bookkeeping, and reach customers by email—including corrections like reassigning the billed customer or resending from an existing document. |
| **Entry Point / Surface** | Sleek App > invoicing / sales invoice flows (consumer of API); API surface `invoice` (acct-coding-engine) |
| **Short Description** | Generates the next invoice number from prior sales invoices, renders PDFs with PDFMake (logo, bank details, optional “Pay now” Stripe link), uploads PDFs to S3, creates `SALES_INVOICE` documents with ledger/category context, publishes them, and emails customers via the transactional mailer. Supports preview-only PDF download, resend by document id(s), assigning an invoice customer to a document, and supporting data APIs for customers, products, bank details, and saved invoice settings. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Document** module (`publishDocument`, `getDocumentById`) for publish and lifecycle; **invoice-payments** (`InvoicePaymentsService.getInvoicePaymentLink`) for Stripe payment links when `stripeEnabled`; **S3** for PDF storage and logo retrieval; **Mailer** (`EMAIL_TEMPLATES.INVOICE.SEND_EMAIL_TO_BUYER`); **COA** (default Sales category); **company** service for company context; **SleekBack** (`getCompanyUsersFromSleekBack`) for membership checks; **currency** conversion helpers for functional vs bank-account currency; invoice sub-services for customers, products, users acknowledgement, settings, bank-account-details. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (Document — sales invoices, file metadata, `payment_link`, `email_status`); `mlfeedbackschemas` (Feedback — created on manual invoice); `bank_account_details`; Mongoose default names for invoice models on `SLEEK_RECEIPTS`: `invoicecustomers`, `invoiceproducts`, `invoiceusers`, `invoicesettings`; **Company** on `CODING_ENGINE` connection (reads for company context). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `sendEmailByDocumentId` passes `customer.email` as `senderEmail`/`fromEmail` to `sendInvoiceToCustomerByEmail`, whereas the primary send path uses the authenticated user’s email—confirm intended sender identity for resends. Exact in-app navigation labels may differ by product. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/invoice/invoice.controller.ts`

- **Auth**: All routes use `AuthGuard` (authenticated Sleek users with company membership enforced in service).
- **Invoice number**: `GET invoice/generate-invoice-number/:companyId` → `generateInvoiceNumber`.
- **PDF preview / download**: `POST invoice/generate-invoice-pdf/:companyId` — returns `application/pdf` attachment with encoded filename from `getInvoiceName`.
- **Send to customer**: `POST invoice/send-to-customer/:companyId` — validates payload, optional `getInvoicePaymentLink` when `stripeEnabled`, PDF generation with link, S3 upload, `createInvoice`, `publish`, `sendInvoiceToCustomerByEmail`, `processPostInvoiceCreationTasks` (async bank details, customer update, product save).
- **Supporting reads**: `GET invoice/bank-account-details/:companyId/:bankAccountId`; `GET invoice/find-customer`; `GET invoice/find-products`; `DELETE` / `PATCH` archive for products and customers.
- **Settings & onboarding**: `POST invoice/acknowledge-invoicing-feature`; `GET invoice/invoice-user`; `GET` / `POST invoice/invoice-settings/:companyId` (multipart logo on save).
- **Resend / assign**: `POST invoice/send-email-by-document-id/:documentId`; `POST invoice/send-email-by-document-ids` (body `documentIds`); `POST invoice/assign-customer-to-document/:documentId` with `FindCustomersDto`.

### `src/invoice/invoice.service.ts`

- **Invoice numbering**: Latest `document_type: SALES_INVOICE` with `document_reference`, increment via `TRAILING_NUMBER_REGEX` / `incrementInvoiceNumber`; uniqueness check `isValidInvoiceNumber`.
- **PDF**: `generateInvoicePdfWithPDFmake` — pdfmake, invoice settings for logo (S3 base64) and footer; optional Stripe link rendered as “Pay Now” with external-link icon.
- **Persistence**: `createInvoiceDocument` — `documentModel.create` with revenue ledger, line items from COA sales category, `invoice_customer_id`, `payment_link` / `payment_status` when Stripe; `feedbackModel.create` for manual flow.
- **Email**: `sendInvoiceToCustomerByEmail` — `mailerService.sendEmail` with PDF attachment; `updateDocumentEmailStatus` on success/failure.
- **Publish**: `publish` → `documentService.publishDocument`.
- **Resend**: `sendEmailByDocumentId` rebuilds `InvoicePayloadDto` from document + invoice customer, loads PDF from S3, calls `sendInvoiceToCustomerByEmail`.
- **Assign customer**: `updateCustomerForDocument` — `findOrCreateInvoiceCustomer` then `documentModel.findByIdAndUpdate` setting `invoice_customer_id`.
- **Membership**: `isUserBelongsToCompany` via `sleekBackService.getCompanyUsersFromSleekBack`.

### `src/invoice/dto/invoice.dto.ts`

- **Payload**: `InvoicePayloadDto` — invoice number, dates `DD-MM-YYYY`, customer `user_name` / `user_email`, line items with decimal validation via service, `stripeEnabled`, optional `created_by_user_*` for payment flows, `receipt_user_id`, optional `bank_account` / `bank_details`.

### `src/invoice/invoice.module.ts`

- Registers Mongoose models on `DBConnectionName.SLEEK_RECEIPTS` (Document, Feedback, BankAccountDetails, InvoiceCustomer, InvoiceProduct, InvoiceUsers, InvoiceSettings) and Company on `CODING_ENGINE`; imports `DocumentModule`, `InvoicePaymentsModule`, `CompanyModule`, `CoaModule`, etc.
