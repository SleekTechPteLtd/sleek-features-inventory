# Trigger Manual Subscription Renewal

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Trigger Manual Subscription Renewal |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Billing Ops) |
| **Business Outcome** | Lets billing operators unblock companies whose subscriptions could not renew automatically by generating a fresh renewal invoice on demand, clearing stale draft invoices and active payment tokens in the process. |
| **Entry Point / Surface** | Sleek Billings Admin App > Invoices > Manual Renewal (API: `POST /invoices/manual-renewal`) |
| **Short Description** | Accepts a company ID, a list of subscriptions, and an invoice origin, then creates a "Manual Renewal" invoice in MongoDB and syncs it to Xero. Before creating, it purges any existing draft manual-renewal invoices and active manual-renewal payment tokens for the company to avoid duplication. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Auto-renewal pipeline (this is the manual fallback); Xero invoice sync (`XeroService.updateOrCreateInvoice`); `InvoiceItemCodeSwapService` (item code/price resolution); `CompanyService` (company details); `CompanyUserService` (company admin lookup); Payment token lifecycle (`PaymentTokenRepository`) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `invoices`, `paymenttokens` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which frontend surface calls this endpoint (CLM admin, billing ops tool, or direct API)? Is there a role restriction beyond `@Auth()` — no `@GroupAuth` guard is present, so any authenticated user can call it; is that intentional? Which markets/jurisdictions are covered? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/invoice/controllers/invoice.controller.ts` — `POST /invoices/manual-renewal` handler (lines 155–168)
- `src/invoice/services/invoice.service.ts` — `createRenewalInvoiceFromSubscriptionList` (lines 655–730)
- `src/invoice/dtos/manual-renewal.request.dto.ts` — request shape

### HTTP surface
```
POST /invoices/manual-renewal
Guard: @Auth()   (no @GroupAuth restriction)
```

### Request DTO (`ManualRenewalRequestDto`)
| Field | Type | Notes |
|---|---|---|
| `companyId` | `MongoId` | Target company |
| `subscriptions` | `CustomerSubscription[]` (min 1) | Subscriptions to renew |
| `invoiceOrigin` | `InvoiceOrigin` enum | e.g. `manualRenewal` |

### Controller handler
```ts
// invoice.controller.ts:155–168
@Post('manual-renewal')
@Auth()
async manualRenewal(@Body() payload: ManualRenewalRequestDto, @Req() req: ExtendedRequest) {
  return this.invoiceService.createRenewalInvoiceFromSubscriptionList(
    payload.companyId,
    payload.subscriptions,
    payload.invoiceOrigin,
    req.user,
  );
}
```

### Service logic (lines 655–730)
1. Fetches company details and company users; derives `companyAdmin`.
2. For each subscription, resolves item details via `InvoiceItemCodeSwapService.getResolvedInvoiceItemDetails`; falls back to subscription service fields if no swap found.
3. When `invoiceOrigin === InvoiceOrigin.manualRenewal`:
   - Deletes draft invoices matching `{ companyId, status: draft, invoiceOrigin: manualRenewal }`.
   - Deletes active payment tokens matching `{ companyId, status: ACTIVE, paymentOrigin: MANUAL_RENEWAL }`.
   - Sets invoice title to `"Manual Renewal - {company.name}"`.
   - Assigns `userId` from `reqUser._id` (the operator's identity).
4. Calls `updateOrCreateInvoice` → creates invoice in MongoDB with `status: draft`, then syncs to Xero via `XeroService.updateOrCreateInvoice`.

### Collections written
| Collection | Operation |
|---|---|
| `invoices` | `deleteMany` (clears stale drafts), `create` (new renewal invoice) |
| `paymenttokens` | `deleteMany` (clears stale ACTIVE manual-renewal tokens) |

### External systems
- **Xero** — renewal invoice is created/updated in Xero after the internal record is persisted (`xeroService.updateOrCreateInvoice`).

### Key enum values
```ts
InvoiceOrigin.manualRenewal = 'manualRenewal'  // invoice.schema.ts:61
InvoiceStatus.draft = 'draft'                   // invoice.schema.ts:35
PaymentTokenStatus.ACTIVE                        // payment-token/dto/create-payment-token.dto.ts
PaymentOrigin.MANUAL_RENEWAL                     // payment-token/dto/create-payment-token.dto.ts
```
