# Notify Company Owner (Mailroom)

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Notify Company Owner (Mailroom) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Alert the client company's admin that new mail or documents have been received and added to their mailroom |
| **Entry Point / Surface** | Admin App > Mailroom > Select Company > NOTIFY OWNER button |
| **Short Description** | Sends a notification to the company owner about documents in the mailroom. This button is unique to the Mailroom section and is absent in the Files section. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Confirm what channel the notification is sent via (email / in-app). Confirm whether notification content is templated or customisable. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/mailroom.js` — mailroom UI (shared patterns with Files; notify owner action). Webpack: `admin/mailroom`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
