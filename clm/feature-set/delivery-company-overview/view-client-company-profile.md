# View Client Company Profile

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | View Client Company Profile |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Delivery Staff |
| **Business Outcome** | Enables delivery staff to surface a client company's statutory registration details and jurisdiction-specific regulatory obligations (ATO requirements, HK tax documents, UK VAT history) from a single screen, reducing context-switching during client servicing. |
| **Entry Point / Surface** | Sleek Billings App > Delivery > Company Overview |
| **Short Description** | Delivery staff search for a client company by name or registration number and view its statutory profile — company status, registration numbers, incorporation date, FYE dates, and Xero contact ID — with additional jurisdiction panels for ATO reporting (AU), ER/PTR tax documents (HK), and VAT registration history (UK). Attached files and links from company tasks are also browsable from the same screen. |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | Subscription Progress / Delivery Overview (`/delivery/overview`) — linked via "View subscription progress" button; Companies House API (UK — accounts filing dates, confirmation statement dates); Xero (contact ID displayed for HK and UK) |
| **Service / Repository** | sleek-billings-frontend, sleek-back (statutory details via `GET /companies/:id?load[]=fye`), sleek-service-delivery (company search, task activities, ATO/HK tax/UK VAT endpoints), Companies House API (UK, proxied through sleek-back) |
| **DB - Collections** | Unknown — frontend only; backend collections for ATO requirements, HK tax documents, and UK VAT registration records are in sleek-service-delivery and not visible in this repo |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) Company Tasks tab is currently hidden/commented out — planned feature or deprecated? (2) `billingConfig.platform` is read from localStorage to determine which market fields to display — where and when is this set? (3) Backend DB collections for ATO, HK tax doc, and UK VAT data are unknown without access to sleek-service-delivery repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Search & company selection
- `CompanyOverview.jsx` — debounced (300 ms) search calls `sleekServiceDeliveryApi.getAllCompanies({ search, limit: 10, page: 1 })` → `GET /companies?search=...`
- On selection, fetches statutory details via `sleekBackApi.getCompanyDetails(company.external_ref_id)` → `GET /companies/:id?load[]=fye`
- For UK platform only, additionally calls `sleekCompaniesHouseApi.getCompany(data.uen)` → `GET /v1/companies/fetch-details/:companyNumber` (production) or `GET /v1/companies/:companyNumber` (non-production) — Companies House integration

### Platform-aware statutory fields (`CompanyOverviewDetails.jsx`)
Platform is resolved from `localStorage.getItem("billingConfig").platform`:

| Market | Fields shown |
|---|---|
| **SG** | status, company_type, onboardedFor, incorporation_date, UEN, last_filed_fye, financial_year, current_fye |
| **HK** | status, company_type, onboardedFor, xero_contact_id, incorporation_date, CR No. (crn), BR No. (brn), last_filed_fye, financial_year, current_fye |
| **AU** | status, company_type, onboardedFor, incorporation_date, ABN, ACN, TFN (tax_number), last_filed_fye, financial_year, current_fye |
| **UK** | status, company_type, onboardedFor, xero_contact_id, incorporation_date, Company Number (uen), UTR, lastAccountsMadeUpTo, accountsNextMadeUpTo, accountsNextDue, current_fye, confirmationStatementLastMadeUpTo, confirmationStatementNextMadeUpTo, confirmationStatementNextDue |

UK accounts/confirmation-statement dates are sourced from `companyDetails.companiesHouseData` (Companies House response).

### Tab: Files & Links
- `sleekServiceDeliveryApi.getCompanyTaskActivities(companyId, { activityTypes: ['FILE', 'COMMENT_AND_FILE'] })` → `GET /companies/:id/task-activities?activityTypes=...`
- `sleekServiceDeliveryApi.getCompanyTaskActivities(companyId, { activityTypes: ['LINK'] })` → same endpoint, different filter
- File download: `sleekServiceDeliveryApi.getTaskActivityFileUrl(activity.id)` — opens signed URL in new tab
- Paginated (8 per page)

### AU panel — ATO Reporting Requirements (`CompanyOverviewDetailsAU.jsx`)
- `sleekServiceDeliveryApi.getATOReportingRequirements(companyId)` — read
- `sleekServiceDeliveryApi.createATOReportingRequirements(payload)` — create/update entry
- `sleekServiceDeliveryApi.deleteATOReportingRequirements(id)` — remove entry
- Captures: financialYear, gstRegistered (Yes/No), reportingRequirement (BAS/IAS/None), reportingFrequency (Annually/Quarterly/Monthly), effectiveFrom, remarks
- Logic: status = "Required" when (gstRegistered=Yes + BAS) or (gstRegistered=No + IAS); else "Not required"
- History grouped by FY with collapsible rows

### HK panel — Company Tax Documents ER/PTR (`CompanyOverviewDetailsHK.jsx`)
- `sleekServiceDeliveryApi.getCompanyTaxDocuments(companyId)` — read
- `sleekServiceDeliveryApi.createCompanyTaxDocument(payload)` — add new PTR/ER document
- `sleekServiceDeliveryApi.updateCompanyTaxDocument(id, data)` — update status (Received ↔ Submitted)
- `sleekServiceDeliveryApi.deleteCompanyTaxDocument(id)` — remove document
- Document types: Employer's Return (ER), Profits Tax Return (PTR)
- Fields: taxYear, documentType, status, dateReceived, issueDate, dueDate, filedDate, remarks
- History grouped by tax year with collapsible rows

### UK panel — VAT Registration (`CompanyOverviewDetailsUK.jsx`)
- `sleekServiceDeliveryApi.getVATRegistrationRequirements(companyId)` — read
- `sleekServiceDeliveryApi.createVATRegistrationRequirements(payload)` — add new entry
- VAT Status options: Not registered, Registered, Deregistered
- When Registered: frequency (Annually/Quarterly/Monthly), staggerGroup (quarter end months), vatScheme (Accruals/Cash/Flat Rate/Partial Exemption), effectiveFrom (EDR)
- Derives effectiveTo from the next entry's effectiveFrom − 1 day for display in history table
- "View details" action opens a full-detail dialog for any historical VAT record

### Hidden feature
- Company Tasks tab exists in code but is commented out — placeholder rows were implemented with mock data; deferred from the current release
