# Export document HTML to PDF

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Export document HTML to PDF |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (authenticated admin API with `document_templates` **read** permission) |
| **Business Outcome** | Operations staff turn sanitized HTML (including output from templated document generation) into a downloadable PDF with predictable layout defaults and safe rendering options, for sharing or filing. |
| **Entry Point / Surface** | Authenticated admin HTTP API on sleek-back: `POST /admin/document-templates/convert-html-to-pdf` (`userService.authMiddleware` + `accessControlService.can("document_templates", "read")`). Often chained after `POST /admin/document-templates/:templateId/generate-doc-from-data` (which returns `{ htmlResult }`). Exact Sleek admin UI label is not defined in the referenced files. |
| **Short Description** | Accepts `htmlToConvert` and optional `options`, sanitizes the request body and HTML, whitelists PDF engine options and merges them with regional `config.pdfFormat`, strips dangerous PDF options, wraps HTML for consistent TinyMCE-style fonts and layout, then renders a PDF buffer and returns it as `application/pdf` with attachment filename `converted.pdf`. |
| **Variants / Markets** | SG, HK, UK, AU (default PDF layout comes from `config.pdfFormat` in each region’s `multi-platform/config/*/default.json`; not a separate product “variant” beyond deployment config). |
| **Dependencies / Related Flows** | **Upstream** — HTML produced by `documentTemplateService.generateContentFromData` via `POST .../generate-doc-from-data`, or any other trusted admin-supplied HTML. **Rendering** — `html-pdf` via `pdf-utils.createPDFBufferFromHtml`; `pdf-utils.wrapHTMLContent` injects shared CSS/fonts and hides certain merge-field markers for print. **Security** — `mongo-sanitize` on body; `sanitize-html` allowlist; explicit removal of `localUrlAccess`, `phantomPath`, `phantomArgs` after merge. **Related** — other controllers reuse `config.pdfFormat` + `pdf-utils` (e.g. questionnaire utilities, Camunda document generators); not specific to this route. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | None — this endpoint does not read or write MongoDB; it only transforms the request body to a PDF response. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether long-term migration off `html-pdf`/Phantom-style rendering is planned (shared dependency across multiple PDF flows). Whether clients ever need a custom download filename instead of fixed `converted.pdf`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/document-template-controller.js`

- **`POST /admin/document-templates/convert-html-to-pdf`** — `userService.authMiddleware`, `accessControlService.can("document_templates", "read")`.
- **Body validation** — `validationUtils.validateOrReject`: `htmlToConvert` (string, required), `options` (object, optional).
- **Sanitization** — `reqBody = sanitize(reqBody)` (`mongo-sanitize`).
- **PDF option whitelist** — only `format`, `orientation`, `border`, `headerTemplate`, `footerTemplate`, `margin`, `scale`, `printBackground`, `landscape`, `pageRanges`, `width`, `height` copied from `reqBody.options` into `safeOptions`.
- **Merge** — `merge({}, config.pdfFormat, safeOptions)`; then `delete options.localUrlAccess`, `delete options.phantomPath`, `delete options.phantomArgs`.
- **HTML sanitization** — `sanitizeHtml(reqBody.htmlToConvert, …)` with extended tags (`style`, `link`, `html`, `head`, `body`, `table`) and `allowVulnerableTags: true`.
- **PDF** — `pdfUtils.wrapHTMLContent(htmlClean)` then `pdfUtils.createPDFBufferFromHtml(htmlToConvert, options)`.
- **Response** — `Content-Type: application/pdf`, `Content-disposition: attachment; filename=converted.pdf`, `res.send(buffer)`; errors `422` JSON.

### `utils/pdf-utils.js`

- **`wrapHTMLContent(htmlContent)`** — Prepends shared document head (TinyMCE content CSS, Google font imports, Roboto, layout helpers, `html { zoom: 75%; }`). If input contains `<style>`, splices after opening style; else if `<body>` exists, inserts after synthetic `</head>`; else wraps fragment in `<body>...</body></html>`. Replaces several `{signature:`, `{i:`, `{datepicker:`, `{dynamic:` prefixes with white text spans; closes spans after specific `}` patterns for template placeholders.
- **`createPDFBufferFromHtml(htmlContent, options)`** — `pdf.create(htmlContent, options).toBuffer` (Promise wrapper); uses `html-pdf` module.
- **`createPDFStreamFromHtml`** — same library `.toStream` (not used by this controller route).

### `multi-platform/config/*/default.json` (e.g. SG)

- **`pdfFormat`** — default `format` (e.g. `"A4"`), `orientation`, `border` margins, `header`/`footer` heights; merged into the convert endpoint’s options.
