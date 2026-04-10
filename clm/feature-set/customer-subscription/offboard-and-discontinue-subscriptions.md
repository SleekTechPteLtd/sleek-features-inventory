# Offboard and Discontinue Subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Offboard and Discontinue Subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal operator) |
| **Business Outcome** | Enables internal operators to formally end a customer subscription engagement — either by flagging it as pending-offboard (with a documented reason) or fully discontinuing it — so that service delivery and billing lifecycle are correctly closed out with an auditable trail. |
| **Entry Point / Surface** | Internal Ops Portal → Subscriptions management → offboard or discontinue action on a specific subscription |
| **Short Description** | Two-step end-of-engagement workflow: `offboard` marks the subscription as `toOffboard` with a mandatory reason string; `discontinue` advances the status to `discontinued`. Both actions are written to the audit log and trigger automatic task-status updates in service-delivery-api via a MongoDB change stream listener. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `AuditLogsService` (audit trail per action); `service-delivery-api` change stream listener (automatically syncs downstream task status on subscription status change); `reactivateSubscription` (reverse flow to undo offboarding); `archive-company` service (also sets `discontinued` status when a company is churned or struck off) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | customersubscriptions |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | No market-specific branching is visible in these methods — unclear if geography restricts these operations. Both endpoints use only the standard `@Auth()` guard with no role/group restriction; unclear which internal roles are permitted to trigger offboard vs discontinue in the UI. The `toOffboard` → `discontinued` transition appears to be a manual two-step process (two separate API calls), but no guard enforces that offboard must precede discontinue. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Endpoints

| Method | Path | Guard | DTO |
|---|---|---|---|
| `PUT` | `/customer-subscriptions/:id/offboard` | `@Auth()` | `OffboardSubscriptionDto` (`serviceDeliveryOffboardingReason: string`) |
| `PUT` | `/customer-subscriptions/:id/discontinue` | `@Auth()` | _(none — body not required)_ |

Source: `customer-subscription/controllers/customer-subscription.controller.ts:148–184`

### Service logic

**`offboardSubscription`** (`customer-subscription.service.ts:1061–1094`):
- Looks up subscription by `id`; throws `NotFoundException` if missing.
- Calls `customerSubscriptionRepository.updateById(id, { serviceDeliveryStatus: ServiceDeliveryStatus.toOffboard, serviceDeliveryOffboardingReason: "<reason> by <user.email>", serviceDeliveryReactivationReason: '' })`.
- Writes audit log: action `create`, text `offboarded the subscription (Reason: …)`, tags `['subscription', 'subscription-{id}']`, keyed by `companyId` and `userId`.

**`discontinueSubscription`** (`customer-subscription.service.ts:1096–1122`):
- Looks up subscription by `id`; throws `NotFoundException` if missing.
- Calls `customerSubscriptionRepository.updateById(id, { serviceDeliveryStatus: ServiceDeliveryStatus.discontinued })`.
- Writes audit log: action `create`, text `discontinued the subscription`, same tag/key pattern.
- Comment in code: _"Task status update in service-delivery-api is handled automatically by the mongoose hook in customer-subscription.schema.ts"_ — actual mechanism is a change stream listener, not a synchronous API call.

### Status enum values (relevant subset)

```typescript
// customer-subscription/models/customer-subscription.schema.ts
export enum ServiceDeliveryStatus {
  toOffboard   = 'toOffboard',    // set by offboardSubscription
  discontinued = 'discontinued',  // set by discontinueSubscription
  // other values: none, active, inactive, delivered, toBeStarted, deactivated
}
```

### Related flows

- `reactivateSubscription` (`PUT /:id/reactivate`) — reverses an offboard; sets status back and records a reactivation reason.
- `archive-company/archive-company.service.ts:44–47` — independently sets `discontinued` when company status is `churn` or `striked_off`, bypassing these endpoints.
- `AuditLogsService` is injected at service constructor level and called on every status-changing operation in the service.
- `ServiceDeliveryApiService` is injected but downstream task sync for offboard/discontinue flows through a MongoDB change stream, not a direct service call from these methods.

### Schema / collection

- Model class: `CustomerSubscription` (`customer-subscription/models/customer-subscription.schema.ts`)
- Mongoose collection: `customersubscriptions` (default pluralisation; no explicit `collection` override in `@Schema` decorator)
- Registered via `MongooseModule.forFeature([{ name: CustomerSubscription.name, schema: CustomerSubscriptionSchema }])`
