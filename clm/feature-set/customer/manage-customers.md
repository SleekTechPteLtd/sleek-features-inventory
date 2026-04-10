# Manage Customers

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Customers |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal operator / admin) |
| **Business Outcome** | Operators maintain a unified billing identity record per customer — linking individual users to Stripe and companies to Xero — so that downstream billing and bookkeeping systems can resolve the correct external account for every transaction. |
| **Entry Point / Surface** | Internal REST API — `POST /customers`, `PUT /customers/:id` (sleek-billings-backend) |
| **Short Description** | Allows authenticated operators to create and update customer records that bridge an internal reference identity (user or company) to its external billing counterpart: Stripe for individual users, Xero for companies. Supports three customer types: `user`, `company`, and `onboarding_user`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Stripe (stripeCustomerId, required for type=user); Xero (xeroContactId, required for type=company); downstream: invoice generation, billing reconciliation, bookkeeping flows; QueueService injected but not yet wired (planned event publishing) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `customers` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) Admin role guard is marked TODO — currently any authenticated user can create/update customers; intended access should be restricted to admin/operator roles. (2) QueueService is injected in the controller but unused — what events were planned (e.g. customer.created, customer.updated)? (3) `onboarding_user` type has no conditional billing ID requirement in the DTO — how is it used and what external system does it link to? (4) `referenceId` is a MongoDB ObjectId — which service/collection does it point to (user service, CRM)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Endpoints (`customer/controllers/customer.controller.ts`)
- `POST /customers` — `@Auth()` guard, calls `customerService.createCustomer(dto)`
- `PUT /customers/:id` — `@Auth()` guard, calls `customerService.updateCustomer(id, dto)`
- Both carry `// @TODO: check admin role` — role enforcement is incomplete
- `QueueService` injected but not called in any route handler

### Service (`customer/services/customer.service.ts`)
- `createCustomer(dto)` → `customerRepository.create(dto)`
- `updateCustomer(id, dto)` → `customerRepository.updateById(id, dto)`
- Additional internal lookup methods (not exposed via controller): `getCustomerDetail`, `getCustomerByReferenceId`, `getCustomerByParams`, `getCustomerByXeroContactId` — consumed by other modules

### Create DTO (`customer/dtos/create-customer.request.dto.ts`)
- Required: `referenceId` (MongoId), `type` (enum: user | company | onboarding_user)
- Conditional: `stripeCustomerId` required when `type === 'user'`
- Conditional: `xeroContactId` required when `type === 'company'`
- Optional: `email`, `firstName`, `lastName`, `middleName`

### Update DTO (`customer/dtos/update-customer.request.dto.ts`)
- All fields optional: `email`, `firstName`, `lastName`, `middleName`, `referenceId`, `xeroContactId`, `stripeCustomerId`, `type`

### Schema (`customer/models/customer.schema.ts`)
- Collection: `customers`
- Key fields: `referenceId` (ObjectId ref), `type` (user/company/onboarding_user), `stripeCustomerId` (users only), `xeroContactId` (companies only, sparse unique index), `migratedAt`, `address` (object)
- Compound unique index: `{ type, referenceId }` — one record per (type, reference entity)
- Timestamps: `createdAt`, `updatedAt`
