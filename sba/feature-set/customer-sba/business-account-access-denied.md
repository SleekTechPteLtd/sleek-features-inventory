# Business account access denied

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Business account access denied |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Explains when the user cannot access SBA (permissions, KYB state, or product eligibility). |
| **Entry Point / Surface** | **`/sba/business-account-access-denied`** — **`name: "business-account-access-denied"`**, component **`SBAAccessDenied`**. |
| **Short Description** | Dedicated access-denied surface under `/sba` for gating errors. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Auth / company entitlements from `sleek-back` |
| **Service / Repository** | customer-sba; sleek-back; sba-bank-api |
| **DB - Collections** | N/A |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `customer-sba/src/routes/routes.js` — `path: "/sba/business-account-access-denied"`.
