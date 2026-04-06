# Filter & Sort Company List

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Filter & Sort Company List |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin User |
| **Business Outcome** | Allow ops teams to narrow the company list by lifecycle or regulatory state without manual searching |
| **Entry Point / Surface** | Admin App > Companies List |
| **Short Description** | Filter dimensions vary by region. SG has 6 filters (Status 18 opts incl. Draft→Archived, ACRA Non-Compliant, ACRA Status, Client Type, Company Type, Record Type). HK has 2 filters (Status 15 opts using 'Processing by Company Registry', Record Type). UK has 3 filters (Status 18 opts using 'Processing by Companies House', Client Type, Record Type). AU has 2 filters (Status 16 opts using 'Processing by ASIC', Record Type). All regions support sortable columns and inline Name / registration-ID text filter. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | ACRA Non-Compliant and ACRA Status filters are SG-only. Company Type filter is SG-only. Client Type filter is SG and UK only. Status option labels differ by regulatory body (ACRA / Company Registry / Companies House / ASIC). |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/companies/index.js` — Status / Client Type / Company Type / Record Type multi-selects, SG-only ACRA filters, column sort (`handleClickTableHeader`), inline name and registration-ID filters.

### sleek-back

- `controllers/admin/company-controller.js` — `GET /admin/companies` with `sortBy` / `sortOrder`, `createFindQuery` (status, sub_status, clientType, company_type, record_type, …).

### Live app walkthrough

- Confirms admin UX described in the master sheet.
