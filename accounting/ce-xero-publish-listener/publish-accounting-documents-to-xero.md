# Publish accounting documents to Xero

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Publish accounting documents to Xero |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Bookkeeping documents that are ready to post in the client’s Xero organisation are created in Xero as authorised invoices, bank transactions, or credit notes in one place, with attachments when supplied, so downstream workflows know the publish succeeded or failed without manual reconciliation. |
| **Entry Point / Surface** | Event-driven: `CEXeroPublishListener` handles inbound domain events on the shared event stream (`@SubscribeEvent(CEXeroInvoiceCreatedEvent.name)`). Not an end-user screen; upstream producers (e.g. Coding Engine) emit publish requests. |
| **Short Description** | On each message, the listener reads `xeroPublishType` and dispatches to `XeroService.createXeroInvoice`, `createXeroBankTransaction`, or `createXeroCreditNote`. Each path resolves the company’s Xero tenant via BigQuery, uses the stored OAuth token set (MongoDB) with `xero-node`, creates an **AUTHORISED** invoice or credit note (or a bank transaction), uploads optional attachments from S3 URIs, then publishes `CEXeroInvoiceDoneEvent` or `CEXeroInvoiceFailedEvent` via `DataStreamerService` with `document_id`, `publish_id`, and Xero IDs or errors. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream** — Kafka/event producers that emit `CEXeroInvoiceCreatedEvent` (payload `DocumentXeroPublish`). **External** — Xero Accounting API (`xero-node`); Google BigQuery `xero_tenants` (company UEN → `xeroTenantId`); AWS S3 for attachment bytes (`AwsS3Service`). **OAuth** — same app-level `XeroAuthToken` store as other Xero flows (`initializeXeroConfig`). **Downstream** — consumers of done/failed publish events on the event stream. **Related** — `accounting/xero-auth/connect-xero-accounting-integration.md` (different repo) for consent/token bootstrap; tenant override in dev/staging via `XERO_TENANT_ID`. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | MongoDB: `xeroauthtokens` (Mongoose model `XeroAuthToken`) — read and update when refreshing OAuth tokens during Xero API calls. No MongoDB document write for the published invoice/bank transaction/credit note payload itself. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Event class is still named `CEXeroInvoiceCreatedEvent` while comments and behaviour suggest a generic “publish created” event; should it be renamed to `CEXeroPublishCreatedEvent`? Listener calls `createXero*` without `await` — is fire-and-forget intentional? Invoices support `fileURIs` (multiple); bank transactions and credit notes only use `fileUri` in code — is parity desired? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/kafka/listeners/ce-xero-publish.listener.ts`

- **`CEXeroPublishListener`**: `@Controller('ce-xero-publish-listener')`, `@SubscribeEvent(CEXeroInvoiceCreatedEvent.name)` → `onCEXeroPublishCreated`
- **Dispatch**: `switch (message.data.xeroPublishType)` — `XeroPublishType.INVOICE` → `createXeroInvoice`, `BANK_TRANSACTION` → `createXeroBankTransaction`, `CREDIT_NOTE` → `createXeroCreditNote`; unsupported type logs error
- Service calls are **not** awaited

### `src/kafka/events/ce-xero-publish-created.event.ts`

- **`CEXeroInvoiceCreatedEvent`**: `extends DomainEvent<DocumentXeroPublish>`

### `src/xero/interface/document.interface.ts`

- **`DocumentXeroPublish`**: `xeroPublishType`, `documentId`, `publishId`, `uen`, `contact`, `lineItems`, `lineAmountTypes`, `invoiceNumber`, dates, `currencyCode`, optional `total`/`totalTax`, `fileUri` / `fileURIs`, `isECReport`; invoice-type fields: `invoiceType`; bank: `bankTransactionType`, `bankAccount`; credit note: `creditNoteType`

### `src/xero/constants/xero.constant.ts`

- **`XeroPublishType`**: `INVOICE`, `BANK_TRANSACTION`, `CREDIT_NOTE`
- Related enums: `XeroInvoiceType`, `XeroBankTransactionType`, `XeroCreditNoteType`, `LineAmountType`

### `src/xero/xero.service.ts` (publish paths)

- **`getCompanyDataFromBQ(uen)`**: BigQuery `xero_tenants` by `orgRegistrationNumber` (UEN) to obtain `xeroTenantId`; dev/staging/sit can override tenant via `XERO_TENANT_ID`
- **`initializeXeroConfig`**: loads `XeroAuthToken` from MongoDB, refreshes token if expired, persists updates
- **`createXeroInvoice`**: `createInvoices` with `status: AUTHORISED`; optional `createInvoiceAttachment` / loop for `fileURIs` (S3 → stream → `createInvoiceAttachmentByFileName`); success → `dataStreamerService.publish(CEXeroInvoiceDoneEvent.name, …)` with `document_id`, `publish_id`, `invoice_id`; auth/validation/other errors → `CEXeroInvoiceFailedEvent` with `errors` array
- **`createXeroBankTransaction`**: `createBankTransactions` (default type `SPEND` if unset); optional `createBankTransactionAttachment`; done/failed events use `invoice_id` field for the Xero `bankTransactionID` string
- **`createXeroCreditNote`**: `createCreditNotes` with `status: AUTHORISED`; optional `createCreditNoteAttachment`; done/failed same pattern as invoice
- **Imports**: `CEXeroInvoiceDoneEvent` from `../kafka/events/ce-xero-publish-done.event.ts`, `CEXeroInvoiceFailedEvent` from `../kafka/events/ce-xero-publish-failed.event.ts`

### `src/kafka/events/ce-xero-publish-done.event.ts` / `ce-xero-publish-failed.event.ts`

- **`CEXeroInvoiceDoneEvent`**: payload `document_id`, `publish_id`, `invoice_id`, optional `isECReport`
- **`CEXeroInvoiceFailedEvent`**: payload `document_id`, `publish_id`, `errors`, optional `isECReport`
