# Onboarding: questionnaire

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Onboarding: questionnaire |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Collects KYB and product-fit answers required before account opening approval. |
| **Entry Point / Surface** | **`/sba/business-account-questionnaire`** — **`name: "business-account-questionnaire"`**, component **`SBASignUpQuestionnaire`**. |
| **Short Description** | Questionnaire module under `onboarding/`; pairs with process and welcome routes. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Compliance/KYB services via orchestrator |
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

- `customer-sba/src/routes/routes.js` — `path: "/sba/business-account-questionnaire"`, import `pages/onboarding/Questionnaire`.
