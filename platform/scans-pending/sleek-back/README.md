# sleek-back — scan notes (placeholder)

Legacy **Node/Express** monolith (`sleek-back`).

Use [../../inventory-scope-and-domains.md](../../inventory-scope-and-domains.md) for **Platform vs other domains** and a first-pass map of `app-router.js` mounts. For **customer-mfe** + **sleek-website** together with this API, see [../../cross-repo-sleek-surfaces-map.md](../../cross-repo-sleek-surfaces-map.md).

## Authentication

**Out of scope for new Platform auth rows** — canonical authentication inventory is **Sleek Auth** under [../../authentication/](../../authentication/). Legacy routes (`/users/login-keep`, `/v2/two-factor-auth/*`, etc.) are migration context only; do not file duplicate “login” / “OTP” features here.

## In scope for this repo scan

Pick **non-auth** (or non-overlapping) outcomes and add `.md` files under the matching **category** at `platform/` root (e.g. another squad’s domain may eventually get its own top-level category; until then, keep **Platform** docs free of duplicate auth).

Examples of areas that are **not** Sleek Auth (may belong to other domains / squads — confirm before filing under Platform):

- Receipts / document events: `/receipt-system/document-events/*` (`controllers/receipt-user-controller.js`)
- Workflows, subscriptions, etc. — map to the right domain enum from the audit hub, not necessarily `Platform`.

## Workflow

1. Confirm the capability is **not** already covered as Sleek Auth authentication.
2. Choose category + domain per the master sheet.
3. Cite `sleek-back` `controllers/`, `services/`, and **customer-mfe** proxies when the UI calls this API.

## Logged from this repo (non-auth)

- [../../operations/sleek-back-monolith-health-and-rate-guard.md](../../operations/sleek-back-monolith-health-and-rate-guard.md)
- [../../external-integrations/sleek-back-partner-origin-white-label.md](../../external-integrations/sleek-back-partner-origin-white-label.md)

## Related

- [customer-mfe README](../customer-mfe/README.md)
- [Platform root README](../../README.md)
