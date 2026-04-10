# Manage Payment Methods

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Payment Methods |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User / Admin |
| **Business Outcome** | Enables company admins to register and manage Stripe payment methods so that subscriptions and invoices can be billed automatically without manual intervention. |
| **Entry Point / Surface** | Sleek App > Billing > Payment Methods (REST API: `POST/GET/PUT/DELETE /payment-methods`) |
| **Short Description** | Users attach Stripe payment methods (credit/debit cards, SEPA debit, BACS, AU BECS) to a company account, designate one as primary for billing, and remove outdated methods. Adding the first payment method automatically re-enables subscription auto-renewal if it was previously paused due to missing payment details. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Stripe (attach/retrieve payment methods), CustomerService (resolve Stripe customer ID from company), Manage Subscriptions (auto-renewal toggle reactivated on first payment method added), Credit Card (legacy `isPrimary` flag kept in sync), Audit Logs |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `paymentmethods`, `paymentmethodarchiveds`, `customersubscriptions` (auto-renewal update), `creditcards` (isPrimary sync) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. `mscomsec` app-origin routes listing by `userId` rather than `companyId` — is this a consumer (B2C) variant or an internal tool path? 2. SEPA debit type is handled in code — which markets use it (EU customers)? 3. `creditCardRepository` `isPrimary` sync suggests a legacy `creditcards` collection coexists with `paymentmethods` — is the credit card module being deprecated in favour of this one? 4. `archivedPaymentMethod()` is not exposed via the controller — what internal flow triggers archival (e.g. Stripe webhook on card expiry)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `src/payment-method/payment-method.controller.ts`

| Method | Route | Guard | Notes |
|---|---|---|---|
| `POST` | `/payment-methods` | `@Auth()` | Creates payment method; reads `app-origin` header to set client type |
| `GET` | `/payment-methods` | `@Auth()` | Lists by `companyId` query param; `mscomsec` origin lists by `userId` instead |
| `GET` | `/payment-methods/:id` | `@Auth()` | Retrieves single payment method detail |
| `PUT` | `/payment-methods/:id` | `@Auth()` | Updates payment method (e.g. set as primary); validates MongoId |
| `DELETE` | `/payment-methods/:id` | `@Auth()` | Deletes; ownership check — only the creating user may delete (unless `lastDigits === 'TEST'`) |

### Service — `src/payment-method/services/payment-method.service.ts`

**`createPaymentMethod`**
- Initialises Stripe client per `clientType` via `StripeService.init(clientType)`
- Fetches payment method details from Stripe (`stripeService.getPaymentMethodInfo`)
- Attaches Stripe payment method to the company's Stripe customer (`stripeService.attachPaymentMethod`)
- Sets `isPrimary = true` automatically if no other payment method exists for the company
- Populates type-specific fields:
  - `card`: `lastDigits`, `expiredAt`, `walletType`, `brand`
  - `sepa_debit`: `lastDigits`, `brand` (bank code)
  - `bacs_debit` (UK): `lastDigits`
  - `au_becs_debit` (AU): `lastDigits`
- Persists to `paymentmethods` collection via `PaymentMethodRepository`
- Re-enables auto-renewal on subscriptions previously disabled with reason `"Auto renewal off - No payment method found"` via `CustomerSubscriptionRepository.updateMany`
- Writes audit log: action `create`, tags `['payment-method', 'adding-payment-method']`

**`updatePaymentMethod`**
- If `isPrimary: true` in payload, clears `isPrimary` on all other records in both `paymentmethods` and `creditcards` collections for the same company (legacy sync)
- Writes audit log: action `update`, tags `['payment-method', 'updating-payment-method']`

**`deletePaymentMethod`**
- Hard-deletes record from `paymentmethods`
- Writes audit log: action `delete`, tags `['payment-method', 'deleting-payment-method']`

**`archivedPaymentMethod`** _(internal — not exposed via controller)_
- Copies payment method to `paymentmethodarchiveds` with `archivedAt`, `archivedReason`, `originalPaymentMethodId`
- Deletes original from `paymentmethods`
- If archived method was primary, auto-reassigns: card types take priority; oldest by `createdAt` wins

### Schemas — `src/payment-method/models/`

- **`payment-method.schema.ts`** → collection `paymentmethods`; fields: `userId`, `companyId`, `lastDigits`, `brand`, `country`, `walletType`, `externalId`, `expiredAt`, `type`, `isPrimary`, `status`; indexes on `userId` and `companyId`
- **`payment-method-archived.schema.ts`** → collection `paymentmethodarchiveds`; adds `archivedAt`, `archivedReason`, `originalPaymentMethodId`; indexes on `userId`, `companyId`, `originalPaymentMethodId`
