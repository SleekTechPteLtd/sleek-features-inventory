# Manage Sales Outreach for Incomplete Orders

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Sales Outreach for Incomplete Orders |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Sales / Sales Admin) |
| **Business Outcome** | Enables sales operators to coordinate follow-up on companies that started but did not complete an order, by assigning a responsible agent and tracking contact progress through a defined status workflow. |
| **Entry Point / Surface** | Sleek Admin > Unpaid Incomplete Orders (`/admin/incomplete-orders/`) |
| **Short Description** | Admin view listing companies with draft/unpaid incomplete orders. Operators assign a sales agent from the Sales or Sales Admin group to each company and record a contact status (Not Contacted, Left Message, Call Back Another Time, Customer Went Elsewhere, Others). Agent assignment propagates downstream to update Camunda deadline workflow task assignees for that company. |
| **Variants / Markets** | SG, HK, GB (UK Beta filtering is applied for GB tenant); AU Unknown |
| **Dependencies / Related Flows** | Sleek Workflow / Camunda (deadline workflows — agent assignment side-effect updates task assignees); Company Resource Allocation API; Company Comments (latest comment displayed inline); Company Overview page (deep-link per row) |
| **Service / Repository** | sleek-website |
| **DB - Collections** | companies (contact_status field, resourceAllocation embedded), resource_allocations |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Does contact_status persist on the company document itself or a separate collection? GB-specific `appOnboardingVersion: Beta` filter — is this the only market variant or are there more? Is there any reporting or analytics driven off the contact_status values? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/views/admin/incomplete-orders/index.js` — React SPA rendered into `#root`; Admin-only route.

### Data fetching
- `fetchCompanies()` — calls `api.retrieveCompanyData({ query: { status: "draft", removeEmptyNames: true, requestFrom: "unpaidIncompleteOrderPage" } })`. For GB tenant, additionally filters `appOnboardingVersion: "Beta"`.
- `fetchGroupsAndUsers()` / `getGroupUsers()` — fetches all admin groups then filters to groups named in `UNPAID_INCOMPLETE_ORDER_AGENT_GROUP` (`["Sales", "Sales Admin"]`), loading their member users as the agent picklist.

### Constants (`src/utils/company-order-constants/incomplete-order.js`)
- `UNPAID_INCOMPLETE_ORDER_CONTACT_STATUS`: `notContacted`, `leftMessage`, `callBackAnotherTime`, `customerWentElsewhere`, `others`
- `UNPAID_INCOMPLETE_ORDER_AGENT_GROUP`: `["Sales", "Sales Admin"]`
- `UNPAID_INCOMPLETE_ORDER_AGENT`: `"sales-in-charge"` (resource allocation type key)

### Agent assignment
- `handleAgentUpdate()` — calls `api.updateCompanyResourceAllocation(companyId, { resourceAllocation: { "sales-in-charge": userId } })`.
- After saving, triggers `handleDeadlinesWorkflowUpdate(company)` → `updateExistingDeadlineAssigneesViaStaffAssigned(company, platformConfig)` from `src/views/admin/sleek-workflow/services/services.js`.

### Camunda side-effect (`updateExistingDeadlineAssigneesViaStaffAssigned`)
- Queries Sleek Workflow for active/new deadline workflows for the company.
- For each workflow, fetches the Camunda task list and re-assigns accounting and tax-executive steps to the company's current staff (accounting-team-leader, accounting-bookkeeper, tax-executive) via `updateAssignee` (Camunda API).

### Contact status
- `handleContactStatusSelect()` — calls `api.editCompany(companyId, { contact_status: value })`, persisting the status directly on the company document.

### UI surface
- Table columns: Company Name (link to overview), Date Started, Package, Sales Agent (dropdown), Contact Status (dropdown), Comments (latest comment text + link to comment history).
- Supports search by company name and sort by name or createdAt.
- Pagination: 20 companies per page.
