# Client Request – Change of Shareholder's Particulars

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Request – Change of Shareholder's Particulars |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Company Director / Shareholder |
| **Business Outcome** | Allows clients to update an existing shareholder's particulars and file the change with ACRA via Sleek. |
| **Entry Point / Surface** | Client App > Requests > Request > Change of Shareholder's Particulars > Create a New Request |
| **Short Description** | Client submits change to an existing shareholder's particulars. Form fill < 5 mins; processing 4-5 working days. Free. Steps: No Payment > Processing document > Pending Signatures > ACRA Filing. ACRA documentation and penalty information linked. |
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

- Same **route** and module as officer particulars: `GET /customer/change-of-particular` — entry is distinguished by request catalogue type `change-of-shareholder-particular` in `CustomerRequestContent.vue`, which routes users into the shared change-of-particular workflow UI.

### customer-common

- Shared workflow messaging and layout as for officer particulars.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms shareholder-specific entry from **Requests** and shared downstream flow.
