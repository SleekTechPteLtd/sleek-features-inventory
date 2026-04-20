# Open new currency account

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Open new currency account |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Onboards additional currency accounts for the business within SBA. |
| **Entry Point / Surface** | **`/sba/business-account/accounts/new`** — **`name: "New Account"`**, component **`SBAOpenAccount`**. |
| **Short Description** | Application or wizard for new account opening tied to DBS/orchestrator rules. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Account details; `sba-bank-api` / DBS VA flows |
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

- `customer-sba/src/routes/routes.js` — `path: "business-account/accounts/new"`.
