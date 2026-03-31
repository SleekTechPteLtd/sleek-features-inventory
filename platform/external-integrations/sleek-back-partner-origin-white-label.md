# Partner (white-label) origin context on API requests

## Master sheet (draft)


| Column                           | Value                                                                                                                                                                                                                                                              |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Domain**                       | Platform                                                                                                                                                                                                                                                           |
| **Feature Name**                 | Resolve partner tenant from browser Origin                                                                                                                                                                                                                         |
| **Canonical Owner**              | TBD                                                                                                                                                                                                                                                                |
| **Primary User / Actor**         | End customers on partner-branded domains; partner admins                                                                                                                                                                                                           |
| **Business Outcome**             | Same Sleek backend serves Sleek-owned and partner white-label frontends; downstream handlers can apply partner-specific branding, config, or entitlements                                                                                                          |
| **Entry Point / Surface**        | Every API request (after rate limiter, before `appRouter`)                                                                                                                                                                                                         |
| **Short Description**            | Middleware reads `Origin`, skips known Sleek domains and localhost, loads `Partner` by configured domain URLs, and attaches `req.partner` (and related user flags when used with login flows). Not a replacement for Sleek Auth; complements session/token checks. |
| **Variants / Markets**           | Partner records in MongoDB (`Partner` schema); domain URL fields                                                                                                                                                                                                   |
| **Dependencies / Related Flows** | `SLEEK_DOMAINS`; `/v2/partner` and partner handlers; customer portal on non-Sleek hostnames must send `Origin`                                                                                                                                                     |
| **Service / Repository**         | `sleek-back` `services/partners/partner-service.js`, `controllers-v2/partner.js`                                                                                                                                                                                   |
| **DB - Collections**             | `Partner`, `Company`, `User` (partner linkage)                                                                                                                                                                                                                     |
| **Evidence Source**              | Codebase                                                                                                                                                                                                                                                           |
| **Criticality**                  | High (for managed-service / white-label channels)                                                                                                                                                                                                                  |
| **Usage Confidence**             | Medium                                                                                                                                                                                                                                                             |
| **Disposition**                  | Must Keep until channel model moves to Sleek Auth + explicit tenant claims                                                                                                                                                                                         |
| **Open Questions**               | Long-term alignment with Sleek Auth org/tenant model; cookie vs Origin edge cases                                                                                                                                                                                  |
| **Reviewer**                     |                                                                                                                                                                                                                                                                    |
| **Review Status**                | Draft                                                                                                                                                                                                                                                              |


## Evidence

### sleek-back

- `services/partners/partner-service.js` — `partnerMiddleware`, `getPartnerByDomainUrl`, `assignUserPartnerUserDetailsViaOrigin`.
- `app.js` — `app.use(partnerService.partnerMiddleware)` before `appRouter`.
- `app-router.js` — `router.use("/v2/partner", require("./controllers-v2/partner"))`.

### customer-mfe

- Browser `Origin` is set by the host serving the Vue shell (e.g. partner domain vs `*.sleek.com`). Env such as `VUE_APP_PLATFORM_API` points API calls at `sleek-back` while preserving that `Origin` in CORS scenarios.

## Related

- [../scans-pending/customer-mfe/README.md](../scans-pending/customer-mfe/README.md)
- [../authentication/README.md](../authentication/README.md) (canonical identity; no duplicate legacy login rows)

