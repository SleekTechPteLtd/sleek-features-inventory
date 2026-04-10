# Manage Xero Contacts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Xero Contacts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | SuperAdmin; System (Invoice service, auto-triggered during invoice creation) |
| **Business Outcome** | Ensures every billing client has a corresponding contact record in Xero so that invoices issued through the billing system are correctly attributed to accounting entries in Xero. |
| **Entry Point / Surface** | Internal API — `POST /xero/contact` (SuperAdmin-gated); also called automatically by the Invoice service when generating or fetching a customer's Xero contact before invoice creation. |
| **Short Description** | SuperAdmins create a new Xero contact for a client by supplying name, email, and optional address details. The billing system also upserts contacts automatically when issuing invoices, covering the full contact lifecycle (create and update). Address fields are populated only in SG; other markets receive name/email only. |
| **Variants / Markets** | SG, HK, UK, AU — contact address (street, city, region, postal code, country) is written to Xero only in SG (`xero_contact_address: true`); disabled for HK, UK, AU. |
| **Dependencies / Related Flows** | Invoice creation flow (`invoice.service.ts → xeroService.updateOrCreateContact`); Xero OAuth token management (`XeroSettingRepository`); Xero Accounting API (external, `accounting.contacts` scope); multi-tenant Xero support (ClientType: `main`, `manageService`). |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `xero_settings` (MongoDB via SleekXeroDB — persists encrypted OAuth tokens and optional per-tenant clientId/clientSecret; Xero contacts themselves are stored in Xero, not MongoDB) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Is `POST /xero/contact` exposed through an admin UI or used only via internal tooling/scripts? What triggers a SuperAdmin to manually create a contact as opposed to relying on the auto-creation path in invoice.service.ts? Is there a reconciliation flow that checks for contact mismatches between the billing system and Xero? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `src/xero/xero.controller.ts`

| Method | Route | Guard | Purpose |
|---|---|---|---|
| `POST` | `/xero/contact` | `@GroupAuth(Group.SuperAdmin)` | Creates a Xero contact for the given client type |

- `client-type` header selects the Xero tenant (`main` or `manage_service`).
- Delegates to `XeroService.createContact(contactData: ContactDto)`.

### Service — `src/xero/services/xero.service.ts`

**`createContact(contactData: ContactDto)`** (line ~320)
- Builds a `Contact` object (name, email, firstName, lastName).
- Calls `xeroClient.accountingApi.updateOrCreateContacts(tenantId, contacts)`.
- Returns the first contact from the Xero response.

**`updateOrCreateContact(contactData: ContactDto, contactId?: string)`** (line ~347)
- Upsert variant; accepts an optional existing `contactID` to update in place.
- Adds an `Address` (type `POBOX`) when `address` is supplied **and** `COUNTRY_SPECIFIC_CONFIG[PLATFORM].xero_contact_address === true` (SG only).
- Called internally by `invoice.service.ts` during customer-contact resolution.

**`getContact(contactId: string)`** (line ~304)
- Fetches a single Xero contact by ID via `accountingApi.getContact`.
- Used to verify whether an existing contact is still active (archived-contact fallback in invoice service).

**Multi-tenant init** (`init({ clientType, tokenId })`)
- Loads encrypted OAuth tokens from `xero_settings` MongoDB collection (via `XeroSettingRepository`).
- Supports an active/backup token-set mechanism (`XERO-TOKEN-SET-{clientType}` / `XERO-TOKEN-SET-{clientType}-BACKUP`).
- Xero scopes used: `accounting.settings`, `accounting.transactions`, `accounting.contacts`.

### DTO — `src/xero/dtos/contact.dto.ts`

Fields: `name` (required), `email`, `firstName`, `lastName`, `address` (optional object with `addressLine1`, `addressLine2`, `city`, `region`, `postalCode`, `country`).

### Schema — `src/xero/models/xero-setting.schema.ts`

`XeroSetting` document: `_id` (token key), `value` (token JSON, encrypted), `clientId`, `clientSecret`, `isActive`. Stored in `SleekXeroDB`.

### Country config — `src/shared/consts/common.ts`

`COUNTRY_SPECIFIC_CONFIG.sg.xero_contact_address = true`; all other markets (`hk`, `uk`, `au`) set to `false`.

### Cross-repo caller — `src/invoice/services/invoice.service.ts`

Calls `xeroService.updateOrCreateContact(...)` when resolving a customer's Xero contact before creating an invoice. Falls back to a second `updateOrCreateContact` call if the contact appears to be archived.
