# Manage Credit Cards

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Credit Cards |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Company User, Company Admin |
| **Business Outcome** | Enables users and company admins to maintain the credit cards on file for a company account, ensuring billing can always proceed with a valid, up-to-date primary payment method. |
| **Entry Point / Surface** | Sleek App > Billing > Payment Methods > Credit Cards |
| **Short Description** | Users can add, view, set a primary card, and remove credit cards linked to a company account. Setting a card as primary deactivates the primary flag on all other cards and payment methods for that company. Stripe is used as the card tokenisation and storage layer; the token is never exposed to callers. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Stripe (card tokenisation and customer management); CustomerService (Stripe customer ID provisioning); CompanyUserService (admin role check on delete); PaymentMethodRepository (primary flag sync across payment methods); AuditLogsService (audit trail for add / update / delete) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `creditcards` (CreditCard schema), `paymentmethods` (PaymentMethod schema — primary flag reset on primary card change) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) `getCreditCardDetail` has a TODO to allow company admins to view any card, but that guard is currently commented out — only card owners can fetch detail. (2) The `mscomsec` app-origin header switches list filtering from companyId to userId — unclear which client uses this. (3) The `reference` field is accepted on card creation but undocumented; purpose is unknown. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `credit-card/credit-card.controller.ts`
| Method | Route | Guard | Description |
|---|---|---|---|
| `GET` | `/:id` | `@Auth()` | Fetch single card detail by Mongo ID; restricted to card owner (admin access TODO) |
| `GET` | `/` | `@Auth()` | List cards for a company (`companyId` query param); switches to userId filter when `app-origin: mscomsec` |
| `POST` | `/` | `@Auth()` | Add a new credit card via Stripe token; sets `isPrimary = true` if first card for company |
| `PUT` | `/:id` | `@Auth()` | Update card fields (isPrimary, status); restricted to card owner (TEST cards bypass) |
| `DELETE` | `/:id` | `@Auth()` | Remove card; allowed for card owner **or** company admin |

### Service — `credit-card/services/credit-card.service.ts`
- `createCreditCard`: calls `StripeService.init()` → `createStripeSource` (testing) or `createStripeCustomerSource`; provisions a Stripe customer via `CustomerService` if none exists; writes to `creditcards` collection; emits audit log (`AuditLogAction.create`).
- `updateCreditCard`: when `isPrimary = true`, bulk-resets `isPrimary = false` on all `creditcards` and `paymentmethods` for the company, then updates the target card.
- `deleteCreditCard`: emits audit log (`AuditLogAction.delete`), then hard-deletes via `CreditCardRepository.deleteById`.
- `sanitizeCreditCard`: strips the `token` field from all responses.

### Schema — `credit-card/models/credit-card.schema.ts`
Fields: `userId`, `companyId`, `reference`, `lastDigits`, `expiredAt`, `type` (card brand), `isPrimary`, `token` (Stripe source/card ID — internal only), `status`, `migratedAt`.
Indexes: `{ userId: 1 }`, `{ companyId: 1 }`.

### DTO — `credit-card/dtos/update-credit-card.request.dto.ts`
Accepted fields: `isPrimary` (boolean, optional), `status` (string | null, optional).
