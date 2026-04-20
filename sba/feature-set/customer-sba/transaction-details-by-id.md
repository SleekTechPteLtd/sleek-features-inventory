# Transaction details by ID

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Transaction details by ID |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Presents full detail for a single transaction (status, rails metadata, counterparty). |
| **Entry Point / Surface** | **`/sba/business-account/transaction-details/:id`** — **`name: "transaction-details"`**, component **`SBATransactionDetails`**. |
| **Short Description** | Dynamic route loads transaction by `:id` from list/deeplink. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Account transactions list |
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

- `customer-sba/src/routes/routes.js` — `path: "business-account/transaction-details/:id"`.
