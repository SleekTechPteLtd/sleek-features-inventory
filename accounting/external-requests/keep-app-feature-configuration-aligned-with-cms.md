# Keep app feature configuration aligned with CMS

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Keep app feature configuration aligned with CMS |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | When CMS content for app features changes, the receipts service refreshes its cached copy so feature-related behavior matches the latest published configuration. |
| **Entry Point / Surface** | Sleek Receipts service — External API base `/api/external` — `POST /cms/cache/update` with JSON body `{ model, entity }`. Intended for CMS or platform integrations (webhook/callback), not an end-user app screen. |
| **Short Description** | Delegates to `sleek-cms-util` `CacheManager.refreshCache` for the given CMS `model` and `entity`, using Redis-backed cache keys scoped under the shared CMS config (`baseKey` `cms`, `modules` includes `app-features`). Separately, on startup in non-test/non-development environments, the service may sync the full app-feature list from Strapi into a local mock-data file for offline/test fallbacks. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: Sleek CMS (Strapi) via `SLEEK_CMS_URL` / `SLEEK_CMS_TOKEN`. Shared library `sleek-cms-util` with Redis getters/setters from `cms-util-setup-singleton`. Downstream: any code that resolves app features through `app-features-util` (`getAppFeaturesByName`, `getAppFeatureList`) after cache refresh. Related: `syncAppFeatures` / `createFile` writes `src/constants/app-features-mock-data.js` on boot. |
| **Service / Repository** | sleek-receipts, sleek-cms-util (npm) |
| **DB - Collections** | None for this flow — Redis cache keys only (MongoDB not touched by `updateAppFeatureCache`). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether `/api/external` routes (including this endpoint) are protected by auth, API gateway, or private network only is not defined in the reviewed files. Exact `model` / `entity` values and contract from the CMS side are not visible in-repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/routes/external-requests.js`**: `router.post("/cms/cache/update", …)` reads `model` and `entity` from `req.body`, calls `appFeatureUtil.updateAppFeatureCache({ model, entity })`, returns `200` with `{}` on success; logs errors on failure. Router is mounted at `/api/external` in `index.js`.
- **`src/utils/app-features-util.js`**: `updateAppFeatureCache` instantiates `cmsUtil.CacheManager()` from `CmsUtilSetup.getInstance()` and awaits `cacheManager.refreshCache({ model, entity })`. Also exports `getAppFeaturesByName` / `getAppFeatureList` (Strapi `AppFeaturesModule` with mock-data fallback), `syncAppFeatures` + `createFile` to regenerate `app-features-mock-data.js`.
- **`src/utils/cms-util-setup-singleton.js`**: Wires `sleek-cms-util` with Redis `getRedisCache` / `setRedisCache` / `deleteRedisCache`, API base URL and token from env, and cache settings including `modules: ['app-features']`.
- **`index.js`**: `app.use("/api/external", ExternalRequestsRouter)`; calls `appFeatureUtil.syncAppFeatures()` when `NODE_ENV` is not `test` or `development` (startup sync distinct from per-entity cache refresh).
