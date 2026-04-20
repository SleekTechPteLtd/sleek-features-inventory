# Convert currency (FX)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Convert currency (FX) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Exchanges balances between currency accounts at available rates. |
| **Entry Point / Surface** | **`/sba/business-account/exchange-currency`** — **`name: "Convert Currency"`**, component **`CurrencyExchange`**. |
| **Short Description** | FX conversion UI; depends on DBS FX and MAS/orchestrator rate sources. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | `sba-bank-dbs-api` FX |
| **Service / Repository** | customer-sba; sba-bank-api; sba-bank-dbs-api |
| **DB - Collections** | N/A |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `customer-sba/src/routes/routes.js` — `path: "business-account/exchange-currency"`.
