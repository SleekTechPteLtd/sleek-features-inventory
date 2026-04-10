# Track client onboarding progress

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM (Client Lifecycle Management) |
| **Feature Name** | Track client onboarding progress |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations Staff |
| **Business Outcome** | Gives operations staff a centralized view of active client onboarding workflows so they can monitor status, assignee, and timelines to ensure new clients are set up on time |
| **Entry Point / Surface** | Sleek Billings App > Billing > Onboarding (`/onboarding`) |
| **Short Description** | Displays a searchable list of client onboarding workflows showing each client's status, assigned staff member, start date, and target completion date. UI is complete but currently renders hardcoded sample data — backend integration is pending. |
| **Variants / Markets** | SG, HK, AU (inferred from subscription priority labels in SDS; no UK-specific onboarding logic found) |
| **Dependencies / Related Flows** | Staff role types `AUDIT_ONBOARDING_IC` and `ACCOUNTING_ONBOARDING_IC` (SDS team assignments); `onboardedFor` field on company records (`CompanyOverviewDetails`); Offboarding module (counterpart workflow); `sleek-service-delivery-api` subscriptions/deliverables/tasks API (backend integration pending) |
| **Service / Repository** | sleek-clm-monorepo / sleek-billings-frontend (UI); sleek-service-delivery-api (likely backend — subscriptions, deliverables, tasks data) |
| **DB - Collections** | Backend integration not yet wired; when implemented, expected PostgreSQL tables: `subscriptions` (status, start/end dates), `deliverables`, `tasks`, `team_assignments` (assigned staff), `companies` (client name) — all in sleek-service-delivery-api |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Low |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service will supply onboarding workflow data (SDS or a dedicated onboarding service)? What actions are available via the per-row ellipsis menu (not implemented)? Will search filter server-side or client-side? Is this feature currently visible to operations staff in production? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/pages/Onboarding/OnboardingList.jsx`** — sole UI file for this feature; renders a table with columns: Client Name, Status (badge), Start Date, Assigned To, Completion Date, Actions (ellipsis button). Search input is present but filters nothing (data is hardcoded). Explicit code comment: `// Sample data - replace with actual data from your backend`.
- **`src/App.jsx:161`** — route `<Route path="onboarding" element={<OnboardingList />} />` under `MasterLayout`; loaded lazily.
- **`src/components/Navbar.jsx:122`** — nav entry: Billing > Onboarding (`/onboarding`, `UserGroupIcon`).
- **`src/lib/constants.jsx:367,376`** — role types `AUDIT_ONBOARDING_IC = 'Audit Onboarding I/C'` and `ACCOUNTING_ONBOARDING_IC = 'Accounting Onboarding I/C'`, used in `src/pages/Delivery/TeamAssignments.jsx:51,62` — staff with these roles exist in the SDS system and are candidates to appear in the "Assigned To" column.
- **`src/pages/Delivery/CompanyOverviewDetails.jsx:29,113,147`** — `onboardedFor` field tracked on company records, suggesting an onboarding state is already stored per company in the SDS/delivery layer.
- No API service calls to any backend endpoint for onboarding data were found; `src/services/api.js`, `service-delivery-api.js`, and `sleek-back-api.js` contain no onboarding-specific methods.
- **`sleek-service-delivery-api/src/subscriptions/entities/subscription.entity.ts`** — `ServiceDeliveryStatus` enum includes `toBeStarted` (likely the status for new onboarding clients); `SubscriptionPriorityLabel` has SG, HK, AU-specific labels — no UK labels, confirming SG/HK/AU markets.
- **`sleek-service-delivery-api/src/deliverables/entities/deliverable.entity.ts`** — `DeliverableStatus` enum: `PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `ARCHIVED` — maps to the onboarding status column in the UI.
- **`sleek-service-delivery-api/src/tasks/entities/task.entity.ts`** — tasks have `assignedUserId`, `dueDate`, `taskStartDate`, `taskEndDate` — fields that would back the Start Date / Completion Date / Assigned To columns.
- **`sleek-service-delivery-api/src/common/enums/role-type.enum.ts`** — `AUDIT_ONBOARDING_IC` and `ACCOUNTING_ONBOARDING_IC` role types confirm these roles exist in the SDS user model.
- **`sleek-service-delivery-api/docs/ENTITY_DOCUMENTATION.md`** — system overview confirms the Subscription → Deliverable → Task hierarchy as the delivery model for client work. New client onboarding would follow this path with a subscription `serviceDeliveryStatus` of `toBeStarted`.

## Unknown columns — reasons

| Column | Reason |
|---|---|
| **DB - Collections** | No backend integration wired in the frontend yet; expected tables identified from SDS entity model but not confirmed as the actual data source |
