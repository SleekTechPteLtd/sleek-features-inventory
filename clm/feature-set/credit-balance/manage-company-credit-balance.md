# Manage Company Credit Balance

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Company Credit Balance |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables Sleek operations staff to manually adjust a company's credit balance (add or deduct) with a mandatory reason, and to review the current balance alongside a full chronological transaction history — giving ops full visibility and control over credits applied to client accounts. |
| **Entry Point / Surface** | Internal Ops Tool > Company > Credit Balance (exact nav path unknown; backend API: `POST /credit-balances`, `GET /credit-balances/:companyId`) |
| **Short Description** | Operations users can add or deduct credits from a company's account by posting a signed amount with a required reason. The system records every change as a transaction (add/deduct) attributed to the acting user, and returns the running balance plus full transaction history — including linked invoices — on retrieval. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Invoice payment flow (credits auto-deducted at invoice payment via `deductCreditBalance` and `getCreditBalanceAmountForInvoice`); User service (operator identity resolution); Invoice collection (transaction history populated with invoice data) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `creditbalances`, `creditbalancetransactions` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. What frontend surface (admin portal, ops tool) calls these endpoints? 2. `CreditBalanceAccountType` has a `sleek_internal` variant — is there a separate internal credit pool, and who manages it? 3. Are credits denominated in a specific currency, or are they currency-agnostic units? 4. What markets/regions use credit balances? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `credit-balance/controllers/credit-balance.controller.ts`

| Method | Route | Guard | Purpose |
|---|---|---|---|
| `POST` | `/credit-balances` | `@Auth()` | Create or update a company's credit balance (add or deduct via signed `amount`) |
| `GET` | `/credit-balances/:companyId` | `@Auth()` | Retrieve current balance + full transaction history for a company |

### Service — `credit-balance/services/credit-balance.service.ts`

- **`updateOrCreateCreditBalance(payload, req)`** — upserts the balance record; validates the resulting balance cannot go negative; records a `CreditBalanceTransaction` with `actionType: add | deduct`, the acting user's ID and email, and an optional `invoiceId`. Positive `amount` → add; negative → deduct.
- **`getCompanyCreditBalance(params)`** — returns the balance document merged with all transactions for the company, sorted newest-first, with each transaction's linked `Invoice` populated.
- **`deductCreditBalance(companyId, amount, description, userId, invoiceId, reason?)`** — system-initiated deduction used by the invoice payment flow; idempotent (checks for an existing transaction against the same `invoiceId` before deducting).
- **`getCreditBalanceAmountForInvoice(invoiceId, companyId?)`** — called during invoice generation/payment to determine how much credit to apply; returns 0 for onboarding invoices (no `companyId`).

### DTO — `credit-balance/dtos/update-or-create-credit-balance.request.dto.ts`

| Field | Type | Required | Notes |
|---|---|---|---|
| `companyId` | MongoId | Yes | Target company |
| `amount` | Number | Yes | Positive = add, negative = deduct |
| `reason` | String | Yes | Mandatory audit trail field |
| `invoiceId` | MongoId | No | Links credit change to a specific invoice |

### Schemas

**`credit-balance/models/credit-balance.schema.ts`** → collection `creditbalances`
- Fields: `companyId`, `balance`
- Index: `{ companyId: 1 }`

**`credit-balance/models/credit-balance-transaction.scheme.ts`** → collection `creditbalancetransactions`
- Fields: `companyId`, `creditBalanceId`, `userId`, `userEmail`, `invoiceId`, `amount`, `actionType` (add | deduct), `accountType` (general | sleek_internal), `description`, `reason`
- Virtual: `invoice` → populated from `Invoice` collection via `invoiceId`
- Indexes: `{ invoiceId: 1 }`, `{ companyId: 1 }`
