# Account details

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Account details |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Shows detailed information for a selected currency/business account (identifiers, status, related actions). |
| **Entry Point / Surface** | **`/sba/business-account/accounts/details`** — **`name: "Account Details"`**, component **`SBAAccountDetails`**. |
| **Short Description** | Detail view for an account; may deep-link from dashboard or open-account flows. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | `sba-bank-api` account endpoints |
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

- `customer-sba/src/routes/routes.js` — `path: "business-account/accounts/details"`.
