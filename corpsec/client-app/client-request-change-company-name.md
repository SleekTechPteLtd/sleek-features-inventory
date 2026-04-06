# Client Request – Change Company Name

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Request – Change Company Name |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Company Director |
| **Business Outcome** | Allows clients to initiate a company name change via Sleek, with ACRA filing handled on their behalf. |
| **Entry Point / Surface** | Client App > Requests > Request > Change Company Name > Create a New Request |
| **Short Description** | Client submits a request to change company name. ACRA name availability check is performed; S$15 name reservation fee absorbed by Sleek. Form fill < 15 mins; processing 5 working days to 2 months for referred cases. Steps: No Payment > Sleek Processing > Document Pending Signatures > ACRA Filing. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | ACRA filing; SleekSign (document signatures); Camunda workflow (admin side) |
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

- Route `GET /customer/change-of-company-name` — `src/routes/routes.js`.
- `src/modules/change-of-company-name/containers/ChangeOfCompanyName.vue` (lazy chunk `customer-requests`) — end-user flow for name change / ACRA-related steps.

### customer-common

- `MasterLayout` and shared customer chrome.

### customer-root

- `src/root-config.js` — `/customer` → `customer-main`.

### Live app walkthrough

- Confirms catalogue entry under **Requests** and multi-step status progression on the sheet.
