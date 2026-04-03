# Compare document images

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Compare document images |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Lets accounting workflows hand off document image pairs or batches to ML by publishing comparison jobs to Kafka, so similarity or duplicate checks can run without blocking the caller. |
| **Entry Point / Surface** | System — HTTP API `POST /api/v1/sleek-ml/compare-images` (not a user-facing screen); callers are typically backend services in the accounting platform. |
| **Short Description** | The sleek-ml Node server accepts a JSON body on the compare-images route and publishes it to the Kafka topic named by `COMPARE_IMAGES_TOPIC`, using the shared Confluent producer. A separate root `POST /api/v1/sleek-ml/` route publishes bookkeeping query payloads to `BOOKKEEPING_QUERIES_TOPIC`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: services that POST comparison payloads. Apache Kafka via Confluent Cloud (`KAFKA_*` env vars in `src/producer.js`). Topic name from `COMPARE_IMAGES_TOPIC`. Downstream: Kafka consumers that perform ML image comparison (not in this repo). Related: same router also exposes bookkeeping query publishing to `BOOKKEEPING_QUERIES_TOPIC`. |
| **Service / Repository** | sleek-ml-node-server |
| **DB - Collections** | None in the listed files; this path is API → Kafka only. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | No Express auth/guard is applied in `producer.routes.js` — confirm whether ingress, API gateway, or network policy enforces access. Payload shape for compare-images is not validated or documented in code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`routes/index.routes.js`**: Mounts producer routes at `/api/v1/sleek-ml`.
- **`routes/producer.routes.js`**: `POST /compare-images` calls `producer.producerMessage(compare_images_topic, req.body)` where `compare_images_topic` is `process.env.COMPARE_IMAGES_TOPIC`. `POST /` uses `process.env.BOOKKEEPING_QUERIES_TOPIC`. Responses `201` with `{ content: post }` on success, `500` on error.
- **`models/producer.model.js`**: `producerMessage(topic, request)` delegates to `produceMessage` from `../src/producer` and resolves with a spread of `request` (promise resolves after scheduling produce).
- **`src/producer.js`**: `node-rdkafka` producer; `produceMessage(topic, topic_object)` serializes `topic_object` as JSON to a Buffer, produces to the given topic with key `message`, flush/disconnect pattern. Uses `KAFKA_USERNAME`, `KAFKA_PASSWORD`, `KAFKA_PROTOCOL`, `KAFKA_CLIENT_ID`, `KAFKA_MECHANISMS`, `KAFKA_BOOTSTRAP_SERVER`.
