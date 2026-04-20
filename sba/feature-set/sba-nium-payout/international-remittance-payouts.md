# International remittance payouts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | International remittance payouts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer / system |
| **Business Outcome** | Sends cross-border payouts through NIUM's payout product behind the orchestrator. |
| **Entry Point / Surface** | REST API on `sba-nium-payout` (NestJS); Swagger at `/docs` |
| **Short Description** | Validates and transforms payout requests; calls NIUM payout APIs; persists state in PostgreSQL via TypeORM. |
| **Variants / Markets** | Currency and corridor rules per NIUM |
| **Dependencies / Related Flows** | sba-bank-api routes via NiumPayoutVendor |
| **Service / Repository** | sba-nium-payout |
| **DB - Collections** | PostgreSQL (TypeORM entities) |
| **Evidence Source** | README; sba-bank-api architecture diagram |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | List primary payout endpoints for inventory cross-links |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `sba-bank-api/README.md` — sba-nium-payout in architecture diagram.
- `sba-nium-payout/README.md` — NIUM integration overview.
