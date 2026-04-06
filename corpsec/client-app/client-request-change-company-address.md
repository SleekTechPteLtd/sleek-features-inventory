# Client Request – Change Company Address

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Request – Change Company Address |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Company Director |
| **Business Outcome** | Allows clients to update their company's registered address and file the change with ACRA via Sleek. |
| **Entry Point / Surface** | Client App > Requests > Request > Change Company Address > Create a New Request |
| **Short Description** | Client submits updated registered address. Requires signing of documents and payment for the change of address service. Form fill < 5 mins; processing 4-5 days. Steps: Create request > Sleek Processing > Board Resolution for Signing > Pending Signatures > ACRA Filing. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | ACRA filing; SleekSign (board resolution signatures); Camunda workflow (admin side) |
| **Service / Repository** | customer-main, customer-common, customer-root (client shell and shared UI) |
| **DB - Collections** | — |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** |  |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### customer-main

- Route `GET /customer/change-of-address` — `src/routes/routes.js` (`ChangeOfAddress` container).
- Related automation path: `/customer/automation-workflow/...` (Camunda) for workflow-driven change-of-address in some flows.

### customer-common

- Layout / navigation.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms board resolution / signing / ACRA steps described on the sheet.
