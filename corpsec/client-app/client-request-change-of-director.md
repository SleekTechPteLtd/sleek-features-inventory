# Client Request – Change of Director

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Request – Change of Director |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Company Director |
| **Business Outcome** | Allows clients to change an existing director (e.g. to Nominee or Own Director) with ACRA filing handled by Sleek. |
| **Entry Point / Surface** | Client App > Requests > Request > Change of Director > Create a New Request |
| **Short Description** | Client initiates change of director type (Nominee or Own Director). Requires a local director remaining on board. Form fill < 15 mins; processing 4-5 working days. Steps: Payment (if required) > Invitation to join company > Due diligence on new director > Sleek Processing > Letter of resignation of old director > Pending Signatures > ACRA Filing. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | ACRA filing; SleekSign; KYC/due diligence flow; Camunda workflow (admin side) |
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

- Route `GET /customer/change-of-director-v2` — `src/routes/routes.js` (`ChangeOfDirectorContainerCamunda`).

### customer-common

- Shared workflow messaging (`MessagingTopic`, constants) used by Camunda-driven request UIs.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms nominee vs own-director branching and downstream signing/KYC notes.
