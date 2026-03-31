# Sleek Sign customer MFE (Vue shell)

## Master sheet (draft)


| Column                           | Value                                                                                                                                                                                                                                                                  |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Domain**                       | Sleeksign                                                                                                                                                                                                                                                              |
| **Feature Name**                 | Customer-facing Sleek Sign web experience (micro-frontend)                                                                                                                                                                                                             |
| **Canonical Owner**              | TBD                                                                                                                                                                                                                                                                    |
| **Primary User / Actor**         | End customers and invited signers                                                                                                                                                                                                                                      |
| **Business Outcome**             | Self-service document list, editor, signing, templates, and social/OTP-assisted access in the customer domain                                                                                                                                                          |
| **Entry Point / Surface**        | Hosted **customer-mfe** package `sleek-sign` (routes under `/sleek-sign/...` when composed with root shell); admin may deep-link with `?origin=admin` from **sleek-website**                                                                                           |
| **Short Description**            | Vue modules under `src/modules/sleeksign/`* with proxies under `src/proxies/back-end/sleeksign/*` calling **sleek-sign-backend** and/or **sleek-back** depending on operation. Uses platform config (`/v2/config/...`) for branding and feature flags like other MFEs. |
| **Variants / Markets**           | Partner white-label when customer host differs; env `VUE_APP_PLATFORM_API` / sign API bases                                                                                                                                                                            |
| **Dependencies / Related Flows** | [sleeksign-v2-rest-api.md](./sleeksign-v2-rest-api.md), [sleeksign-legacy-document-api.md](./sleeksign-legacy-document-api.md), [../cross-repo-sleek-surfaces-map.md](../cross-repo-sleek-surfaces-map.md)                                                             |
| **Service / Repository**         | `customer-mfe/sleek-sign`                                                                                                                                                                                                                                              |
| **DB - Collections**             | N/A (client)                                                                                                                                                                                                                                                           |
| **Evidence Source**              | Codebase                                                                                                                                                                                                                                                               |
| **Criticality**                  | High                                                                                                                                                                                                                                                                   |
| **Usage Confidence**             | High                                                                                                                                                                                                                                                                   |
| **Disposition**                  | Must Keep                                                                                                                                                                                                                                                              |
| **Open Questions**               | Split of calls between sign backend vs sleek-back per feature                                                                                                                                                                                                          |
| **Reviewer**                     |                                                                                                                                                                                                                                                                        |
| **Review Status**                | Draft                                                                                                                                                                                                                                                                  |


## Evidence

### customer-mfe

- `sleek-sign/src/proxies/back-end/sleeksign/` — document, sign, OTP, templates, contacts, uploads, reminders, etc.
- `sleek-sign/src/proxies/back-end/config/`*, `sleek-address/*` — platform config and address helpers.
- `sleek-sign/src/modules/sleeksign/*` — UI components and flows.

## Related

- [../scans-pending/customer-mfe/README.md](../scans-pending/customer-mfe/README.md)

