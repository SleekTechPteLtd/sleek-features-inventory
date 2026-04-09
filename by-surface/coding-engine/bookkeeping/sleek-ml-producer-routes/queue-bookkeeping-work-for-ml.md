# Queue bookkeeping work for ML

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Queue bookkeeping work for ML |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Bookkeeping-related work can be handed off asynchronously to ML services via Kafka, so classification, matching, and similar ML pipelines run without the accounting platform blocking on ML latency or implementation details. |
| **Entry Point / Surface** | Internal HTTP API on sleek-ml-node-server: `POST /api/v1/sleek-ml` (JSON body published to `BOOKKEEPING_QUERIES_TOPIC`). Not an end-user app screen; intended for platform or service-to-service calls. A related route `POST /api/v1/sleek-ml/compare-images` publishes to `COMPARE_IMAGES_TOPIC` for image-comparison ML work. |
| **Short Description** | The producer routes accept POST bodies and publish JSON messages to Kafka using `node-rdkafka` (Confluent-style SASL config from environment). The default route targets bookkeeping queries; the compare-images route targets a separate topic for image comparison workloads. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Kafka**: `KAFKA_BOOTSTRAP_SERVER`, `KAFKA_USERNAME`, `KAFKA_PASSWORD`, `KAFKA_PROTOCOL`, `KAFKA_MECHANISMS`, `KAFKA_CLIENT_ID`, plus `BOOKKEEPING_QUERIES_TOPIC` and `COMPARE_IMAGES_TOPIC` for routing. **Upstream**: callers that POST bookkeeping or image payloads. **Downstream**: ML consumers subscribed to those topics. |
| **Service / Repository** | sleek-ml-node-server |
| **DB - Collections** | None (service has no database layer in codebase). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | No authentication or API-key middleware appears on the Express app in-repo; production access control (network, gateway, secrets) is deployment-specific. `producer.model` resolves the HTTP response immediately after scheduling `produceMessage` without awaiting Kafka delivery confirmation—operational implications for “success” semantics. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`routes/index.routes.js`**: Mounts producer routes at `/api/v1/sleek-ml`.
- **`routes/producer.routes.js`**: `POST /` → `producer.producerMessage(bookkeeping_queries_topic, req.body)` with `201` and `{ content: post }`; `POST /compare-images` → same pattern with `compare_images_topic`. Errors return `500` with `{ message: err.message }`.
- **`models/producer.model.js`**: Wraps `producer.producerMessage` from `src/producer`; resolves a promise with a spread of the request object after calling `produceMessage` (does not await Kafka delivery).
- **`src/producer.js`**: `produceMessage(topic, topic_object)` uses `node-rdkafka` `Producer`, `JSON.stringify` payload, `produce` with key `'message'`, `flush` then `disconnect`; SASL/bootstrap from `process.env`.
