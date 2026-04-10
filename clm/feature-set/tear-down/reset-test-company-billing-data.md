# Reset test company billing data

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Reset test company billing data |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (automated test runner) |
| **Business Outcome** | Ensures automated integration tests start from a clean billing state by wiping all billing records for test companies, preventing test pollution and false failures between test runs. |
| **Entry Point / Surface** | Internal test infrastructure — `POST /api/tear-down` (no auth guard; expected to be network-restricted to non-production environments) |
| **Short Description** | Accepts a `companyId`, verifies the company exists and its name contains `AUTOTESTCOM`, then hard-deletes all billing records (subscriptions, invoices, payment methods, payment tokens, customers, coupon usages) scoped to that company. Returns per-collection deletion counts. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | CompanyService (company lookup and test-company guard); consumed by automated E2E / integration test suites |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | customerSubscriptions, invoices, paymentMethods, paymentTokens, customers, couponUsages |
| **Evidence Source** | codebase |
| **Criticality** | Low |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | No authentication guard on the controller — is this endpoint protected at the network/ingress level? Is it only deployed in non-production environments? Is the `AUTOTESTCOM` name convention enforced by test setup tooling? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `src/tear-down/tear-down.controller.ts` — `POST /api/tear-down`, no `@UseGuards` decorator; delegates to `TearDownService.tearDownByCompanyId(dto)`
- `src/tear-down/dto/tear-down-request.dto.ts` — single input field `companyId` (MongoDB ObjectId, validated with `@IsMongoId`)
- `src/tear-down/tear-down.service.ts`:
  - Calls `CompanyService.getCompanyDetails(dto.companyId)` — throws `UnauthorizedException` if company not found
  - Safety guard: `company.name.toUpperCase().includes('AUTOTESTCOM')` — throws `UnauthorizedException` for non-test companies
  - `CustomerSubscriptionRepository.deleteMany({ companyId })` → customerSubscriptions collection
  - `InvoiceRepository.deleteMany({ companyId })` → invoices collection
  - `PaymentMethodRepository.deleteMany({ companyId })` → paymentMethods collection
  - `PaymentTokenRepository.deleteMany({ companyId })` → paymentTokens collection
  - `CustomerRepository.deleteMany({ referenceId: companyId })` → customers collection (note: keyed on `referenceId`, not `companyId`)
  - `CouponUsageRepository.deleteMany({ companyId })` → couponUsages collection
  - Returns `{ deletedSubscriptions, deletedInvoices, deletedPaymentMethods, deletedPaymentTokens, deletedCustomers, deletedCouponUsages }` with per-collection deletion counts
