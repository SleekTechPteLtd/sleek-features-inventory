# Invoicing onboarding and user preferences

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Invoicing onboarding and user preferences |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User |
| **Business Outcome** | Each user can confirm they have seen the invoicing feature introduction and the product can persist and read that state plus any per-user invoicing preferences held for them. |
| **Entry Point / Surface** | Sleek App — invoicing area (feature introduction / user preferences); backed by `POST /invoice/acknowledge-invoicing-feature` and `GET /invoice/invoice-user` |
| **Short Description** | Authenticated users record acknowledgement of the invoicing feature (upsert by user id). They can retrieve their invoice user record, including whether invoicing was acknowledged. Preferences are stored on the `InvoiceUsers` document (currently `is_acknowledged`; schema supports timestamps). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Depends on auth (`AuthGuard` / `UserDetails`); data lives in MongoDB via `SLEEK_RECEIPTS` connection. Related to broader invoicing flows in the same module (invoice settings, PDF generation, etc.) but this capability is limited to acknowledgement and user-level invoice prefs. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `invoiceusers` (Mongoose model `InvoiceUsers`, connection `SLEEK_RECEIPTS`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact client navigation labels and any future per-user preference fields beyond `is_acknowledged` are not defined in these two files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`acct-coding-engine/src/invoice/invoice.controller.ts`**
  - `POST acknowledge-invoicing-feature` — `@UseGuards(AuthGuard)`, `@ApiOperation` summary: "Create invoicing feature acknowledgement", calls `invoiceService.acknowledgeInvoicingFeature(userDetails)` with `UserDetails` from the request.
  - `GET invoice-user` — `@UseGuards(AuthGuard)`, `@ApiOperation` summary: "Get invoice user preferences", returns `InvoiceUsers | null` via `invoiceService.getInvoiceUserInfo(userDetails)`.

- **`acct-coding-engine/src/invoice/services/invoice-users.service.ts`**
  - `acknowledgeInvoicingFeature`: `findOneAndUpdate` on `invoiceUsersModel` with filter `{ user_id }`, update `{ is_acknowledged: true }`, options `{ upsert: true, new: true }`; returns `BaseResponse` success/failure (errors are caught and returned as `success: false`, not rethrown).
  - `getInvoiceUserInfo`: `findOne({ user_id })` `.lean()`, returns document or `null`; errors are logged and rethrown.

- **`acct-coding-engine/src/invoice/models/invoice-users.schema.ts`**
  - Fields: `user_id` (ObjectId, required), `is_acknowledged` (boolean, default false); `timestamps: true`; index on `user_id`.

- **Delegation:** `InvoiceService.acknowledgeInvoicingFeature` / `getInvoiceUserInfo` delegate to `InvoiceUsersService` (see `invoice.service.ts`).
