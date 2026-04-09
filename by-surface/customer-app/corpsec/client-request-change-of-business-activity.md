# Client Request – Change of Business Activity

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Request – Change of Business Activity |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Company Director |
| **Business Outcome** | Allows clients to add or change their company's business activity (SSIC code) via Sleek with ACRA filing. |
| **Entry Point / Surface** | Client App > Requests > Request > Change of Business Activity > Create a New Request |
| **Short Description** | Client submits updated business activity description (75 word limit). Can add additional activity or replace existing. Form fill < 15 mins; processing 1-3 working days. Free. Steps: No Payment > Processing document > Pending Signatures > ACRA Filing. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | ACRA filing; SleekSign; Camunda workflow (admin side) |
| **Service / Repository** | customer-main, customer-common, customer-root (client shell and shared UI) |
| **DB - Collections** | — |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** |  |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### customer-main

- Route `GET /customer/change-of-business-activity` — `src/routes/routes.js` (`ChangeOfBizAct`).

### customer-common

- `MasterLayout`.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms SSIC / activity copy limits and free-flow steps.
