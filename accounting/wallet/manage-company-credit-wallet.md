# Manage company credit wallet

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage company credit wallet |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Company user (register wallet, view balance, list transactions); Admin (adjust wallet balance) |
| **Business Outcome** | Companies can hold and spend prepaid Sleek credits with a clear balance and transaction history tied to people, while admins can correct balances so credits match payments and invoicing. |
| **Entry Point / Surface** | Unknown (API-backed; company-scoped routes under `/api/company/:companyId/…`) |
| **Short Description** | Registers a company wallet against the Sleek Wallet service, stores `wallet_id` on the company, exposes balance and transaction history (with `created_by` resolved to user full names), and lets admins apply balance updates that include optional invoice linkage. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek Wallet** HTTP API (`config.sleekWallet.baseUrl`): `POST /api/wallet`, `GET /api/wallet/:walletId`, `GET /api/wallet/:walletId/transactions`, `PUT /api/wallet/:walletId`. Tenant localization supplies `country` via `tenant.general.localization.alpha_3_code`. MongoDB **Company** holds `wallet_id`; **User** is read to decorate transaction `created_by` with names. Admin updates may reference `invoice_id` for reconciliation with invoicing. |
| **Service / Repository** | sleek-back; external Sleek Wallet (ledger) service |
| **DB - Collections** | `companies` (read/update `wallet_id`); `users` (read for actor display on transactions) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether the Sleek Wallet deployment name maps 1:1 to “sleek-ledger” in all environments; exact app UI path for wallet screens. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Routing & auth** — `controllers-v2/wallet.js`: `buildPostRoute` / `buildAuthenticatedGetRoute` use `userService.authMiddleware` and `companyService.canManageCompanyMiddleware("companyUser")` for register, balance, and transactions; `buildPutRoute` uses the same auth with **`canManageCompanyMiddleware("admin")`** for balance updates only.
- **Endpoints** — `POST /api/company/:companyId/register-wallet` → `registerWallet`; `GET …/wallet-balance` → `getWalletBalance`; `GET …/transactions` → `getWalletTransactions`; `PUT …/update-wallet-balance` → `updateWalletBalance`.
- **Register** — `credit-balance.js` `registerWallet`: `POST` to `${sleekWallet.baseUrl}/api/wallet` with `company_id`, `company_name`, `country` from body (`CompanyId`, `CompanyName`) and tenant.
- **Balance** — `getWalletBalanceService`: loads `Company` by id; if `wallet_id` exists, `GET /api/wallet/:walletId`; else creates wallet via `POST /api/wallet`, persists `company.wallet_id`, then `GET` wallet details.
- **Transactions** — `getWalletTransactions`: same wallet bootstrap pattern; `GET /api/wallet/:walletId/transactions`; maps each `transaction.created_by` through `User.findById` to `"first_name last_name"` or `""`; empty/null response from ledger yields `[]`.
- **Admin update** — `updateWalletBalanceService`: `PUT` to `/api/wallet/:walletId` with `description`, `currency`, `amount`, `user_id`, `invoice_id` from request body.
- **Schema** — `schemas/company.js`: `wallet_id` (ObjectId).
