# Encrypt or decrypt company text

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Encrypt or decrypt company text |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Admin (authenticated callers with `companies` resource `full` access) |
| **Business Outcome** | Sensitive plain-text values used in accounting and admin workflows can be protected at rest or in transit (encrypt) and recovered when needed (decrypt), using a shared server-side key. |
| **Entry Point / Surface** | `sleek-back` HTTP API: `POST /v2/encode/encrypt` and `POST /v2/encode/decrypt` (mounted in `app-router.js` under `/v2/encode`). Requires `Authorization` via `userService.authMiddleware` and `accessControlService.can("companies", "full")`. No Sleek app screen path is defined in this code. |
| **Short Description** | Accepts JSON body `{ "text": "<string>" }`, encrypts with AES-256-CBC (key/IV derived from configured secret) and returns `{ encryptedData: "<hex>" }`, or decrypts hex ciphertext and returns `{ decryptedData: "<plain text>" }`. Errors surface as `500` with default error shape. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Config / ops**: production uses `process.env.ENCRYPT_KEY`; non-production uses `config.encryption.key`. **Consumers**: any internal or app flow that calls these endpoints to wrap or unwrap sensitive strings for accounting/admin use. **Downstream**: callers must store or transmit the hex payload they receive; no persistence layer in this module. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | None — no MongoDB reads or writes in this flow. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether a separate permission test exists for users who pass auth but lack `companies` `full` (tests cover 401 for bad token, not 403 for insufficient scope). Whether encryption is intended to be company-scoped or global — implementation uses one shared key, not per-company material. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/encrypt-decrypt.js`

- **`buildPostRoute`**: registers `POST` routes with `userService.authMiddleware`, `accessControlService.can("companies", "full")`, and the handler.
- **`/encrypt`** → `encryptDecryptHandler.encryptString`.
- **`/decrypt`** → `encryptDecryptHandler.decryptString`.

### `app-router.js`

- **`router.use("/v2/encode", require("./controllers-v2/encrypt-decrypt"))`** — full paths `POST /v2/encode/encrypt`, `POST /v2/encode/decrypt`.

### `controllers-v2/handlers/encrypt-decrypt/encrypt-decrypt-handler.js`

- **`encryptString`**: reads `req.body.text`, calls `encryptUtil.encryptString`, responds `{ encryptedData: encryptedString.toString('hex') }` (util already returns hex string; see util).
- **`decryptString`**: reads `req.body.text`, calls `encryptUtil.decryptString`, responds `{ decryptedData: decryptedString.toString() }`.
- **Errors**: `catch` → `500` JSON with `errors.default_error_500()`.

### `controllers-v2/handlers/encrypt-decrypt/encrypt-decrypt-util.js`

- **Secret**: `production` → `process.env.ENCRYPT_KEY`; else `config.encryption.key`.
- **`encryptString`**: MD5-derived key and IV from password; **`crypto.createCipheriv('aes-256-cbc', ...)`**; returns **hex string** of ciphertext.
- **`decryptString`**: normalizes input (`-`/`_` to `+`/`/`); rebuilds same key/IV; **`createDecipheriv('aes-256-cbc', ...)`**; returns UTF-8 string.

### `tests/controllers-v2/encrypt-decrypt/encrypt-decrypt-test.js`

- Supertest against `POST /v2/encode/encrypt` and `/decrypt` with user having `companies: "full"`; asserts round-trip and `401` for bad `Authorization`.
