# Forward ERPNext invoices to Sleek Receipts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Forward ERPNext invoices to Sleek Receipts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | When ERPNext submits an invoice, Sleek Receipts receives a consistent, normalized payload so purchase and receipt document workflows stay aligned with the ledger without manual re-entry. |
| **Entry Point / Surface** | Server-to-server: `POST /webhook/invoice/submit` on `sleek-erpnext-service` (`WebhookController.receiveERPNextInvoiceData`). Secured by `ERPNextAuthGuard` (`x-frappe-webhook-signature` must match `FRAPPE_WEBHOOK_SECRET`). Swagger tags `Webhook`; not an end-user screen. |
| **Short Description** | Reads `docs` from the ERPNext webhook body, converts Python-style string content to JSON (`formatWebhookInvoiceData`), maps a subset of invoice fields (doctype, extraction_id, supplier, items, dates, totals, bill references), and POSTs to `{SLEEK_RECEIPTS_BASE_URL}/webhook/invoice/submit` with `Authorization: SLEEK_RECEIPTS_TOKEN`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** ERPNext/Frappe document submit webhook to this service. **Downstream:** Sleek Receipts `POST /webhook/invoice/submit` — see inventory `accounting/webhook/sync-erpnext-invoice-data-to-documents.md` (sleek-receipts consumer, `updateDocumentEventByExtractionId`). **Config:** `SLEEK_RECEIPTS_BASE_URL`, `SLEEK_RECEIPTS_TOKEN`, `FRAPPE_WEBHOOK_SECRET`. Same `WebhookController` also exposes `POST /webhook/document/reconcile-from-sb` (bank reconciliation); that path is separate from invoice forwarding. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None: `WebhookService` uses `HttpService` only; no Mongoose models in this flow. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Inline comment notes additional DSS field mapping may be adjusted when live data is available; HTTP 500 message typo `Interval Server Error`; confirm whether Swagger `ApiSecurity('basic')` is accurate vs signature-only guard. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/webhook/webhook.controller.ts`

- **`POST /webhook/invoice/submit`** → `receiveERPNextInvoiceData`: extracts `docs` from `body` via `lodash.get(body, 'docs', '')`, delegates to `webhookService.receiveERPNextInvoiceData(docs)`, responds `200` with JSON result.
- **Guards / pipes:** `@UseGuards(new ERPNextAuthGuard())`, `ValidationPipe({ transform: true })`.
- **OpenAPI:** `@ApiTags('Webhook')`, `@ApiOperation({ summary: 'Webhook Api operation' })`, `@ApiHeader` for `x-frappe-webhook-signature` (required), `@ApiSecurity('basic')`.

### `src/webhook/webhook.service.ts`

- **`formatWebhookInvoiceData(docs: string)`:** Replaces Python-style literals (`'`, `None`, newlines) so `JSON.parse` yields an invoice object.
- **`receiveERPNextInvoiceData(docs: string)`:** Logs payload; builds `data` from `invoice` with `get(invoice, …)` for `doctype`, `extraction_id`, `supplier`, `items`, `due_date`, `currency`, `total`, `base_total`, `bill_no`, `bill_date` (fallback `posting_date`); POST `${SLEEK_RECEIPTS_BASE_URL}/webhook/invoice/submit` with headers `{ Authorization: SLEEK_RECEIPTS_TOKEN }`; on HTTP 200 returns `response.data`, else throws `HttpException` (non-200 path uses generic internal error message).

### `src/guard/erpnext-auth.guard.ts`

- **`ERPNextAuthGuard`:** Requires header `x-frappe-webhook-signature`; compares to `process.env.FRAPPE_WEBHOOK_SECRET`; `Forbidden` if missing, `InternalServerError` if secret unset, `Unauthorized` if mismatch.
