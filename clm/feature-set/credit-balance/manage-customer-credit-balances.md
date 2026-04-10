# Manage Customer Credit Balances

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Customer Credit Balances |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operators to view and adjust credit balances held on behalf of customers, giving finance teams visibility into when credits were issued, by whom, and why — and allowing manual additions or deductions to support billing adjustments. |
| **Entry Point / Surface** | Sleek Billings > Billing > Credit Balance (`/credit-balance`); add credit via `/credit-balance/create` |
| **Short Description** | Operators browse and search credit balance transaction history across all clients (by customer name or email), viewing transaction date, initiator, description, reason, linked invoice, and amount. Authorised users can manually add or deduct credit for a company, with a required reason and optional invoice link. The backend enforces a non-negative balance constraint and writes a full audit trail of every change. |
| **Variants / Markets** | Unknown (currency display hardcoded to `$` in the frontend; no market-switching logic found) |
| **Dependencies / Related Flows** | Invoice management (`Invoice` collection populated via virtual on transactions); auto-deduct on invoice payment (system-triggered `deductCreditBalance` internal call); User service (audit trail — stores userId and userEmail of initiating operator) |
| **Service / Repository** | sleek-billings-frontend; sleek-billings-backend |
| **DB - Collections** | `credit_balances` (one doc per company — holds running balance); `credit_balance_transactions` (append-only audit log — add/deduct entries with amount, reason, invoiceId, userEmail); `invoices` (populated via virtual on transactions) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | (1) `sleekBillingsApi.getCreditBalances()` (list-all call in CreditBalanceList.jsx) is not matched by a list endpoint in the controller (`GET /credit-balances/:companyId` returns one company's data) — a separate list/paginated endpoint may exist in another module or the API method is incomplete. (2) Currency is hardcoded to `$`; unclear whether multi-currency or per-company currency is planned. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend — sleek-billings-frontend

- `src/pages/CreditBalance/CreditBalanceList.jsx` — list page; calls `sleekBillingsApi.getCreditBalances({ page, limit: 10, filter })` with MongoDB-style `$or` filter on `customerName` / `customerEmail`; renders columns: Transaction Date (`balance.createdAt`), Initiated by (`balance.initiatedBy`), Description (`balance.description`), Reason (`balance.reason`), Invoice (`balance.invoice`), Amount (`balance.amount`); debounced search (300 ms); MUI Pagination; "Add Credit" button navigates to `/credit-balance/create`
- `src/App.jsx` — lazy-loaded route: `<Route path="credit-balance" element={<CreditBalanceList />} />`; no `/credit-balance/create` route registered (creation component not yet wired in the router)
- `src/components/Navbar.jsx` — Credit Balance listed under the Billing nav group: `{ path: '/credit-balance', icon: CurrencyDollarIcon, label: 'Credit Balance' }`

### Backend — sleek-billings-backend

- `src/credit-balance/controllers/credit-balance.controller.ts`
  - `POST /credit-balances` `@Auth()` — creates or updates a company's credit balance; body: `{ companyId, amount (positive = add, negative = deduct), reason, invoiceId? }`
  - `GET /credit-balances/:companyId` `@Auth()` — returns current balance and full transaction history (sorted by `createdAt desc`, invoice populated via virtual)
- `src/credit-balance/services/credit-balance.service.ts`
  - `updateOrCreateCreditBalance` — upserts `credit_balances` doc; validates new balance ≥ 0 (`BadRequestException: Insufficient balance`); writes `credit_balance_transactions` entry with `actionType: add | deduct`, `reason`, `userId`, `userEmail`, optional `invoiceId`; falls back to master user if no `req.user`
  - `getCompanyCreditBalance` — fetches balance + all transactions; populates `invoice` virtual
  - `deductCreditBalance` — internal (non-HTTP) method called by invoice payment flows; idempotent per `invoiceId`; also validates sufficient balance before deducting
  - `getCreditBalanceAmountForInvoice` — returns applicable credit for an invoice (0 if no companyId; uses existing transaction amount if already applied)
- `src/credit-balance/dtos/update-or-create-credit-balance.request.dto.ts` — `companyId (MongoId)`, `amount (number, required)`, `reason (string, required)`, `invoiceId (MongoId, optional)`
- `src/credit-balance/models/credit-balance.schema.ts` — `CreditBalance` schema: `companyId`, `balance`; indexed on `companyId`
- `src/credit-balance/models/credit-balance-transaction.scheme.ts` — `CreditBalanceTransaction` schema: `companyId`, `creditBalanceId`, `userId`, `userEmail`, `invoiceId`, `amount`, `actionType (add|deduct)`, `accountType (general|sleek_internal)`, `description`, `reason`; virtuals `invoice`; indexed on `invoiceId` and `companyId`
