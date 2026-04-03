# Record reconciliation completion and failure

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Record reconciliation completion and failure |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | After bookkeeping finishes posting a reconciliation in SleekBooks, the platform persists whether it succeeded or failed so reconciliation and document status match the books and users see an accurate end state. |
| **Entry Point / Surface** | Event-driven: `ReconciliationDoneEvent` and `ReconciliationFailedEvent` consumed by `ReconciliationListener` (`@Controller('reconciliation-listener')`); optional `POST reconciliation-listener/process-message` exists for ML results testing, not for this done/failed path. |
| **Short Description** | Subscribes to bookkeeping completion events, applies Redis-backed idempotency per event, then updates the reconciliation document (aggregate status, reconcile entry status, payment entry id, ML bank-transaction status, optional cash-coded flag) and, on success, the accounting document (reconciled status, `reconciliation_id`, `reconciliation_method`). Publishes `DOCUMENT_RECONCILED` and writes Sleek Auditor logs on the success path; failure path records errors on reconcile entries and aggregate failure status with auditor error logs. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: SleekBooks / bookkeeping pipeline emitting `ReconciliationDoneEvent` / `ReconciliationFailedEvent` after reconcile entry processing. Uses `ReconciliationService`, `SleekbooksService` (cash-code check), `EventUtils.publishEvent` (`CodingEngineEventType.DOCUMENT_RECONCILED`), `SleekAuditorService.insertLogsToSleekAuditor`. Downstream consumers of `DOCUMENT_RECONCILED` and document/reconciliation reads in app and other services. Related: broader listener also handles `MLReconciliationResultEvent` (separate flow). |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | reconciliations, documentdetailevents |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Listener** — `src/kafka/listeners/reconciliation.listener.ts`: `@SubscribeEvent(ReconciliationDoneEvent.name)` → `onCEReconciliationDone` → `commonCacheService.setCacheIfNotExists` idempotency key `reconciliation:processed-event:{message.data?.id \|\| message.id}` (30s TTL) → `reconciliationService.updateReconciliationDoneEvent(message.data)`. `@SubscribeEvent(ReconciliationFailedEvent.name)` → `onCEReconciliationFailed` → same idempotency pattern → `reconciliationService.updateReconciliationFailedEvent(message.data)`.
- **Service — success** — `src/reconciliation/reconciliation.service.ts` `updateReconciliationDoneEvent`: loads reconciliation by `id`; `reconciliationModel.updateOne` sets `payment_entry_id`, `reconcile_entries.$.status` = `ReconcileStatus.DONE`, aggregate `status` = `ReconciliationStatus.RECONCILED`; optional second `updateOne` for `reconcile_entries.$.is_cash_coded` when SleekBooks shows journal-entry cash coding; updates `ml_reconciliation_results.bank_transactions.$.status` to `RECONCILED`; `determineReconciliationMethod` → `documentModel.updateOne` with `reconciliation_id`, document `status` reconciled, `reconciliation_method`; `eventUtils.publishEvent(CodingEngineEventType.DOCUMENT_RECONCILED, ...)`; `sleekAuditorService.insertLogsToSleekAuditor` success log (errors in catch also auditor-logged).
- **Service — failure** — `updateReconciliationFailedEvent`: `reconciliationModel.updateOne` sets `payment_entry_id`, `reconcile_entries.$.error` (formatted), `reconcile_entries.$.status` = `FAILED`, aggregate `status` = `ReconciliationStatus.FAILED`; updates ML bank transaction status to `FAILED`; `insertLogsToSleekAuditor` for failure messaging.
- **Schemas** — Reconciliation and document collections as used elsewhere in inventory: `src/reconciliation/models/reconciliation.schema.ts` → `reconciliations`; `src/document/models/document.schema.ts` → `documentdetailevents`.
