# Feed bookkeeping extraction feedback to coding engine

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Feed bookkeeping extraction feedback to coding engine |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | When bookkeeping ML runs finish, their results are forwarded to the coding engine’s extraction feedback API so models can learn from completed production runs and improve over time. |
| **Entry Point / Surface** | Not a user-facing surface. When `CONSUMER_ENABLED` is true, the Node process starts Kafka consumers at runtime; bookkeeping completion events arrive on the configured bookkeeping results topic (Confluent Cloud, `node-rdkafka`). |
| **Short Description** | The consumer reads JSON payloads from `BOOKKEEPING_RESULTS_TOPIC`, normalises the body depending on `OAI_EXTRACTION_ENABLED` (OpenAI extraction path uses nested `data` only; legacy path sends `id`, `type`, and `data`), and POSTs to `${CODING_ENGINE_BASE_URL}/feedback/openai-extraction` or `/feedback/extraction`. Empty or invalid JSON is skipped; API errors are logged without blocking the consumer loop. The same file also runs a separate consumer for image-similarity results that posts to Sleek Receipts—see Evidence. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Kafka:** Confluent Cloud (`KAFKA_*` env: bootstrap, SASL, client id, `GROUP_ID`), `BOOKKEEPING_RESULTS_TOPIC` (bookkeeping path), `SIMILARITY_RESULTS_TOPIC` (separate `consumeImageMessage` path to `${SLEEK_RECEIPTS_BASE_URL}/webhook/ml-image-similarity` with bearer token). **Downstream:** coding-engine HTTP API (`CODING_ENGINE_BASE_URL`, feedback routes). **Runtime:** `CONSUMER_ENABLED` must be true for either consumer to start; `dotenv` loads configuration. |
| **Service / Repository** | sleek-ml-node-server |
| **DB - Collections** | None (no persistence in this consumer; stateless HTTP forward). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | No visible retry or dead-letter path when the coding-engine POST fails; whether both bookkeeping and similarity consumers are always desired when `CONSUMER_ENABLED` is true; production values for `OAI_EXTRACTION_ENABLED` and schema contract with upstream ML publishers. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/consumer.js`**: `createConsumer` builds `Kafka.KafkaConsumer` with `client.id`, `bootstrap.servers`, SASL user/password, `security.protocol`, `sasl.mechanisms`, `group.id`; `consumeMessage` subscribes to `BOOKKEEPING_RESULTS_TOPIC` (default param), parses message value as JSON, skips null/empty strings, builds `body` from `{ id, type, data }` or `{ data }` when `OAI_EXTRACTION_ENABLED` is true, then `axios.post` to `` `${CODING_ENGINE_BASE_URL}/feedback/${isOAIExtractionEnabled ? 'openai-extraction' : 'extraction'}` `` with logging on success and structured error logging on failure.
- **`src/consumer.js`**: Entry point: `isConsumerEnabled = JSON.parse(CONSUMER_ENABLED || "false")`; when true, runs `consumeMessage()` and `consumeImageMessage()` in parallel (both register `SIGINT` to `consumer.disconnect()`).
- **`src/consumer.js`**: `consumeImageMessage` consumes `SIMILARITY_RESULTS_TOPIC` and POSTs parsed JSON to `${sleek_receipts_base_url}/webhook/ml-image-similarity` with `Authorization: sleek_receipts_token`—distinct from the coding-engine feedback path but shipped in the same process.
