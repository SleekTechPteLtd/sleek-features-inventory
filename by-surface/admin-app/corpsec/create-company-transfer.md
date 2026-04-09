# Create Company – Transfer

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Create Company – Transfer |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin User / Corpsec Officer |
| **Business Outcome** | Enable Sleek to onboard an existing company being transferred to Sleek's management |
| **Entry Point / Surface** | Admin App > Companies List > CREATE COMPANY > Transfer |
| **Short Description** | Immediately creates a Draft company record (On-boarded for = Transfer). AU uniquely splits this into two sub-types: 'Transfer - Company' and 'Transfer - Sole trader', each creating a Draft record with the appropriate entity profile. SG, HK, UK have a single Transfer option. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | AU exposes Transfer as two distinct options (Transfer - Company / Transfer - Sole trader) — confirm whether these are treated as separate feature rows or variants of the same flow. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/companies/create-draft-company-button/create-draft-company-button.js` — Transfer path and AU variants.

### sleek-back

- `controllers/admin/company-controller.js` — `POST /admin/companies/draft-creation`.

### Live app walkthrough

- Confirms admin UX described in the master sheet.
