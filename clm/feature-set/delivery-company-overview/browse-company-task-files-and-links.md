# Browse Company Task Files and Links

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Browse Company Task Files and Links |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Delivery Staff (Operations User) |
| **Business Outcome** | Gives delivery staff a single place to find all documents and external references attached to a company's service delivery tasks, reducing time spent searching across tasks for supporting materials. |
| **Entry Point / Surface** | Sleek Billings App > Delivery > Company Overview (`/delivery/company-overview`) — Files tab and Links tab |
| **Short Description** | After searching for and selecting a client company, delivery staff can browse paginated lists of all files uploaded and external links added across that company's task activities. Files can be downloaded via a signed URL; links open in a new tab. Both lists show the linked subscription and task context. |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | Company Overview Details tab (company info); Delivery Overview (`/delivery/overview`) for subscription progress; `sleek-service-delivery-api` backend for company search and task-activity queries; `sleek-back-api` for company details; `sleek-companies-house-api` (UK only) for Companies House enrichment |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery-api (backend, external) |
| **DB - Collections** | Unknown — data served via `sleek-service-delivery-api`; no direct DB access from this frontend |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. What is the actual `sleek-service-delivery-api` backend repo and its DB schema for task activities? 2. The "Company Tasks" tab is temporarily hidden (commented out in JSX) — is it planned, abandoned, or gated behind a flag? 3. Are there file-size or file-type restrictions enforced server-side? 4. Signed file URL TTL / access control details are unknown. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- Route: `delivery/company-overview` — `src/App.jsx:193`
- Component: `src/pages/Delivery/CompanyOverview.jsx`

### Company search
- `sleekServiceDeliveryApi.getAllCompanies({ search, limit, page })` — `GET /companies?search=…`
- Debounced at 300 ms; results shown in a MUI Popper dropdown (`CompanyOverview.jsx:92–116`)

### Company details (Details tab)
- `sleekBackApi.getCompanyDetails(company.external_ref_id)` — external CRM/back-office API
- UK platform: additionally calls `sleekCompaniesHouseApi.getCompany(uen)` for Companies House enrichment (`CompanyOverview.jsx:193–198`)
- Platform detected from `localStorage.billingConfig.platform` (values: `sg`, `hk`, `au`, `uk`)
- Rendered by `CompanyOverviewDetails` → `CompanyOverviewDetailsAU/HK/UK` sub-components

### Files tab
- `sleekServiceDeliveryApi.getCompanyTaskActivities(companyId, { activityTypes: ["FILE", "COMMENT_AND_FILE"], page, limit: 8, sortBy: "updatedAt", sortOrder: "DESC" })`
- API endpoint: `GET /companies/{companyId}/task-activities?activityTypes=FILE&activityTypes=COMMENT_AND_FILE&…`
- `service-delivery-api.js:323–341`
- Columns displayed: Name (`activity.fileName` / `activity.content`), Last edited, Linked subscription, Linked task, Download action
- Download: `sleekServiceDeliveryApi.getTaskActivityFileUrl(activityId)` → `GET /task-activities/{activityId}/file-url` returns a signed URL opened in a new tab (`CompanyOverview.jsx:519`)

### Links tab
- Same `getCompanyTaskActivities` call with `activityTypes: ["LINK"]`
- Columns: Name (`activity.linkTitle` / `activity.linkUrl`), Last edited, Linked subscription, Linked task
- Link renders as `<a target="_blank">` to `activity.linkUrl` (`CompanyOverview.jsx:495–504`)

### Pagination
- 8 items per page; MUI `Pagination` with first/last buttons
- Total count sourced from `res.data.meta.total` (falls back through several shapes)

### Hidden "Company Tasks" tab
- `TAB_COMPANY_TASKS = "company-tasks"` constant defined but tab `<Tab>` is commented out (`CompanyOverview.jsx:402`)
- If activated, it would show a placeholder table of deliverable/task/label/status/due-date/assignee rows — hardcoded mock data only
