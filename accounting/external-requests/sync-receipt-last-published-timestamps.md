# Keep receipt last-published dates aligned with Xero and SleekBooks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Keep receipt last-published dates aligned with Xero and SleekBooks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System |
| **Business Outcome** | Accounting and reporting can rely on `last_published_on` as the timestamp of the last successful publish to Xero or SleekBooks, consistent with stored publish history. |
| **Entry Point / Surface** | Sleek Receipts service — External API base `/api/external` — `POST /receipts/update-last-published-in-background` (async Bull job), `GET /receipts/update-last-published-in-background/status/:jobId`, `POST /update-last-published-direct` (synchronous full scan). Not an end-user app screen; operator or platform integration. |
| **Short Description** | Scans non-archived, non-deleted document events that have `publish_entries`, finds the chronologically last entry with `status === 'done'` and `publish_to` in `sb` or `xero`, and sets `last_published_on` to that entry’s `published_on`. Processing can run in batches via a Bull queue (Redis) with configurable batch size and delay, or update documents one-by-one in a direct endpoint. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Depends on `publish_entries` being populated by publish flows (Xero, SleekBooks). Uses Bull queue `update-last-published` (Redis). Downstream: any reporting, UI, or jobs that read `DocumentDetailEvent.last_published_on`. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (Mongoose model `DocumentDetailEvent`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether `/api/external` routes are protected by auth, API gateway, or private network only is not defined in the reviewed files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/routes/external-requests.js`**: Router mounted at `/api/external` in `index.js`. Defines Bull queue `update-last-published` with `DocumentDetailEvent.find` cursor: active docs (`is_archived` / `is_deleted` not true) with non-empty `publish_entries`. For each document, `lastSuccessfulPublishDoneEntry` = last array element (reverse scan) where `status === 'done'` and `publish_to` is `sb` or `xero`; `bulkWrite` / `updateOne` sets `last_published_on` to `published_on` of that entry. Background job: `POST /receipts/update-last-published-in-background` (202 + job id, batch 100, 100ms delay). Status: `GET /receipts/update-last-published-in-background/status/:jobId`. Direct: `POST /update-last-published-direct` returns counts and id lists for succeeded/failed. Queue retries: 5 attempts, 60s backoff.
- **`src/schemas/document-detail-event.js`**: Schema fields `last_published_on` (Date, default null) and `publish_entries` (array). Model name `DocumentDetailEvent`.
- **`src/tests/controllers/external-requests.test.js`**: Fixture documents with `publish_entries` including `publish_to: "xero"`, `status: "done"` for behaviour coverage.
