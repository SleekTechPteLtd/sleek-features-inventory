# Vendor factory and proxy routing

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Vendor factory and proxy routing |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (sba-bank-api) |
| **Business Outcome** | Routes each banking operation to the correct vendor microservice (DBS, NIUM cards, NIUM payout) using a consistent Factory + Proxy pattern so product code stays vendor-agnostic. |
| **Entry Point / Surface** | Internal HTTP API of `sba-bank-api`; not called directly by browser clients for vendor calls. |
| **Short Description** | `VendorFactory.getVendor(vendor)` selects DBS, NIUM card, or NIUM payout implementations; HTTP proxies forward to `sba-bank-dbs-api`, `sba-nium-api`, and `sba-nium-payout` with shared middleware (auth, tracing, validation). |
| **Variants / Markets** | SG / vendor-specific behaviour in downstream services |
| **Dependencies / Related Flows** | All SBA vendor microservices; environment URLs for each proxy |
| **Service / Repository** | sba-bank-api |
| **DB - Collections** | Per sba-bank-api data model (MongoDB) |
| **Evidence Source** | README architecture diagram |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `README.md` — vendor routing matrix and Factory + Proxy diagram.
