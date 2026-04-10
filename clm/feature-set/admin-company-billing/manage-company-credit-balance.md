# Manage Company Credit Balance

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage company credit balance |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (internal Sleek operations staff) |
| **Business Outcome** | Enables Sleek admins to manually adjust a company's credit balance and maintain an auditable transaction history, so that credits can be applied to offset future invoices without requiring a new payment. |
| **Entry Point / Surface** | Admin panel > Company > Billing > Credit Balance tab (tab index 2) |
| **Short Description** | Admins view a company's available credit balance and full transaction history (date, initiating user, description, reason, linked invoice, and signed amount). Via a modal dialog, they can add or deduct credit by entering an amount and mandatory reason; the adjustment is posted to the sleek-billing service and the list auto-refreshes. |
| **Variants / Markets** | Unknown — currency is read from `platformConfig.currency.code`, suggesting per-market behaviour, but no explicit market gating is visible in the frontend code |
| **Dependencies / Related Flows** | Company Billing (Subscriptions tab, Invoices & Credit Notes tab); invoice linking on credit transactions (external invoice URL + number rendered inline); sleek-billing payment service |
| **Service / Repository** | sleek-website (frontend); sleek-billing service (backend, resolved via `SLEEK_BILLINGS_API` env var) |
| **DB - Collections** | Unknown — data is owned by the sleek-billing service; collections not visible from frontend code |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which admin roles are permitted to add/deduct credit — is any role-based guard enforced on the backend endpoint? 2. Are credit balance adjustments journaled in Xero or SleekBooks? 3. Which markets is this feature active in? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend files
- `src/views/admin/company-billing/credit-balance-list.js` — `CreditBalanceList` component; calls `getCompanyCreditBalance(company._id)` on mount; renders available balance and a transaction table (columns: Transaction date, Initiated by `userEmail`, Description, Reason, Invoice link, Amount); exposes **Add Credit** and **Deduct Credit** buttons that open `CreditBalanceForm`.
- `src/views/admin/company-billing/credit-balance-form.js` — `CreditBalanceForm` modal dialog; captures `amount` (number, must be > 0) and `reason` (required text); on submit calls `updateOrCreateCreditBalance({ body: JSON.stringify({ amount: signed, reason, companyId }) })`; amount is positive for `add`, negative for `deduct`; shows toast on success/failure.
- `src/views/admin/company-billing/index.js` — `AdminBillingConfigurationView`; mounts `CreditBalanceList` as tab index 2 ("Credit Balance") within the Company Billing tabbed layout alongside Subscriptions (0) and Invoices & Credit Notes (1).

### API calls (via `src/utils/sleek-billings-api.js`)
- `GET  {SLEEK_BILLINGS_API}/credit-balances/{companyId}` — fetch current balance and transaction list; response shape: `{ balance: Number, transactions: Array }`.
- `POST {SLEEK_BILLINGS_API}/credit-balances` — create or update a credit balance entry; body: `{ amount, reason, companyId }`.

### Transaction data shape (from list rendering)
Fields present on each transaction: `_id`, `createdAt`, `userEmail`, `description`, `reason`, `invoice { externalUrl, externalNumber }`, `amount`, `actionType` (`"add"` | subtract implied by negative display).

### Error handling
On POST failure, the error toast suggests contacting `#new-subscription-billing-support` in Slack, indicating this is an ops-facing internal tool.
