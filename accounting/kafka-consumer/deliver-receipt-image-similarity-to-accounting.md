# Deliver receipt image similarity results to accounting

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Deliver receipt image similarity results to accounting |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Image-similarity ML output reaches the receipts domain so bookkeepers and matching flows can align current receipts with historical Dext-style documents without manual bridge work. |
| **Entry Point / Surface** | Event-driven: when `CONSUMER_ENABLED` is `true`, the process runs `consumeImageMessage()` alongside the extraction-feedback consumer; it subscribes to `SIMILARITY_RESULTS_TOPIC` (Confluent Kafka via `node-rdkafka`). Not an end-user screen. |
| **Short Description** | A Node consumer reads JSON payloads from the configured similarity-results topic and POSTs each parsed body to `{SLEEK_RECEIPTS_BASE_URL}/webhook/ml-image-similarity` with an `Authorization` header set from `SLEEK_RECEIPTS_TOKEN`, delegating persistence and document updates to the receipts service. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream**: Kafka topic that carries ML image-similarity results (same pipeline family as ML server producers). **Kafka**: `KAFKA_*` SASL/SSL settings, `GROUP_ID`, `KAFKA_CLIENT_ID`, `SIMILARITY_RESULTS_TOPIC`. **Downstream**: `sleek-receipts` `POST /webhook/ml-image-similarity` (shared-token auth); see `accounting/webhook/integrate-ml-extraction-and-similarity-callbacks.md` for how the service applies similarity maps to documents. Same repo also runs `consumeMessage()` for extraction feedback to `CODING_ENGINE_BASE_URL` — separate capability. |
| **Service / Repository** | sleek-ml-node-server (consumer); sleek-receipts (webhook receiver) |
| **DB - Collections** | None in this consumer (HTTP forward only). Sleek receipts persists and updates collections documented on the webhook feature (`mlfeedbackschemas`, `documentdetailevents`, `dextevents` for the image-similarity path). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium — behavior is clear from code; production reliance depends on `CONSUMER_ENABLED` and correct Kafka/receipts configuration. |
| **Disposition** | Unknown |
| **Open Questions** | Whether malformed JSON on the similarity topic is acceptable risk (no try/catch around `JSON.parse` in `consumeImageMessage`); exact message schema contract between ML producers and the webhook. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/consumer.js`**: `createConsumer` builds `Kafka.KafkaConsumer` with `client.id`, `bootstrap.servers`, SASL user/password, `security.protocol`, `sasl.mechanisms`, `group.id` from env.
- **`src/consumer.js`**: `consumeImageMessage(topic = similarity_results_topic)` — `on('data')` handler POSTs `JSON.parse(value.toString())` to `` `${sleek_receipts_base_url}/webhook/ml-image-similarity` `` with `headers: { Authorization: sleek_receipts_token }` via `axios`; subscribes to `[topic]`, calls `consume()`; `SIGINT` disconnects.
- **`src/consumer.js`**: Entry: `CONSUMER_ENABLED` parsed as JSON (default `false`); when true, both `consumeMessage()` and `consumeImageMessage()` are started (parallel Kafka consumers in one process).
- **Env (from destructuring)**: `SIMILARITY_RESULTS_TOPIC`, `SLEEK_RECEIPTS_BASE_URL`, `SLEEK_RECEIPTS_TOKEN`, plus shared Kafka vars (`KAFKA_USERNAME`, `KAFKA_PASSWORD`, `KAFKA_PROTOCOL`, `KAFKA_MECHANISMS`, `KAFKA_BOOTSTRAP_SERVER`, `KAFKA_CLIENT_ID`, `GROUP_ID`).
