# View & Search Company List

## Master sheet (draft)


| Column                           | Value                                                                                                                                                                                                            |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Domain**                       | Corpsec                                                                                                                                                                                                          |
| **Feature Name**                 | View & Search Company List                                                                                                                                                                                       |
| **Canonical Owner**              | TBD                                                                                                                                                                                                              |
| **Primary User / Actor**         | Admin User                                                                                                                                                                                                       |
| **Business Outcome**             | Give operations teams a single place to locate any client company quickly                                                                                                                                        |
| **Entry Point / Surface**        | Admin App > Companies List                                                                                                                                                                                       |
| **Short Description**            | Paginated list of all companies showing Name / UEN / Transfer flag / Client Type / Record Type / Created Date. Search by User Email / Allocated Users / Customer Name.                                           |
| **Variants / Markets**           | SG, HK, UK, AU                                                                                                                                                                                                   |
| **Dependencies / Related Flows** | —                                                                                                                                                                                                                |
| **Service / Repository**         | sleek-back, sleek-website                                                                                                                                                                                        |
| **DB - Collections**             | sleek                                                                                                                                                                                                            |
| **Evidence Source**              | Live app walkthrough, codebase                                                                                                                                                                                   |
| **Criticality**                  | High                                                                                                                                                                                                             |
| **Usage Confidence**             | High                                                                                                                                                                                                             |
| **Disposition**                  | Must Keep                                                                                                                                                                                                        |
| **Open Questions**               | Registration ID column name differs by region: SG=UEN, HK=BR No., UK=Company Number, AU=ABN. HK and AU show Updated Date column instead of Client Type. UK admin has an additional Dashboard top-level nav item. |
| **Reviewer**                     |                                                                                                                                                                                                                  |
| **Review Status**                | Draft                                                                                                                                                                                                            |


## Evidence

### sleek-website

- **Admin Companies List UI** — `src/views/admin/companies/index.js` (`AdminCompaniesView`): breadcrumbs “Companies”, pagination (`page` / `perPage` 20), search dropdown (`User Email` / `Allocated Users` when resource allocation feature is on / `Customer Name`) and debounced `getCompanies`; table uses CMS-driven registration label (`company_meta.value.business_registration_number_label_short`), Transfer column, Client Type vs **Updated Date** header depending on `getCompanyClientType` (feature `companies.filters.client_type_enabled`), Record Type, sortable Created Date; links to company overview/edit via `getCompanyOverviewUrl`. Webpack entry: `webpack/paths.js` → `admin/companies/index` → page `/admin/companies/`.
- **API client** — `src/utils/api.js`: `getCompanies` calls `GET ${base}/companies`; when the caller sets `options.admin = true`, `getResource` rewrites the base URL to `${base}/admin`, so the list request is `**GET /admin/companies`** with query params (`status`, `sub_status`, `clientType`, `record_type`, `sortBy`, `sortOrder`, `skip`, `email`, `emailType`, `uen`, `name`, SG-only ACRA filters, etc.).

### sleek-back

- **Admin list endpoint** — `controllers/admin/company-controller.js`: `GET /admin/companies` with `userService.authMiddleware` and `accessControlService.can("companies", "read")`. Parses query (`sub_status`, `acra_non_compliant`, `acra_statuses`, `record_type`, …), resolves email search by `emailType` (`getUserByEmail`, `getAllocatedUsers`, `getUserByCustomerName`) for Sleek Admin, builds Mongo find via `createFindQuery`, optional ACRA UEN filtering through `corporateRegistryService.filterUensforAdminCompanySearch` for SG, returns `{ companies, count }` with `Company.find` / `countDocuments` and `companyService.sanitizeCompany`.

### Live app walkthrough

- Confirms paginated companies table, column and regional differences, and search behaviour described in the master sheet and implemented in the admin list view above.

