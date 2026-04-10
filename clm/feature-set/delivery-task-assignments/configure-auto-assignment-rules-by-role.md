# Configure Auto-Assignment Rules by Role

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Configure Auto-Assignment Rules by Role |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Delivery Operator |
| **Business Outcome** | New companies are automatically assigned to the right team member for each service role, eliminating manual assignment overhead at client onboarding time. |
| **Entry Point / Surface** | Sleek Admin App > Delivery > Company Assignment > Page menu (⋮) > Manage auto-assignment (side drawer) |
| **Short Description** | Delivery operators open a drawer from the Company Assignment page to set a default assignee per role (e.g. Team Lead, Accountant IC, Bookkeeper, Tax IC, Corporate Secretary IC). When a new company is created, the service-delivery-api applies these defaults automatically without manual intervention. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Manual team assignment per company per role (same TeamAssignments page); Company Overview (displays resulting assignments); service-delivery-api `/auto-assignments` resource |
| **Service / Repository** | sleek-billings-frontend, service-delivery-api |
| **DB - Collections** | Unknown (managed by service-delivery-api backend; no schema files in frontend repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Is auto-assignment applied server-side at company-creation time or via a background job? What happens when no default is configured for a role — is the slot left unassigned silently? Are all markets in scope or only SG? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Component
`src/pages/Delivery/TeamAssignments.jsx`

- Route: `/delivery/task-assignments` (App.jsx:197); nav label "Company Assignment" (nav-rail-items.js:146–148)
- State: `openAutoAssignmentDrawer`, `autoAssignmentsMap` (keyed by `roleType`), `originalAutoAssignmentsMap`, `autoAssignmentEditModeSet` (lines 135–141)
- `rolesForAutoAssignment` (line 177) = all roles across five `ROLE_CATEGORIES`: General, Accounting, Audit, Tax, Corporate Secretary — spanning roles such as `TEAM_LEAD`, `ACCOUNTING_ONBOARDING_IC`, `ACCOUNTANT_IC`, `BOOKKEEPER`, `AUDIT_IC`, `TAX_IC`, `CORPORATE_SECRETARY_IC`, etc.
- `fetchAutoAssignments()` (line 290): calls `getAutoAssignments()`, builds map from `roleType → { ...assignedUser, autoAssignmentId }`.
- `handleSaveAutoAssignments()` (line 990): iterates roles and fans out parallel API calls — `createAutoAssignment`, `updateAutoAssignment`, or `deleteAutoAssignment` — depending on diff between `originalAutoAssignmentsMap` and `autoAssignmentsMap`. Payloads include `roleType`, `assignedUserId`, `createdBy` / `updatedBy`.
- Success toast: `"Auto assignments saved successfully"` (line 1031).
- Entry: "Manage auto-assignment" menu item (line 1860) opens the drawer.

### Service
`src/services/service-delivery-api.js`

- `GET  /auto-assignments` — `getAutoAssignments()` (line 693)
- `POST /auto-assignments` — `createAutoAssignment(data)` (line 702); payload: `{ roleType, assignedUserId, createdBy }`
- `PATCH /auto-assignments/:id` — `updateAutoAssignment(id, data)` (line 711); payload: `{ assignedUserId, updatedBy }`
- `DELETE /auto-assignments/:id` — `deleteAutoAssignment(id)` (line 720)
- Auth: Bearer JWT or legacy token via `Authorization` header; `App-Origin: admin` or `admin-sso`.

### Market signals
Market-specific company detail pages exist for AU (`CompanyOverviewDetailsAU.jsx`), HK (`CompanyOverviewDetailsHK.jsx`), UK (`CompanyOverviewDetailsUK.jsx`), implying the Delivery module — and by extension auto-assignment — covers all four markets.
