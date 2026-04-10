# Manage Credit Notes

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Credit Notes |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (BillingSuperAdmin, BillingOperationsAdmin for approval) |
| **Business Outcome** | Allow operations teams to issue, track, and reconcile credit refunds against invoices, ensuring customers receive accurate refunds via cash or credit balance while keeping the accounting system (Xero) in sync. |
| **Entry Point / Surface** | CLM Ops > Invoices > Credit Notes |
| **Short Description** | Operations users create and update draft credit notes linked to an invoice, approve them (pushing to Xero), configure refund payment method details (bank transfer, Stripe, etc.), and mark them as paid once Xero confirms settlement. On payment, credit balances are refunded and any downgrade invoices are automatically generated. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero (external credit note sync), Credit Balance (refund on payment), CustomerSubscriptionService (subscriptions updated on credit note payment), Downgrade Invoice flow (auto-generated when credit note type is `downgrade`), AuditLogs (change tracking), DataStreamerService (PaymentDoneEvent), FileUploadService / S3 (PDF storage) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | invoices |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets are supported? No explicit market/region filtering found in credit note logic. Is the entry point a specific CLM ops screen or the general invoices module? What triggers a `downgrade` credit note type vs. a standard refund? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller endpoints (`invoice/controllers/invoice.controller.ts`)

| Method | Route | Guard | Purpose |
|---|---|---|---|
| `POST` | `/invoices/credit-note` | `@Auth()` | Create or update a draft credit note |
| `PUT` | `/invoices/credit-note/:id/mark-as-paid` | `@Auth()` | Mark credit note as paid after Xero confirms |
| `PUT` | `/invoices/credit-note/:id/payment-method` | `@Auth()` | Update refund payment method details |
| `POST` | `/invoices/credit-note/:id/approve` | `@Auth()` + `@GroupAuth(BillingSuperAdmin, BillingOperationsAdmin)` | Approve credit note and push to Xero |
| `GET` | `/invoices/:id/external-url` | `@Auth()` | Retrieve signed PDF URL for a credit note |

### Service methods (`invoice/services/invoice.service.ts`)

- `updateOrCreateCreditNote` (line 1285) — creates or updates credit note; conditionally syncs to Xero via `isCreateXeroCreditNote` flag; calls `markCreditNoteAsPaid` inline if status is already `paid`
- `approveCreditNote` (line 2701) — restricted to BillingSuperAdmin/BillingOperationsAdmin; pushes credit note to Xero, sets `externalId` / `externalNumber`, records `submittedBy`
- `markCreditNoteAsPaid` (line 1132) — verifies PAID status in Xero; triggers `createDowngradeInvoiceFromCreditNote` for downgrade credit notes; calls `refundCreditBalanceByCreditNote`; calls `customerSubscriptionService.createCustomerSubscriptionsFromCreditNote`
- `updateCreditNotePaymentMethod` (line 1205) — updates `refundPaymentMethodDetails` (bankName, accountNumber, swiftCode, ibanNumber, stripePaymentIntentId, etc.); blocked if already paid
- `transformDataToInternalCreditNote` (line 1009) — calculates `creditNoteCreditBalanceAmount`, `creditNoteItemAmount`, line-item descriptions
- `transformDataToXeroCreditNote` (line 567) — maps internal model to Xero CreditNote payload
- `getCreditNoteSignedPdfUrl` (line 1101) — fetches PDF from S3 or pulls from Xero and caches to S3
- `refundCreditBalanceByCreditNote` (line 2209) — adds credit balance refund to company wallet
- `refundCreditBalanceByDowngradedPrice` (line 2179) — calculates and issues credit balance for downgraded services
- `createDowngradeInvoiceFromCreditNote` (line 732) — builds a downgrade invoice from credit note items after payment is confirmed
- `checkCreditNoteChanged` (line 1429) — diff check to avoid redundant Xero API calls on update

### Schema (`invoice/models/invoice.schema.ts`)

- Collection: `invoices` (Mongoose default for `Invoice` class)
- Relevant fields: `type` (`creditNote`), `creditNoteType` (`downgrade`), `status` (draft → submitted/authorised → paid/voided), `linkedInvoice`, `externalId`, `externalNumber`, `refundPaymentMethodDetails`, `submittedBy`, `issueDate`, `paidAt`, `items[].creditNoteData`

### DTO (`invoice/dtos/update-or-create-invoice.request.dto.ts`, line 126)

`UpdateOrCreateCreditNoteRequestDto` extends the invoice DTO with: `creditNoteId`, `linkedInvoice` (required), `zendeskUrl`, `bankAccountDetails`, `refundPaymentMethodDetails`

### Audit trail

All credit note mutations (create, approve, mark-as-paid, update-payment-method, void) call `auditLogsService.addAuditLog` with `text`, `tags`, `companyId`, and `newValue`.
