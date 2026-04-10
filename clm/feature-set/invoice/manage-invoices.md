# Manage Invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin for restricted actions) |
| **Business Outcome** | Gives operations teams full control over the invoice and credit note lifecycle — creating, editing, voiding, and deleting records — while keeping Sleek's internal state in sync with Xero for accurate billing. |
| **Entry Point / Surface** | Sleek Admin > CLM > Invoices |
| **Short Description** | Operations users can browse, view, create, update, delete (soft or hard), and void invoices and credit notes across their full lifecycle. Invoices are synced bidirectionally with Xero on creation and status changes; reconciliation and credit-note approval are gated behind elevated role permissions. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Xero (external invoice/credit-note sync), Stripe (payment processing), Credit Balance service, Coupon service, Customer Subscription service, Payment Token service, Audit Logs service, Queue service (cleanup jobs), Company service, User service |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | invoices (primary), paymenttokens (aggregation lookup), companies (aggregation lookup); indirectly: coupons, couponusages, customersubscriptions, paymentmethods |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. `GET :id/url` has no `@Auth()` guard — is this intentional for public invoice PDF redirects or a missing guard? 2. `POST apply-coupon-and-credit-balance` also lacks `@Auth()` — is it called internally only? 3. Is there a customer-facing invoice portal surface beyond the admin panel? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `src/invoice/controllers/invoice.controller.ts`

| Method | Route | Guard | Purpose |
|---|---|---|---|
| GET | `/invoices` | `@Auth()` | Paginated invoice list with filters |
| GET | `/invoices/company/:companyId` | `@Auth()` | All invoices for a specific company (limit 1000) |
| GET | `/invoices/:id` | `@Auth()` | Single invoice detail |
| GET | `/invoices/:id/url` | none | Redirect to external (Xero) invoice PDF URL |
| GET | `/invoices/:id/external-url` | `@Auth()` | Return external URL for invoice or credit note |
| POST | `/invoices` | `@Auth()` | Create or update an invoice |
| DELETE | `/invoices/:id` | `@Auth()` | Soft-delete (or restore/hard-delete) an invoice |
| POST | `/invoices/:id/void` | `@Auth()` | Void invoice or credit note (syncs to Xero) |
| POST | `/invoices/credit-note` | `@Auth()` | Create or update a credit note |
| PUT | `/invoices/credit-note/:id/mark-as-paid` | `@Auth()` | Mark a credit note as paid |
| PUT | `/invoices/credit-note/:id/payment-method` | `@Auth()` | Update refund payment method on a credit note |
| POST | `/invoices/credit-note/:id/approve` | `@Auth()` + `BillingSuperAdmin, BillingOperationsAdmin` | Approve a credit note |
| POST | `/invoices/manual-renewal` | `@Auth()` | Create renewal invoice from subscription list |
| POST | `/invoices/reconcile` | `@Auth()` + `BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin` | Reconcile invoice from webhook |
| POST | `/invoices/consider-as-reconciled` | `@Auth()` + `BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin` | Mark webhook as reconciled without processing |
| POST | `/invoices/apply-coupon-and-credit-balance` | none | Apply coupon and credit balance to invoice |
| POST | `/invoices/customer-request` | `@Auth()` | Create a customer-requested invoice |
| POST | `/invoices/auto-upgrade` | `@Auth()` | Create auto-upgrade invoice |
| POST | `/invoices/auto-upgrade/:subscriptionId/cancel` | `@Auth()` | Cancel a pending auto-upgrade |
| POST | `/invoices/clean-up/trigger` | `@Auth()` | Enqueue invoice cleanup job via QueueService |

### Service — `src/invoice/services/invoice.service.ts`

Key method highlights:

- **`updateOrCreateInvoice`** (line 837): Creates draft invoice or updates existing one; blocks edits to paid invoices; syncs to Xero when `isCreateXeroInvoice` flag is set; writes audit log entry.
- **`deleteInvoice`** (line 265): Supports soft-delete (sets `deleted: true` + `deleteReason`), restore (`revert: true`), and hard-delete (`forceDelete: true` removes document entirely). Logs requesting user.
- **`voidInvoice`** (line 2403): Guards against voiding paid/already-voided/deleted records; voids in Xero first (invoice or credit note), then updates internal status to `voided` with optional `voidReason`.
- **`getInvoiceList`** (line 153): MongoDB aggregation pipeline with optional population of `paymentToken`, `linkedInvoice`, and `companyDetails`.
- **`reconcileInvoice`** (line 1959): Reconciles payment state from incoming Xero webhook; optionally creates subscriptions.
- **`createCustomerRequestInvoice`** (line 2351): Creates ad-hoc invoice from a customer request.
- **`createAutoUpgradeInvoice`** (line 2504): Creates an upgrade invoice for plan changes.
- **`approveCreditNote`** (line 2701): Approval workflow for credit notes, restricted to BillingSuperAdmin/BillingOperationsAdmin.

External system calls: `XeroService.updateInvoice`, `XeroService.updateOrCreateCreditNote`, `XeroService.updateOrCreateContact`, `StripeService`, `CreditBalanceService`, `PaymentTokenService`, `AuditLogsService.addAuditLog`, `QueueService.add('triggerInvoiceCleanUp')`.

### Schema — `src/invoice/models/invoice.schema.ts`

Collection: `invoices` (via `SleekPaymentDB` connection — `InvoiceRepository` injects `Invoice` model).

Key fields: `type` (invoice / creditNote / msInvoice / msCreditNote), `status` (draft → submitted → authorised → paid / voided / deleted / failed / ddInProgress), `invoiceOrigin` (paymentRequest, betaOnboarding, autoRenewal, manualRenewal, reconcile, customerRequest, downgrade, autoUpgrade), `externalId` / `externalNumber` (Xero identifiers), `companyId`, `items` (embedded `InvoiceItem[]`), `paymentTokenId` (ref → paymenttokens), `linkedInvoice` (ref → invoices), `creditNoteType`, `createdBy`, `voidReason`, `deleteReason`.

Indexes on: `companyId`, `externalNumber`, `externalId`, `companyId+status+type+title`, `number+migratedFrom`, `createdAt`, `deleted+createdAt`, `invoiceOrigin+status+externalId+createdAt`.

### Repository — `src/invoice/repositories/invoice.repository.ts`

Wraps `BaseRepository<Invoice>` with `SleekPaymentDB` connection. Provides `findById`, `updateById`, `deleteById`, `create`, `aggregateWithPaginationV2`.
