# Mark External Invoice as Paid

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Mark External Invoice as Paid |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Allows operators to manually close an externally-originated invoice as paid, keeping Xero in sync, provisioning the customer's subscriptions, and broadcasting a payment event to downstream systems. |
| **Entry Point / Surface** | Internal ops interface > Invoices > External Invoice actions (PUT `/external-invoices/:id/mark-as-paid`) |
| **Short Description** | Operator triggers a paid status update on an external invoice. The system updates Xero, stamps the invoice as paid in MongoDB, creates customer subscriptions from the invoice line items, and publishes a payment-done event. For Xero-webhook-originated calls, coupons and credit balances are also marked as used. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero (mark invoice paid); DataStreamer/Kafka (`PaymentDoneEvent`, `PaymentDoneFromPaymentRequestEvent`); Customer Subscription creation flow; Coupon & Credit Balance usage flow; Auto-upgrade post-payment flow; Audit Logs |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `invoices`, `customersubscriptions` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which UI surface exposes this action to operators — is it the CLM internal dashboard or a separate ops tool? Which markets/entities use external invoices vs. standard invoices? Is the `skipExternalInvoiceAsPaid` path only ever triggered by the Xero webhook (not the manual endpoint)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `external-invoice/external-invoice.controller.ts:25–31`
  - `PUT /external-invoices/:id/mark-as-paid`
  - Protected by `@Auth()` (authenticated operator session)
  - Reads `app-origin` header to determine `clientType` (main vs. secondary Xero org)

### Core orchestration
- `external-invoice/external-invoice.service.ts:32–100` — `ExternalInvoiceService.markExternalInvoiceAsPaid()`
  1. Validates ObjectId format; throws `BadRequestException` on invalid ID
  2. Calls `InvoiceService.getInvoiceDetail(invoiceId)` → reads `invoices` collection
  3. Short-circuits if invoice already paid (when `skipExternalInvoiceAsPaid` is set)
  4. Initialises Xero client via `XeroService.init({ clientType })`
  5. Calls `XeroService.markInvoiceAsPaid(invoice.externalId, invoice.totalAmount, reference)` — skipped when `skipExternalInvoiceAsPaid=true` or `totalAmount === 0`
  6. Updates invoice: `status = paid`, `paidAt = fullyPaidOnDate || now` via `InvoiceService.updateInvoice()` → writes `invoices` collection
  7. Records audit log entry: `AuditLogAction.create` with tags `['invoice', 'invoice-<id>']`
  8. Calls `CustomerSubscriptionService.createCustomerSubscriptionsFromInvoice(updatedInvoice)` — creates subscription records for each `itemId` in invoice line items → writes `customersubscriptions` collection
  9. Calls `InvoiceService.publishPaymentDoneEvent(updatedInvoice)` — publishes `PaymentDoneEvent` (standard) or `PaymentDoneFromPaymentRequestEvent` (payment-request origin) via `DataStreamerService`
  10. If `skipExternalInvoiceAsPaid` (Xero webhook path): also calls `InvoiceService.markCouponAndCreditBalanceAsUsed()`
  11. If `invoiceOrigin === autoUpgrade`: calls `InvoiceService.postPaymentDoneForAutoUpgradeInvoice()`

### Supporting services
- `invoice/services/invoice.service.ts:246–248` — `getInvoiceDetail` reads `invoices` by ID
- `invoice/services/invoice.service.ts:250–260` — `updateInvoice` writes `invoices`
- `invoice/services/invoice.service.ts:2066–2105` — `publishPaymentDoneEvent` routes to the correct Kafka event based on `invoiceOrigin`
- `invoice/services/invoice.service.ts:2341–2345` — `markCouponAndCreditBalanceAsUsed`
- `invoice/services/invoice.service.ts:2667` — `postPaymentDoneForAutoUpgradeInvoice`
- `customer-subscription/services/customer-subscription.service.ts:393–401` — `createCustomerSubscriptionsFromInvoice` iterates `invoice.items`, resolves services, writes `customersubscriptions`

### Schemas / collections
- `invoice/models/invoice.schema.ts` — `Invoice` class → `invoices` collection; `InvoiceStatus.paid`, `InvoiceOrigin` enum
- `customer-subscription/models/customer-subscription.schema.ts` — `CustomerSubscription` class → `customersubscriptions` collection
