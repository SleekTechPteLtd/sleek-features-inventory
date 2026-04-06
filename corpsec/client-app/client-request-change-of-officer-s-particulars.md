# Client Request – Change of Officer's Particulars

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Request – Change of Officer's Particulars |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Company Director |
| **Business Outcome** | Allows clients to update an existing director's particulars and file the change with ACRA via Sleek. |
| **Entry Point / Surface** | Client App > Requests > Request > Change of Officer's Particulars > Create a New Request |
| **Short Description** | Client submits change to an existing director's particulars. Form fill < 5 mins; processing 4-5 working days. Free. Steps: No Payment > Processing document > Pending Signatures > ACRA Filing. ACRA documentation and penalty information linked. |
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

- Route `GET /customer/change-of-particular` — `src/routes/routes.js` → `modules/change-of-particular/containers/ChangeOfParticular.vue` → `components/ChangeOfParticular*.vue` (document / address / upload steps driven by workflow messaging).
- **Requests hub:** `CustomerRequestContent.vue` maps `change-of-officer-particular` to the change-of-particulars icon/tile.

### customer-common

- `MessagingTopic` and workflow action constants consumed by the change-of-particular flow.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms director particulars change and ACRA filing path.
