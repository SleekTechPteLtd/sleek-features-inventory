# Review Unpaid Incomplete Orders

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Unpaid Incomplete Orders |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Sales / Sales Admin agents) |
| **Business Outcome** | Gives sales teams visibility into companies that began onboarding but never completed payment, enabling targeted follow-up to convert stalled prospects into paying customers. |
| **Entry Point / Surface** | Sleek Admin > Dashboard > Unpaid Incomplete Orders (`/admin/incomplete-orders/`) |
| **Short Description** | Admin dashboard listing companies with `draft` status that have a non-empty name, indicating they started but did not complete payment. Allows a Sales agent to be assigned to each company and a contact status (Not contacted, Left message, Call back another time, Customer went elsewhere, Others) to be set, with pagination, sorting by company name or date started, search by company name, and a view of the latest comment per company. Assigning an agent also propagates the assignee to active Camunda deadline workflow tasks. |
| **Variants / Markets** | SG, HK, GB (GB applies an extra `appOnboardingVersion: "Beta"` filter) |
| **Dependencies / Related Flows** | Company Overview page (`/admin/company-overview/`) for drill-down and comment history; Sleek Workflow / Camunda deadlines engine (agent assignment side-effect via `updateExistingDeadlineAssigneesViaStaffAssigned`); Resource Allocation system; Sales and Sales Admin group membership |
| **Service / Repository** | sleek-website |
| **DB - Collections** | companies (read/update via `retrieveCompanyData`, `editCompany`); resource_allocations (read/write via `updateCompanyResourceAllocation`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | AU/UK market support is not confirmed in code — only GB special-casing is evident. The `requestFrom: "unpaidIncompleteOrderPage"` param suggests server-side filtering logic specific to this view — confirm what additional filtering the backend applies beyond `status: "draft"`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/views/admin/incomplete-orders/index.js` — React page component (`IncompleteOrdersView`), mounted via `domready` into `#root`. Accessible from `/admin/dashboard` via back-navigation.

### Company data fetch
- `api.retrieveCompanyData({ query: { status: "draft", removeEmptyNames: true, requestFrom: "unpaidIncompleteOrderPage", ... } })` — fixed status filter identifies companies that started but never paid.
- GB tenant adds `appOnboardingVersion: "Beta"` to the query (line 127–129).
- Pagination: 20 per page; sort by `name` or `createdAt`.

### Agent assignment
- `UNPAID_INCOMPLETE_ORDER_AGENT_GROUP = ["Sales", "Sales Admin"]` (`src/utils/company-order-constants/incomplete-order.js:43`) — only Sales and Sales Admin group members appear in the agent dropdown.
- `UNPAID_INCOMPLETE_ORDER_AGENT = "sales-in-charge"` (line 44) — resource allocation key written on update.
- `api.updateCompanyResourceAllocation(company._id, { resourceAllocation: { "sales-in-charge": agentId } })` — persists the agent.
- Side effect: `updateExistingDeadlineAssigneesViaStaffAssigned(company, platformConfig)` — fetches active Camunda `deadlines` workflows for the company and re-assigns relevant tasks to the matching staff via Camunda `updateAssignee` API.

### Contact status
- `UNPAID_INCOMPLETE_ORDER_CONTACT_STATUS` (lines 1–22, `incomplete-order.js`): `notContacted`, `leftMessage`, `callBackAnotherTime`, `customerWentElsewhere`, `others`.
- `api.editCompany(company._id, { contact_status: value })` — persists selected status on the company document.

### Comment display
- `company.comments[0].text` — latest comment shown inline; full history linked to `/admin/company-overview/?cid=…&openCommentHistory=true`.

### Camunda / Sleek Workflow service
- `src/views/admin/sleek-workflow/services/services.js` — `updateExistingDeadlineAssigneesViaStaffAssigned` is called after every agent assignment to keep Camunda task assignees in sync.
