# Create Customer-Requested Invoice

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Create Customer-Requested Invoice |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Billing Ops / Admin) |
| **Business Outcome** | Allows Sleek operators to fulfill ad-hoc billing requests from customers — such as upsells or one-time purchases — outside the normal subscription renewal cycle, generating a payment link the customer can use to pay immediately. |
| **Entry Point / Surface** | Sleek Billings Admin App > Invoices (operator-initiated action; customer pays via returned payment token link) |
| **Short Description** | An operator selects a company and a service, optionally specifies purpose of purchase and an existing subscription, and the system creates a new invoice (origin: `customerRequest`) synced to Xero, then returns a payment token the operator can share with the customer. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero (invoice creation/sync via `XeroService`); PaymentToken service (generates shareable payment link); Company service (validates company exists); Service/product catalog (`ServiceRepository`); downstream payment flow (customer uses token to pay) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `invoices`, `services`, `paymenttokens` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/jurisdictions support this flow? Is `purposeOfPurchase` enforced to a fixed set of values beyond the default `"upsell"`? What is the `taskDetails` field used for downstream — is it linked to a task management system? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `POST /invoices/customer-request` — `InvoiceController.createCustomerRequestInvoice`
- Auth: `@Auth()` (standard JWT; no additional `@GroupAuth` restriction — any authenticated operator)

### Controller
```ts
// invoice/controllers/invoice.controller.ts:197–204
@Post('customer-request')
@Auth()
async createCustomerRequestInvoice(
  @Body() payload: CreateCustomerRequestInvoiceRequestDto,
  @Req() req: ExtendedRequest,
): Promise<CreateCustomerRequestInvoiceResponseDto> {
  return this.invoiceService.createCustomerRequestInvoice(payload, req.user);
}
```

### Request DTO
```ts
// invoice/dtos/create-customer-request-invoice.dto.ts
class CreateCustomerRequestInvoiceRequestDto {
  companyId: string;          // required
  serviceId: string;          // required
  taskDetails?: object;       // optional — stored on payment token
  purposeOfPurchase?: string; // optional — defaults to "upsell"
  existingSubscriptionId?: string; // optional — linked subscription context
}
// Response: { paymentToken: string }
```

### Service logic
```ts
// invoice/services/invoice.service.ts:2351–2401
async createCustomerRequestInvoice(payload, reqUser) {
  // 1. Validate company exists
  const company = await this.companyService.getCompanyDetails(companyId);

  // 2. Fetch service from catalog
  const service = await this.serviceRepository.findById(serviceId);

  // 3. Build invoice items (qty=1, price from service, purposeOfPurchase data)
  const items: InvoiceItem[] = [{ itemId, code, name, quantity: 1, price, ... }];

  // 4. Create/sync invoice via updateOrCreateInvoice (calls XeroService internally)
  const invoiceData = {
    title: `Adhoc Request - ${company.name}`,
    items,
    companyId,
    userId: reqUser._id,
    type: InvoiceType.invoice,
    invoiceOrigin: InvoiceOrigin.customerRequest,
  };
  const invoice = await this.updateOrCreateInvoice(invoiceData);

  // 5. Generate or retrieve an active payment token for the invoice
  const paymentToken = await this.generatePaymentToken(invoice._id, companyId);

  // 6. Attach taskDetails to payment token
  await this.paymentTokenRepository.updateById(paymentToken._id, { taskDetails });

  return { paymentToken: paymentToken.token };
}
```

### External integrations
- **Xero**: `updateOrCreateInvoice` calls `this.xeroService.init({ clientType: ClientType.main })` and syncs the invoice to Xero (contact upsert + invoice creation)
- **PaymentToken service**: creates or retrieves an active token tied to the invoice; token is returned to the operator for sharing with the customer

### MongoDB collections
- `invoices` — new invoice document created with `invoiceOrigin: customerRequest`
- `services` — read-only lookup for pricing and tax type
- `paymenttokens` — token created/updated with `taskDetails`
