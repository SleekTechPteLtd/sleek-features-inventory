# Send Request to SleekSign

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Send Request to SleekSign |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Route a completed document to the SleekSign e-signature platform for client or internal signing |
| **Entry Point / Surface** | Admin App > Request detail > SEND TO SLEEKSIGN button |
| **Short Description** | Sends the request document to SleekSign for electronic signature. Available on qualifying requests. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | SleekSign |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Confirm whether SleekSign integration is active in all 4 regions (SG, HK, UK, AU) or SG-only. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/requests/edit.js` — request detail (document data, status, rich-text document, PDF, SleekSign). Webpack: `admin/requests/edit`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
