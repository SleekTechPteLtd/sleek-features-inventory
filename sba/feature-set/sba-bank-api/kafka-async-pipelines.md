# Kafka async pipelines

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Kafka async pipelines |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Decouples long-running or high-volume banking operations (card transactions, cross-currency transfers, NIUM payouts) from synchronous HTTP request handling. |
| **Entry Point / Surface** | Kafka topics produced/consumed inside `sba-bank-api` |
| **Short Description** | Controllers publish events to Kafka; consumers execute service logic and vendor proxy calls asynchronously. |
| **Variants / Markets** | Topic naming and consumer groups per environment |
| **Dependencies / Related Flows** | Kafka cluster; vendor services for completion |
| **Service / Repository** | sba-bank-api |
| **DB - Collections** | |
| **Evidence Source** | README async flow |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `README.md` — async sequence: Controller → Kafka Producer → Topic → Consumer → Service → Proxy.
