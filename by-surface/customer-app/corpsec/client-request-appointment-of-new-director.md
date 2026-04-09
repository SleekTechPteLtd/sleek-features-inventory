# Client Request – Appointment of New Director

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Request – Appointment of New Director |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Company Director |
| **Business Outcome** | Allows clients to onboard a new director to the company with KYC due diligence and ACRA filing handled by Sleek. |
| **Entry Point / Surface** | Client App > Requests > Request > Appointment of New Director > Create a New Request |
| **Short Description** | Client creates a request for a new director joining the company. New director receives invitation and undergoes due diligence. Form fill < 15 mins; processing 4-5 days. Free (payment if applicable). Steps: Payment (if required) > Invitation to join company > Due diligence > Sleek processing > Pending signatures > ACRA Filing. |
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

- Route `GET /customer/appointment-of-director-v2` — `src/routes/routes.js` (`AppointmentOfDirectorContainerCamunda`).
- **Requests hub** lists `appoint-new-director` / `appointment-of-director` in `CustomerRequestContent.vue`.

### customer-common

- `MasterLayout`; workflow constants via `customer-sdk` / shared messaging.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms invitation + due diligence + ACRA filing narrative.
