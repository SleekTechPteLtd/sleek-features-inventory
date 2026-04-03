# Download recovery report

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Download recovery report |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal operators (Admin) |
| **Business Outcome** | Operators can export recovery-related data as a CSV for offline review, auditing, or handoff to another team. |
| **Entry Point / Surface** | Sleek Admin > Mailroom area — Recovery (`/admin/recovery/`; webpack entry `admin/recovery` → `src/views/admin/recovery.js`). Primary toolbar: **Download Recovery Report**. |
| **Short Description** | A single toolbar action downloads a CSV by requesting the main API endpoint that generates the recovery report. The browser saves the file using the filename from the `Content-Disposition` header. The page body is empty; the value is the export action. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Main API**: `GET ${getBaseUrl()}/admin/recovery/generate-csv` (authenticated fetch + blob download). Related admin recovery flows: recovery file upload/list/reconcile under `admin/recovery/recovery-files` and `api.getRecoveryFiles` / `reconcileFiles` — separate capabilities. `api.generateRecoveryCSV` (POST to the same path) exists in `api.js` but is not wired to this view. |
| **Service / Repository** | sleek-website; Sleek main API (`api.sleek.sg` / env) |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | CSV column layout and server-side filters are defined in the main API, not in sleek-website; confirm whether any client should use `generateRecoveryCSV` (POST) vs the GET used here. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **View**: `src/views/admin/recovery.js` — `AdminRecoveryView` with `sidebarActiveMenuItemKey="mailroom"`, `renderPrimaryToolbarContent` → Blueprint **Download Recovery Report** → `onClickDownloadReport` → `viewUtil.downloadFile(\`${api.getBaseUrl()}/admin/recovery/generate-csv\`)`. `renderBodyContent` returns `null`. `componentDidMount` → `api.getUser()` for layout user; `checkResponseIfAuthorized` on error.
- **Download helper**: `src/utils/view.js` — `downloadFile(fileUrl)` delegates to `api.downloadFile`, reads response as blob, parses `Content-Disposition` / `content-disposition` for `filename=...`, triggers browser download (includes IE/Edge `msSaveOrOpenBlob` branch).
- **API client**: `src/utils/api.js` — `downloadFile(urlString, options)` uses `getResource` (GET) with default JSON headers stripped (`Accept` / `Content-Type` removed). Separately, `generateRecoveryCSV(companyServiceId, options)` → `postResource` to `${getBaseUrl()}/admin/recovery/generate-csv` — exported but not referenced by `recovery.js`.
- **Routing / build**: `webpack/paths.js` — `"admin/recovery": "./src/views/admin/recovery.js"`; `webpack.common.js` — outputs `admin/recovery/index.html`.
