# Pay Invoice with Bank Account

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Pay Invoice with Bank Account |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (invoice recipient; unauthenticated — accesses via tokenized payment link) |
| **Business Outcome** | Allows customers to settle an outstanding invoice via bank transfer from a shared payment link, capturing payment intent and delivering bank transfer instructions by email without requiring card credentials. |
| **Entry Point / Surface** | External payment portal > Invoice payment link > Pay with Bank Transfer |
| **Short Description** | Customer submits bank payment intent through a tokenized payment link. The service validates the payment token, applies any coupon or credit balance, syncs the invoice to Xero, updates the payment token status to `PAY_BY_BANK`, and dispatches a bank transfer instruction email via the task queue. |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | Payment Token (authorization), Invoice service (coupon & credit balance application, Xero sync), Task/Email service (bank transfer instruction email), Customer & User creation (beta onboarding path), Audit Logs |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | Invoice, PaymentToken, Customer, User, Company, Task, AuditLogs |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Endpoint has no `@Auth()` guard — authorization relies entirely on `paymentToken`; confirm this is intentional for the external payment portal. Response DTO includes `paymentId` but the service does not populate it — may be vestigial. Which frontend surfaces render this payment flow (CLM admin, customer portal, or both)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `POST /v2/payment/pay-with-bank` — `PaymentV2Controller.payWithBank()` (`payment/controllers/payment-v2.controller.ts:95`)
- No `@Auth()` decorator; authorization is token-based via `paymentToken` in the request body
- `app-origin` header drives `clientType` (market-specific config)

### Request DTO (`pay-with-bank.request-v2.dto.ts`)
- `paymentToken` — required in practice; used to look up the invoice and authorize the payment
- `paymentType` — enum: `auto_renewal`, `manual_renewal`, `payment_request`, `onboarding`, etc.
- `paymentMethodType` — defaults to `bank_transfer`; stored on payment token
- `email`, `firstName`, `lastName` — used for user creation on beta onboarding path
- `couponCode`, `isApplyCreditBalance` — optional discount / credit application
- `sendInstructionEmail` — optional override for email dispatch

### Response DTO (`pay-with-bank.response.dto.ts`)
- Returns `invoice` object: `_id`, `number`, `url`, `totalAmount`, `status`, `invoiceOrigin`
- `paymentId`, `paymentMethod`, `paymentStatus` fields present but not populated by service (likely vestigial)

### Service logic (`payment-v2.service.ts:753–878`)
1. Validates `paymentToken` → resolves linked invoice
2. Beta onboarding path: creates or associates a user (`userService.getOrCreateUserByEmail`) and draft company (`createDraftCompany`) if invoice has no `userId`/`companyId`
3. `invoiceService.markCouponAndCreditBalanceAsUsed(invoice)` — applies discounts
4. `invoiceService.updateOrCreateInvoice({ isCreateXeroInvoice: true })` — syncs invoice to Xero
5. `taskService.createTask({ name: 'sendEmail', emailTemplateId: EmailTemplate.manual_payment_bank_transfer })` — queues bank transfer instruction email
6. `paymentTokenRepository.updateById(…, { status: PaymentTokenStatus.PAY_BY_BANK })` — marks token as bank-pay intent captured
7. `auditLogsService.addAuditLog(…)` — records action with tags `['payment-v2', 'pay-with-bank']`

### External systems
- **Xero** — invoice synced via `isCreateXeroInvoice: true` flag in `InvoiceService`
- **Task queue** — email dispatch is async via `TaskService` (not direct SMTP)

### Collections touched
| Collection | Operation |
|---|---|
| `Invoice` | Read (via payment token), `updateById` (attach userId/companyId on onboarding), `updateOrCreateInvoice` |
| `PaymentToken` | Read (validate token), `updateById` (set `PAY_BY_BANK` status) |
| `Customer` | Read + `updateCustomer` (onboarding path: switch type to `company`) |
| `User` | Read / create via `getOrCreateUserByEmail` |
| `Company` | Create draft company on beta onboarding path |
| `Task` | Create (queue bank transfer instruction email) |
| `AuditLogs` | Create |
