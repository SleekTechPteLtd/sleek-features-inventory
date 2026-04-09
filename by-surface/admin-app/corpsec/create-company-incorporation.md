# Create Company – Incorporation

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Create Company – Incorporation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin User / Corpsec Officer |
| **Business Outcome** | Enable Sleek to onboard a new company for Singapore incorporation |
| **Entry Point / Surface** | Admin App > Companies List > CREATE COMPANY > Incorporation |
| **Short Description** | Immediately creates a Draft company record (On-boarded for = Incorporation) and opens the edit form pre-populated with incorporation-specific fields: Preferred Incorporation date / Reason for establishing company / Dormant flag / Customer Risk Rating / SBA details / SSIC codes / Business Account projections / Registered address / Web 3.0 declaration. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Does clicking Incorporation always auto-create the record or is there a confirmation step? |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/companies/create-draft-company-button/create-draft-company-button.js` — draft creation (incorporation vs transfer; AU sole-trader variant where applicable).

### sleek-back

- `controllers/admin/company-controller.js` — `POST /admin/companies/draft-creation` (`companies`, `full`).

### Live app walkthrough

- Confirms admin UX described in the master sheet.
