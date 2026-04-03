# Manage company share classes

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage company share classes |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Company owner (Sleek Admin bypasses checks via `canManageCompanyMiddleware`) |
| **Business Outcome** | Owners define the share instruments (class type, label, currency, and optionally how they are paid for) so shareholder holdings and allocations reference consistent share classes. |
| **Entry Point / Surface** | Authenticated HTTP API under `share-controller` routes: `POST/PUT/DELETE /companies/:companyId/share-items[...]`. Exact Sleek app navigation label is not defined in this repo. |
| **Short Description** | Create, update, or remove embedded `share_items` on a company document. Payloads include type, name, currency, and optionally `payment_method` when the `corpsec_squad` app feature enables it. Updates may set `has_completed_shares_allocation` on the acting user’s `CompanyUser` record. Duplicate combinations of type, name, and currency are rejected. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream**: `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("owner")`, app feature `corpsec_squad` (payment method and related share props). **Downstream**: Share allocation endpoints in the same controller validate holdings against `company.share_items` ids; `shareAllocationService.setTotalPercentageOfSharesPerShareholder` and incorporation workflows are separate allocation flows that consume those classes. **Schema**: `schemas/company.js` (`shareItemSchema`). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (Mongoose `Company` model): embedded array `share_items`. `companyusers` (or equivalent `CompanyUser` collection): `has_completed_shares_allocation` when cleared via share-item PUT body. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/share-controller.js`

- **`POST /companies/:companyId/share-items`** — `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("owner")`. Body fields via `pick`: `type`, `name`, `currency`, and `payment_method` if `appFeatureUtil.getAppFeaturesByName("corpsec_squad", "general")` exposes `props.shares.value.payment_method`. Calls `shareAllocationService.validateNegativeValues` on the payload, then `Company.findById` and `companyService.addShareItemToCompany(company, shareItemData)`.
- **`DELETE /companies/:companyId/share-items/:shareItemId`** — same auth/middleware. Locates subdocument `company.share_items.id(shareItemId)`, `deleteOne()`, `company.save()`.
- **`PUT /companies/:companyId/share-items/:shareItemId`** — Joi-style validation via `Validator` for `type`, `name`, `currency`, `has_completed_shares_allocation`, optional `payment_method` when corpsec payment method is enabled. `shareAllocationService.validateNegativeValues`; `companyService.isShareItemDuplicate` excluding current id; `subDoc.set(shareItemData)`; `company.save()`. If `has_completed_shares_allocation` is true in body, loads `CompanyUser` for `(company, user)` and sets `has_completed_shares_allocation` on that document.

### `services/company-service.js`

- **`addShareItemToCompany(company, shareItemData)`** — rejects if `isShareItemDuplicate(company.share_items, shareItemData)`; `company.share_items.push(shareItemData)`; `company.save()`; returns the new subdocument.
- **`isShareItemDuplicate(shareItems, newShareItem)`** — duplicate when same `type`, `name`, and `currency` as an existing item.
- **`canManageCompanyMiddleware`** — documents owner-only validation for non-admin users; partner origin and Sleek Admin shortcuts documented in the same file (used by share routes).

### `services/share-allocation-service.js`

- **`validateNegativeValues(sharesData)`** — used for share-item payloads (and allocation payloads elsewhere): flags negative values on `nb_of_shares`, `paid_up_amount`, `value_per_share` when present.
- **`setTotalPercentageOfSharesPerShareholder`**, **`correctValuePerShare`** — not used on the share-item CRUD routes; they support shareholder allocation flows that reference `share_item` ids.

### `schemas/company.js`

- **`shareItemSchema`**: `type` (enum `sharedData.shares.types`), `name`, `currency`, `payment_method` (enum `sharedData.shares.paymentMethods`).
- **`share_items`**: array of `shareItemSchema` on the main company schema.
