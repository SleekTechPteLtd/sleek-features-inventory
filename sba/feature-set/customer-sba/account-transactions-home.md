# Account transactions (dashboard home tab)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Account transactions (dashboard home tab) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Shows account activity, balances, and transaction list from the primary dashboard child route. |
| **Entry Point / Surface** | **`/sba/business-account`** (nested under dashboard) — **`name: "business account"`**, component **`AccountTransactions`**. |
| **Short Description** | Default landing after redirect; surfaces transactions tied to the business account context. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | `sba-bank-api` transactions/accounts; link to transaction details |
| **Service / Repository** | customer-sba; sba-bank-api |
| **DB - Collections** | N/A |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `customer-sba/src/routes/routes.js` — dashboard child `path: "business-account"`, `component: AccountTransactions`.
