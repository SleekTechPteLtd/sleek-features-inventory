# Onboarding: sign-up welcome

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Onboarding: sign-up welcome |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Welcomes the user to SBA signup and routes into questionnaire or process. |
| **Entry Point / Surface** | **`/sba/business-account-sign-up`** — **`name: "business-account-sign-up"`**, component **`SBASignUpWelcome`**. |
| **Short Description** | Entry screen for the SBA acquisition funnel. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Questionnaire; business-account-process |
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

- `customer-sba/src/routes/routes.js` — `path: "/sba/business-account-sign-up"`.
