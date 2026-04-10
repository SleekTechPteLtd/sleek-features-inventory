# Track Service Delivery

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Track Service Delivery |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal operator) |
| **Business Outcome** | Enables ops teams to record and monitor fulfillment progress on active subscriptions by marking individual deliverables and overall subscriptions as delivered, in-progress, or reverted — providing visibility into service completion state. |
| **Entry Point / Surface** | Sleek App > CLM > Subscriptions > Delivery Status (ops-facing internal tools) |
| **Short Description** | Operators update service delivery status at both the deliverable level and the subscription level. When all deliverables under a subscription are marked delivered, the subscription's delivery status auto-rolls up to delivered. Subscriptions grouped by financial year end and item code are updated in bulk. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Subscription Config (grouping criteria: same_fye, same_item_code) — `subscriptions-config` module; Audit Logs — `auditLogsService`; Service Delivery repository — `servicedeliveries` collection |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | customersubscriptions, servicedeliveries |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which UI surface triggers these updates (delivery tracker, subscription detail page, or both)? Is the `PUT /:id/update-delivery-status` endpoint a newer direct override path vs the granular deliverable-level `update-service-delivery-status`? Markets served not determinable from code alone. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| `PUT` | `/customer-subscriptions/update-service-delivery-status` | `@Auth()` | Updates a single service delivery item's status; rolls up to subscription if all deliverables are done |
| `PUT` | `/customer-subscriptions/:id/update-delivery-status` | `@Auth()` | Directly sets the subscription-level `serviceDeliveryStatus` with a mandatory reason string |

### Service methods

- **`updateServiceDeliveryStatus`** (`customer-subscription.service.ts:740`)
  - Accepts `serviceDeliveryId`, `deliveryStatus`, `serviceDeliveryReason`
  - Sets `deliveryStatus`, `completionDate`, `deliveredByUserId`, `deliveredByUserEmail` on the `ServiceDelivery` record
  - Checks if all sibling deliverables are delivered → if yes, updates `customerSubscription.serviceDeliveryStatus = delivered` and sets `serviceDeliveryDate`; otherwise resets to `active`
  - Calls `updateServiceDeliveryBySameFyeAndItemCode` to propagate status to related subscriptions sharing the same financial year end and service item code (governed by `subscriptionConfigService.getServiceDetail` → `subscriptionGroupingCriteria`)
  - Emits audit log via `auditLogsService` for both the deliverable-level and subscription-level transitions

- **`updateSubscriptionDeliveryStatus`** (`customer-subscription.service.ts:1816`)
  - Accepts `deliveryStatus` (enum) + `reason` (required string)
  - Directly writes `serviceDeliveryStatus` on the `CustomerSubscription` document
  - Emits audit log with `oldValue` / `newValue` for the status change

### Schema

**`ServiceDeliveryStatus` enum** (`customer-subscription.schema.ts:13`):
`none` | `active` | `inactive` | `delivered` | `discontinued`

**`CustomerSubscription` fields touched:**
- `serviceDeliveryStatus: ServiceDeliveryStatus` (indexed, compound-indexed with `companyId`)
- `serviceDeliveryDate: Date`

**`ServiceDelivery` fields touched:**
- `deliveryStatus: ServiceDeliveryStatus`
- `completionDate: Date | null`
- `deliveredByUserId: ObjectId | null`
- `deliveredByUserEmail: string | null`
- `serviceDeliveryReason: string`

### File paths

- `src/customer-subscription/controllers/customer-subscription.controller.ts` — route definitions (`updateServiceDeliveryStatus` at line 79, `updateSubscriptionDeliveryStatus` at line 221)
- `src/customer-subscription/services/customer-subscription.service.ts` — business logic
- `src/customer-subscription/models/service-delivery.schema.ts` — ServiceDelivery Mongoose schema
- `src/customer-subscription/models/customer-subscription.schema.ts` — CustomerSubscription schema, ServiceDeliveryStatus enum
- `src/customer-subscription/dtos/update-service-delivery-status.dto.ts`
- `src/customer-subscription/dtos/update-subscription-delivery-status.dto.ts`
