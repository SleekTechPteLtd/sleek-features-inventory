# Manually Trigger Subscription Renewal Charge

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manually Trigger Subscription Renewal Charge |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Billing Super Admin, Billing Operations Admin, Sales Admin |
| **Business Outcome** | Enables billing and sales admins to force an immediate auto-renewal charge for a company's subscriptions outside the normal scheduled window, ensuring revenue collection when the standard attempt-date guards would otherwise block it. |
| **Entry Point / Surface** | Internal admin API — `POST /subscription-auto-renewal/trigger-manual-auto-renewal-charge` (accessed via admin tooling or direct API call) |
| **Short Description** | Admins POST a `companyId` to force a renewal charge for that company's auto-renewable subscriptions immediately. Unlike the scheduled flow, this bypasses the attempt-date guard by expanding the eligible window to today + 30 days and writing results to `manualAutoRenewalAttemptedAt` instead of the standard attempt fields. Creates a renewal invoice, a payment token, and charges via Stripe or direct debit; on failure, marks the invoice failed and sends a charge-failure email. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Subscription auto-renewal scheduler (normal scheduled charge), Invoice creation (`InvoiceService.createRenewalInvoiceFromSubscriptionList`), Payment processing (`PaymentServiceV2.payWithPaymentMethod`), PaymentToken lifecycle, Discount allocation (`InvoiceService.handleInvoiceDiscountsAllocation`), Email task queue (`TaskService.createTask` → `renewal_auto_on_charge_failure_manualrequired`) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | customersubscriptions, invoices, paymenttokens, emaillogs |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Is there an admin UI surface for this endpoint, or is it only used via direct API / Postman by ops? The unguarded `trigger-auto-renewal-charge` endpoint also calls the same service method — what prevents accidental double-charges in practice? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller
`src/customer-subscription/controllers/subscription-auto-renewal.controller.ts`

- `POST /subscription-auto-renewal/trigger-manual-auto-renewal-charge` (line 32–37)
- Guards: `@Auth()` + `@GroupAuth(Group.BillingSuperAdmin, Group.BillingOperationsAdmin, Group.SalesAdmin)`
- Calls `triggerAutoRenewalCharge(companyId, isFirstCharge=true, bypassChargeAttempt=true, req.user)`
- Accepts optional `companyId` in request body; omitting it targets all companies.

### Service
`src/customer-subscription/services/subscription-auto-renewal.service.ts`

**`bypassChargeAttempt=true` behaviour (lines 72–99, 359–362):**
- Uses `manualAutoRenewalAttemptedAt` / `manualAutoRenewalAttemptedFailedReason` fields instead of the standard first/second attempt fields.
- Expands the eligible `nextRenewalDate` window to `today → today + 30 days` (vs. a specific future day), effectively ignoring normal scheduling.
- Skips the attempt-date filter entirely — subscriptions that were already attempted are re-eligible.

**Charge flow (lines 406–595):**
1. Groups eligible subscriptions by company.
2. Skips companies in offboarding status.
3. Detects duplicate service codes and short-circuits if found.
4. Checks for in-progress direct-debit invoices to prevent double-charging.
5. Creates renewal invoice via `InvoiceService.createRenewalInvoiceFromSubscriptionList` with `InvoiceOrigin.autoRenewal`.
6. Creates a `PaymentToken` via `PaymentTokenService.createPaymentToken`.
7. Stagger logic: sleeps 60 s between same-user companies to avoid Stripe rate issues.
8. Calls `payAutoRenewalInvoice` which iterates payment methods (primary first), skips expired cards, and attempts Stripe or direct-debit charge.
9. On success: stamps `manualAutoRenewalAttemptedAt`.
10. On failure: sets invoice to `InvoiceStatus.failed`, records error, sends `renewal_auto_on_charge_failure_manualrequired` email task.

### Collections touched
| Collection | Operations |
|---|---|
| `customersubscriptions` | find (eligible filter), updateMany (stamp attempt date / failure reason) |
| `invoices` | find (in-progress DD check), create (renewal invoice), update (status, errors) |
| `paymenttokens` | create, update (FAILED status + error) |
| `emaillogs` | written by downstream email task (audited via `EmailLogsRepository`) |

### External integrations
- **Stripe** — card charges via `PaymentServiceV2.payWithPaymentMethod` (`PaymentType.auto_renewal`)
- **Direct Debit** — handled by the same payment service; in-progress state tracked via `InvoiceStatus.ddInProgress`
