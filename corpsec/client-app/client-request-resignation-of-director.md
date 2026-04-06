# Client Request – Resignation of Director

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Request – Resignation of Director |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Company Director |
| **Business Outcome** | Allows clients to process a director resignation with all required ACRA documentation handled by Sleek. |
| **Entry Point / Surface** | Client App > Requests > Request > Resignation of Director > Create a New Request |
| **Short Description** | Client initiates resignation of an existing director. Requires a local director remaining on board post-resignation. Form fill < 15 mins; processing 4-5 days. Free. Steps: Sleek Processing > Letter of resignation > Pending Signatures > ACRA Filing > Board resolution > Pending Signatures. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | ACRA filing; SleekSign (letter of resignation and board resolution); Camunda workflow (admin side) |
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

- Route `GET /customer/resignation-of-director-v2` — `src/routes/routes.js` (`ResignationOfDirectorContainerCamunda`).

### customer-common

- Shared layout and workflow helpers as above.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms resignation + board resolution signing steps.
