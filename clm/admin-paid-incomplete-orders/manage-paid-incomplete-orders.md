# Manage Paid Incomplete Orders

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Paid Incomplete Orders |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Corp Sec agents) |
| **Business Outcome** | Ensures companies that have paid but stalled in onboarding are actioned by Corp Sec, reducing revenue leakage and driving order completion. |
| **Entry Point / Surface** | Sleek Admin > Dashboard > Paid Incomplete Orders (`/admin/paid-incomplete-orders/`) |
| **Short Description** | Admin dashboard listing companies with `paid_and_awaiting_company_detail` status. Allows a Corp Sec agent to be assigned to each company and a contact status (Pending Customer, Pending Sleek, Partial Payment, Blocked by WF) to be set, with pagination, sorting, search by company name, and a view of the latest comment per company. Assigning an agent also propagates the assignee to active Camunda deadline workflow tasks. |
| **Variants / Markets** | SG, HK, GB (GB applies an extra `appOnboardingVersion: "Beta"` filter) |
| **Dependencies / Related Flows** | Company Overview page (`/admin/company-overview/`) for drill-down and comment history; Sleek Workflow / Camunda deadlines engine (agent assignment side-effect via `updateExistingDeadlineAssigneesViaStaffAssigned`); Resource Allocation system; Corp Sec admin group membership |
| **Service / Repository** | sleek-website |
| **DB - Collections** | companies (read/update via `retrieveCompanyData`, `editCompany`); resource_allocations (read/write via `getCompanyResourceAllocation`, `updateCompanyResourceAllocation`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `PAID_INCOMPLETE_ORDER_AGENT` constant is named `"sales-backup"` — likely a legacy label; confirm whether this is intentional or should be renamed to reflect Corp Sec ownership. AU/UK market support is not confirmed in code — only GB special-casing is evident. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/views/admin/paid-incomplete-orders/index.js` — React page component (`PaidIncompleteOrdersView`), mounted via `domready` into `#root`. Accessible from `/admin/dashboard` via back-navigation.

### Company data fetch
- `api.retrieveCompanyData({ query: { status: "paid_and_awaiting_company_detail", removeEmptyNames: true, requestFrom: "paidIncompleteOrderPage", ... } })` — fixed status filter identifies paid-but-stalled companies.
- GB tenant adds `appOnboardingVersion: "Beta"` to the query (line 127–129).
- Pagination: 20 per page; sort by `name` or `createdAt`.

### Agent assignment
- `PAID_INCOMPLETE_ORDER_AGENT_GROUP = ["Corp Sec"]` (`src/utils/company-order-constants/incomplete-order.js:46`) — only Corp Sec group members appear in the agent dropdown.
- `PAID_INCOMPLETE_ORDER_AGENT = "sales-backup"` (line 47) — resource allocation key written on update (note: legacy naming).
- `api.updateCompanyResourceAllocation(company._id, { resourceAllocation: { "sales-backup": agentId } })` — persists the agent.
- Side effect: `updateExistingDeadlineAssigneesViaStaffAssigned(company, platformConfig)` — fetches active Camunda `deadlines` workflows for the company and re-assigns `ACCOUNTANT_STEPS` and `TAX_EXECUTIVE_STEPS` tasks to the matching staff (accounting team lead / junior accountant / tax executive) via Camunda `updateAssignee` API.

### Contact status
- `PAID_INCOMPLETE_ORDER_CONTACT_STATUS` (line 24–41, `incomplete-order.js`): `pendingCustomer`, `pendingSleek`, `partialPayment`, `blockedByWf`.
- `api.editCompany(company._id, { contact_status: value })` — persists selected status on the company document.

### Comment display
- `company.comments[0].text` — latest comment shown inline; full history linked to `/admin/company-overview/?cid=…&openCommentHistory=true`.

### Camunda / Sleek Workflow service
- `src/views/admin/sleek-workflow/services/services.js` — `updateExistingDeadlineAssigneesViaStaffAssigned` queries `getSleekWorkflowProcesses` for active deadline workflows, fetches task lists via `getProcessTaskList`, and calls `updateAssignee` for each matching task.
