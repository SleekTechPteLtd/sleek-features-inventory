# Inventory scope: Platform vs other master-sheet domains

Use this when scanning **sleek-back**, **customer-mfe**, or any large repo so capabilities land under the right **Domain** column and the right **documentation tree** (this repo only has `platform/` today; other domains can add sibling folders at the **repository root** when squads maintain markdown inventories).

Aligned with [Sleek Feature Scope Audit Hub](../Sleek%20Feature%20Scope%20Audit%20Hub.md) (spreadsheet **Domain** enum).

## Master-sheet domains (enum)

`Corpsec`, `Compliance`, `SBC`, `Bookkeeping & Accounting`, `Sleeksign`, `CLM`, `Platform`, `SDET`, `RPA`, `AI/ML`, `Marketing` (plus any your sheet adds later).

## Checklist: does the capability belong in `platform/` docs?

Answer for the **user story**, not the repo name.

1. **Is it the same outcome as Sleek Auth login, registration, password/OTP, or session issuance?**
  If yes → document under [authentication/](./authentication/) only for **Sleek Auth**; do **not** add a parallel row for legacy `sleek-back` / `customer-mfe` paths ([authentication/README.md#scope-no-duplicate-auth-rows](./authentication/README.md#scope-no-duplicate-auth-rows)).
2. **Is it “who can do what” (policies, roles, permission catalog, PDP-style checks)?**
  If yes → **Domain** is often still **Platform** for the shared authz product, filed under [authorization/](./authorization/). Legacy-only RBAC in the monolith may need a **separate** row with evidence in `sleek-back`—avoid duplicating the same AuthZ SDK story twice.
3. **Is it health, metrics, rate limits, or observability of shared APIs?**
  If yes → likely **Platform**, [operations/](./operations/).
4. **Is it a bridge to a third party, webhooks, or explicit partner/channel wiring (white-label, Auth0, etc.)?**
  If yes → often **Platform**, [external-integrations/](./external-integrations/) (or the domain that owns the business outcome if the integration is domain-specific, e.g. Xero for accounting).
5. **Is the outcome company formation, filings, registers, corporate actions?**
  If yes → usually **Corpsec**, not Platform—**do not** file under `platform/` unless the capability is purely shared identity/platform glue.
6. **Is the outcome receipts, expenses, accounting files, bank/tax workflows?**
  If yes → usually **Bookkeeping & Accounting**—add a future `bookkeeping/` (or similar) at the repo root when that inventory exists; keep **Platform** free of bookkeeping product rows.
7. **Is the outcome e-sign / document lifecycle for Sleeksign?**
  If yes → **Sleeksign**.
8. **Is the outcome KYC / AML / risk questionnaires / Onfido?**
  If yes → **Compliance** (unless your sheet splits finer).
9. **Unsure?**
  Default the **Domain** column to **Unknown** in the sheet, list evidence paths, and resolve with a product owner—avoid guessing **Platform** just because code lives in `sleek-back`.

## Where to put markdown today


| Domain column (target) | Where to add `.md` today                                                                                                                     |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Platform**           | `platform/<category>/` (authentication, authorization, external-integrations, operations)                                                    |
| Any other domain       | Master sheet row + evidence; optional new top-level folder next to `platform/` when that squad owns markdown (e.g. `corpsec/`) |


## sleek-back — `app-router.js` mount points (first-pass domain hints)

Rough routing for **planning only**; product owners should confirm.


| Mount prefix                                                                                                                                                 | First-pass domain hint                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/v2/draft-company`, `/v2/company`, `/v2/company-users`, `/v2/enquiry`                                                                                       | **SBC** (confirm)                                                                                                                                                             |
| `/v2/users`                                                                                                                                                  | **Platform** only if not duplicate auth; often **SBC** user profile                                                                                                           |
| `/v2/acra-company`, `/v2/corpsec`, `/company-house`                                                                                                          | **Corpsec**                                                                                                                                                                   |
| `/v2/notification`, `/v2/notify`                                                                                                                             | **Platform** or **SBC** (confirm)                                                                                                                                             |
| `/v2/payment-tokens`, `/v2/invoice`, `/v2/payment-requests`, `/v2/credit-balances`, `/v2/renewal`, `/v2/billing-payment`, `/v2/auto-charge-payment-requests` | **Bookkeeping & Accounting** / billing (confirm)                                                                                                                              |
| `/v2/config`, `/v2/utilities`                                                                                                                                | **Platform** (confirm: product vs internal helper)                                                                                                                            |
| `/v2/sleek-auditor`, `/v2/sleek-auditor-v2`                                                                                                                  | **Compliance** or dedicated product domain (confirm)                                                                                                                          |
| `/v2/workflow`, `/v2/admin/workflow`, `/v2/sleek-workflow`                                                                                                   | Cross-cutting—**confirm** (not default Platform)                                                                                                                              |
| `/v2/sleek-sign`                                                                                                                                             | **Sleeksign**                                                                                                                                                                 |
| `/v2/admin`                                                                                                                                                  | Cross-cutting admin—split by outcome, not “all Platform”                                                                                                                      |
| `/v2/sleek-kyc`, `/v2/identity-verification/`*, `/v2/comply-advantage`, `/v2/risk-assesment-form`, `/v2/risk-assessment-form-approval`                       | **Compliance**                                                                                                                                                                |
| `/v2/partner`                                                                                                                                                | **Platform** (channel / partner APIs; see [external-integrations/sleek-back-partner-origin-white-label.md](./external-integrations/sleek-back-partner-origin-white-label.md)) |
| `/v2/two-factor-auth`, `/v2/auth`                                                                                                                            | Legacy auth—**no duplicate** Sleek Auth rows                                                                                                                                  |
| `/v2/encode`                                                                                                                                                 | Often implementation detail; **Platform** only if it is a named product capability                                                                                            |
| `/v2/sleek-site-onboarding`, `/v2/ltd-onboarding`, `/onboarding`                                                                                             | **SBC** / **Corpsec** mix (confirm)                                                                                                                                           |
| `/v2/sb-migration`                                                                                                                                           | **SBC** or migration program (confirm)                                                                                                                                        |
| `/v2/company-user-roles`, `/company-roles`                                                                                                                   | **Platform** authorization surface vs legacy—align with [authorization/](./authorization/)                                                                                    |
| `/internal`, `/v2/crm-service`, `/v2/auto-upgrade-accounting`, `/v2/send-transfer-xero-email`, `/v2/accounting-transfer-xero-email`                          | **Bookkeeping & Accounting** / integrations (confirm)                                                                                                                         |
| `glob("./controllers/**/*.js")` legacy roots                                                                                                                 | Map per controller (e.g. `receipt-user-controller` → **Bookkeeping & Accounting**; `company-controller` → **SBC** / **Corpsec**)                                              |


## customer-mfe

Treat proxies and modules as **UI entry points** to the same domains as the APIs they call. Follow the backend hint above; the **Domain** column should match the business outcome, not “Vue”.

## Related

- [README.md](./README.md)
- [scans-pending/README.md](./scans-pending/README.md)

