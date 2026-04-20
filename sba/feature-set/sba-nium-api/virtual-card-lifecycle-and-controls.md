# Virtual card lifecycle and controls

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Virtual card lifecycle and controls |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (via SBA UI) / admin |
| **Business Outcome** | Issues and manages NIUM virtual cards: limits, MCC blocks, channels, lock/unlock, block/replace. |
| **Entry Point / Surface** | `/api/v1/{customerId}/card/*` REST on `sba-nium-api` |
| **Short Description** | Card APIs mirror NIUM capabilities: create/list cards, unmask, channel and MCC restrictions, transaction limits, card actions. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | NIUM card platform APIs |
| **Service / Repository** | sba-nium-api |
| **DB - Collections** | MongoDB |
| **Evidence Source** | README Card APIs |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `README.md` — Card APIs section.
