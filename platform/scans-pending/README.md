# Scans pending

Notes for scanning **sleek-back**, **customer-mfe**, and **sleek-website** (admin). New capability `.md` files still live under the parent **category** folders ([authentication](../authentication/), [authorization](../authorization/), etc.) — not here — unless you want raw scan logs only in this tree.

**Three-repo surface map:** [../cross-repo-sleek-surfaces-map.md](../cross-repo-sleek-surfaces-map.md).

**Before filing rows:** use the checklist and `app-router` domain hints in [../inventory-scope-and-domains.md](../inventory-scope-and-domains.md) so bookkeeping, corpsec, and other outcomes are not mis-tagged as **Platform**.

## Authentication overlap

**Do not** add duplicate **Authentication** master-sheet rows for legacy `sleek-back` / `customer-mfe` / `sleek-website` login, OTP, password reset, or registration. **Sleek Auth** owns those features in this inventory ([authentication/README.md](../authentication/README.md#scope-no-duplicate-auth-rows)). Use these repos for **other domains** (or migration notes elsewhere).

| Repo | Notes |
|------|--------|
| [sleek-back](./sleek-back/README.md) | Legacy Express API — scan non-auth capabilities |
| [customer-mfe](./customer-mfe/README.md) | Vue customer MFEs — same rule for auth surfaces |
| [sleek-website](./sleek-website/README.md) | Admin site — legacy `/users/*` + Auth0/SSO; map IA to domains |
| [sleek-sign-backend](./sleek-sign-backend/README.md) | Sleek Sign API — rows under [../sleeksign/](../sleeksign/) (**Domain** `Sleeksign`) |

## First-pass rows from sleek-back (non-auth)

These live under category folders, not under `scans-pending/`:

| Category | Document |
|----------|----------|
| Operations | [../operations/sleek-back-monolith-health-and-rate-guard.md](../operations/sleek-back-monolith-health-and-rate-guard.md) |
| External integrations | [../external-integrations/sleek-back-partner-origin-white-label.md](../external-integrations/sleek-back-partner-origin-white-label.md) |
| External integrations | [../external-integrations/sleek-cms-sdk-and-platform-config.md](../external-integrations/sleek-cms-sdk-and-platform-config.md) |

Further monolith capabilities (receipts, workflows, billing, …) still need domain confirmation before adding rows (often **Bookkeeping & Accounting** or other audit-hub domains, not **Platform**).
