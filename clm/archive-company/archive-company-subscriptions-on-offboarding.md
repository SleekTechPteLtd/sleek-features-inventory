# Archive company subscriptions on offboarding

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Archive company subscriptions on offboarding |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Ensures no billing or service delivery continues for a company that has exited the platform (archived, churned, or struck off), protecting revenue integrity and preventing unintended service obligations. |
| **Entry Point / Surface** | Internal API — `POST /archive-company`; triggered by offboarding workflows when a company's status transitions to `archived`, `churn`, or `striked_off` |
| **Short Description** | When a company is archived, churned, or struck off, the platform cancels all recurring subscriptions (disabling auto-renewal, setting renewal status to `cancelled`, clearing next renewal date) and deactivates or discontinues all non-recurring subscriptions based on company status. Audit logs are recorded per subscription for both cancellation and service delivery changes. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Company status management (CLM offboarding flow), AuditLogsService, CompanyService (reads company status), CustomerSubscriptionRepository; upstream: offboarding request approval that transitions company to `archived`/`churn`/`striked_off` |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `customersubscriptions` (read + bulk update), `auditlogs` (write per subscription) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Who calls this endpoint? Is it triggered automatically on company status change (e.g. by CLM backend or offboarding workflow) or manually invoked by ops? 2. Does this apply to all markets (SG, HK, AU, UK) or are any markets excluded? 3. The `@Auth()` guard is present but the caller identity is unclear — is this a service-to-service internal call or an admin-facing action? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/archive-company/archive-company.controller.ts:10–14` — `POST /archive-company`, protected by `@Auth()` decorator; accepts `ArchiveCompanyRequestDto` (single field: `companyId` MongoId)

### Core logic
- `src/archive-company/archive-company.service.ts:archiveCompanyByCompanyId`
  - Guards: validates company exists and status is one of `archived | striked_off | churn` (throws `UnauthorizedException` otherwise)
  - Fetches all `CustomerSubscription` docs for the company with `service` populated
  - Splits into **recurring** (`service.recurring === true`) and **non-recurring** groups

#### Recurring subscription updates
- Always applied: `isAutoRenewalEnabled=false`, `subscriptionRenewalStatus=cancelled`, `subscriptionCancelledBy='system'`, `nextRenewalDate=null`
- Conditionally (only when not already cancelled): `subscriptionCancellationReason`, `subscriptionCancellationDate`
- Conditionally (only when delivery status differs): `serviceDeliveryStatus` (`deactivated` for `archived`; `discontinued` for `churn`/`striked_off`), `serviceDeliveryOffboardingReason`

#### Non-recurring subscription updates
- Always applied: `isAutoRenewalEnabled=false`, `subscriptionRenewalStatus=none`, `nextRenewalDate=null`
- Conditionally (only when status differs from `none`): `subscriptionCancellationReason`
- Conditionally (only when delivery status differs): `serviceDeliveryStatus`, `serviceDeliveryOffboardingReason`

### Audit logging
- One `AuditLogAction.update` log per subscription with a **cancellation** change, tagged: `['subscription', 'subscription-{id}', 'archive-company', 'subscription-cancelled', 'company-{id}']`
- One `AuditLogAction.update` log per subscription with a **service delivery** change, tagged: `['subscription', 'subscription-{id}', 'archive-company', 'service-delivery-updated', 'company-{id}']`

### Schemas / collections
- `CustomerSubscription` schema — `src/customer-subscription/models/customer-subscription.schema.ts`; key enums: `ServiceDeliveryStatus` (`deactivated`, `discontinued`), `SubscriptionRenewalStatus` (`cancelled`, `none`)
- Module registered against `SleekPaymentDB` connection — `src/archive-company/archive-company.module.ts:16–19`

### Status constants
- `COMPANY_STATUS.archived`, `COMPANY_STATUS.striked_off`, `COMPANY_STATUS.churn` — `src/shared/consts/common.ts:224–229`
