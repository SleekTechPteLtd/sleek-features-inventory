# Onboarding: business account process

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Onboarding: business account process |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Guides the user through the multi-step SBA onboarding pipeline after signup intent. |
| **Entry Point / Surface** | **`/sba/business-account-process`** — **`name: "business-account-process"`**, component **`SBAProcess`**. |
| **Short Description** | Container for process steps (loading, validation, handoff to questionnaire or dashboard). |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Sign-up welcome; questionnaire; `sba-bank-api` onboarding APIs |
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

- `customer-sba/src/routes/routes.js` — `path: "/sba/business-account-process"`.
