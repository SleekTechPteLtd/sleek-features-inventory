# Void External Invoice

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Void External Invoice |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Allows operators to cancel a Xero invoice that should no longer be collected, and automatically reverts any pending subscription upgrade tied to that invoice so the client's subscription state stays consistent. |
| **Entry Point / Surface** | Internal operator API — `PUT /external-invoices/:xeroInvoiceId/void` (app-origin header selects main vs manage-service client) |
| **Short Description** | Marks the specified Xero invoice as VOIDED via the Xero API. If the invoice was generated from an auto-upgrade flow, also sets the linked customer subscription's upgrade status to `cancelledVoided` and clears its auto-charge date. |
| **Variants / Markets** | SG, HK (inferred from `ClientType.main` / `ClientType.manageService` split; exact market mapping unknown) |
| **Dependencies / Related Flows** | Xero (external invoice lifecycle); Customer Subscription upgrade flow (`autoUpgrade` invoice origin); Audit Logs service |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `invoices`, `customersubscriptions`, `auditlogs` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which operator roles/surfaces call this endpoint in practice (admin panel, internal script, CS tooling)? Does voiding also trigger any downstream Kafka events or notifications to the client? Is there a guard beyond `@Auth()` (e.g. role check)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `src/external-invoice/external-invoice.controller.ts`

- `PUT /external-invoices/:id/void` protected by `@Auth()` decorator.
- Reads `app-origin` header → `getClientType()` → resolves to `ClientType.main` or `ClientType.manageService`.
- Delegates to `ExternalInvoiceService.voidExternalInvoice(id, clientType)`.

### Service — `src/external-invoice/external-invoice.service.ts` (`voidExternalInvoice`, line 102)

1. `xeroService.init({ clientType })` — selects the correct Xero tenant/credentials.
2. `xeroService.updateInvoice(invoiceId, { status: XeroInvoice.StatusEnum.VOIDED })` — issues a PATCH to the Xero Accounting API setting the invoice status to `VOIDED`.
3. Throws `NotFoundException` if Xero returns null (invoice not found in Xero).
4. `invoiceRepository.findOne({ externalId: invoiceId })` — looks up the matching internal invoice.
5. If `internalInvoice.invoiceOrigin === InvoiceOrigin.autoUpgrade`, calls `invoiceService.cancelSubscriptionUpgradeWhenInvoiceVoided(internalInvoice)`.

### `cancelSubscriptionUpgradeWhenInvoiceVoided` — `src/invoice/services/invoice.service.ts` (line 2678)

- `customerSubscriptionRepository.updateOne({ upgradeInvoiceId: invoice._id }, { upgradeStatus: UpgradeStatus.cancelledVoided })` — marks the pending upgrade as voided-cancelled.
- If `invoice.autoChargeDate` is set, clears it via `invoiceRepository.updateById`.
- Emits an audit log entry: `"cancelled subscription upgrade due to invoice voided"`.

### Xero Integration — `src/xero/services/xero.service.ts` (`updateInvoice`, line 706)

- Calls `xeroClient.accountingApi.updateInvoice(tenantId, invoiceId, invoices)` using the `xero-node` SDK.
- Two tenants supported: `XERO_TENANT_ID_MAIN` and `XERO_TENANT_ID_MANAGE_SERVICE`.

### Module — `src/external-invoice/external-invoice.service.module.ts`

- Registers `Invoice` model against `SleekPaymentDB` (MongoDB).
- Imports `InvoiceServiceModule`, `XeroServiceModule`, `CustomerSubscriptionService`.
