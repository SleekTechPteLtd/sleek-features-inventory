# Manage Auto-Upgrade Billing

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Auto-Upgrade Billing |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Billing Operator) |
| **Business Outcome** | Enables operators to issue and cancel prorated upgrade invoices when a client's subscription plan changes, ensuring accurate billing for plan upgrades. |
| **Entry Point / Surface** | Internal billing API — `POST /invoices/auto-upgrade`, `POST /invoices/auto-upgrade/:subscriptionId/cancel` |
| **Short Description** | Operators create an auto-upgrade invoice to bill a client for a plan upgrade (price delta between current and target service). If a saved payment method is on file, the invoice schedules an automatic charge in 5 days and sends a pre-charge notification email; otherwise a payment link is emailed. Operators can cancel a pending upgrade, which voids the invoice in both the system and Xero and marks the subscription upgrade as cancelled. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero (invoice creation and voiding), Task/Email service (pre-charge notifications with/without saved payment method), Payment method & credit card services (determine auto-charge eligibility), Subscription auto-upgrade service (`subscription-auto-upgrade.service.ts`), Payment V2 service (`postPaymentDoneForAutoUpgradeInvoice`) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `invoices`, `customersubscriptions` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which operator roles (groups) are authorised to call these endpoints — no `@GroupAuth` guard is applied, only `@Auth()`; unclear if any role restriction is enforced upstream. Market scope unknown — no locale/country branching detected in code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `invoice/controllers/invoice.controller.ts`

| Method | Route | Guard | Description |
|---|---|---|---|
| `POST` | `/invoices/auto-upgrade` | `@Auth()` | Create auto-upgrade invoice for a subscription (`createAutoUpgradeInvoice`) |
| `POST` | `/invoices/auto-upgrade/:subscriptionId/cancel` | `@Auth()` | Cancel a pending auto-upgrade and void the invoice (`cancelAutoUpgrade`) |

### Service — `invoice/services/invoice.service.ts`

**`createAutoUpgradeInvoice` (line ~2504)**
- Accepts `subscriptionId` + `upgradeToServiceId`
- Validates subscription, target service, and company exist
- Calculates `priceDiff = targetService.price - currentService.price`
- Creates an invoice with `invoiceOrigin: InvoiceOrigin.autoUpgrade` and `isCreateXeroInvoice: true` (synced to Xero)
- Updates `CustomerSubscription.upgradeInvoiceId` and sets `upgradeStatus` to `pendingCharge` (payment method found) or `noPaymentMethod`
- If payment method exists: sets `autoChargeDate = now + 5 days`, sends `auto_upgrade_pre_charge_with_saved_payment_method` email via task service
- If no payment method: sends `auto_upgrade_pre_charge_without_saved_payment_method` email with a `paymentToken`
- Writes audit log entry

**`cancelAutoUpgrade` (line ~2627)**
- Finds the linked invoice via `subscription.upgradeInvoiceId`
- Guards against cancelling a paid invoice
- Voids invoice in MongoDB (`status: voided`, `autoChargeDate: null`)
- Voids invoice in Xero via `xeroService.updateInvoice`
- Sets `CustomerSubscription.upgradeStatus = cancelledCharge`
- Writes audit log entry

**Related methods**
- `postPaymentDoneForAutoUpgradeInvoice` — called after successful payment; sets `upgradeStatus = manualUpgraded` if not already `autoUpgraded`
- `cancelSubscriptionUpgradeWhenInvoiceVoided` — called when an auto-upgrade invoice is voided directly; sets `upgradeStatus = cancelledVoided`

### DTO — `invoice/dtos/create-auto-upgrade-invoice.dto.ts`
Fields: `subscriptionId` (string, required), `upgradeToServiceId` (string, required)

### Schema fields touched
- `Invoice`: `invoiceOrigin`, `autoChargeDate`, `status`, `externalId`, `cancelledUpgradeReason`
- `CustomerSubscription`: `upgradeInvoiceId`, `upgradeStatus`
