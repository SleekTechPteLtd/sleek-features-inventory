# Apply ML and OpenAI extraction outcomes to receipts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Apply ML and OpenAI extraction outcomes to receipts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | In-flight receipts get categories and (when enabled) full field-level extraction from ML/OpenAI so they can move from extraction toward review and bookkeeping without manual re-entry. |
| **Entry Point / Surface** | System: Kafka subscription on `MLCategoryResultEvent` (shared topic for ML category and OpenAI extraction completion payloads); optional HTTP `POST /ml-category-results-listener/process-message` for controlled testing of OpenAI extraction payloads |
| **Short Description** | The coding engine consumes completion events from the ML categorization / OpenAI extraction pipelines. It routes payloads to `FeedbackService`: either full OpenAI extraction (`ENABLE_OAI_EXTRACTION=true`) or legacy category-only results parsed from `MLCategoryResultEvent` data. Eligible documents in `EXTRACTING` or `PROCESSING` are merged with existing ML feedback, supplier/smart rules, COA matching, duplicate detection, GST/line-item handling, and optional auto-publish—updating MongoDB feedback and document records so workflows can continue. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: ML categorization pipeline, OpenAI extraction service, Kafka event bus. Downstream: `DocumentService` (status, publish, auto-assign), `CoaService` (chart of accounts), supplier rules HTTP APIs, `SleekAuditorService`, `ClaimReportService` (expense claims), `BankService` (auto-publish bank mapping), `DataStreamerService` (optional republish `MLCategoryEvent` when category missing). Related: `receiveExtractionData` webhook path for raw ML feedback vs this Kafka path for OpenAI/ML completion. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `mlfeedbackschemas` (Sleek receipts DB), `documentdetailevents` (Sleek receipts DB), `companies` (coding engine DB) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/kafka/listeners/ml-category-results.listener.ts`** — `MLCategoryResultsListener` (`@Controller('ml-category-results-listener')`): `@SubscribeEvent(MLCategoryResultEvent.name)` on `onOpenAICategoryExtractionDone`; branches on `ENABLE_OAI_EXTRACTION === 'true'` → `feedbackService.handleOAIExtractionDoneEvent(message?.data as OAIExtractionEventData)`; else parses `MLCategoryResultEvent` payload (`docId`, nested `results[0].response`: `category`, `autopub_oai`, `oai_feedback`) → `handleOpenAICategoryDone`. Test hook: `POST process-message` with `OAIExtractionResultEvent` body.
- **`src/kafka/events/ml-category-results.event.ts`** — `MLCategoryResultEvent` extends `DomainEvent` with `docId` and `message.results[].response` (category, autopub_oai, oai_feedback arrays).
- **`src/kafka/events/oai-extraction-results.event.ts`** — `OAIExtractionResultEvent` extends `DomainEvent` with nested `data` (docId, curr, supplier, amount, date, status, category).
- **`src/feedback/feedback.service.ts`** — `handleOAIExtractionDoneEvent`: loads document by `docId`, skips if status not `EXTRACTING`/`PROCESSING`, builds `extractedDataFromOAI` (currency, supplier/customer for sales invoice, amounts, dates, category), then `receiveExtractionDataHandleDocumentEventCaseProcessDocumentUpdate` for rules, COA, duplicates, default line items, `documentService.updateDocumentById`, audit logs, optional auto-publish. `handleOpenAICategoryDone`: same document gate, passes `extractedDataFromOAI` with `isExtracted: true` and OAI category metadata into the same processing path. Shared pipeline updates `Feedback` via `updateFeedbackById` / `updateFeedBackCategory` and touches `Document` and `Company` for validation and publish eligibility.
