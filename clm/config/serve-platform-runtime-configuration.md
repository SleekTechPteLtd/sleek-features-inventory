# Serve Platform Runtime Configuration

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Serve platform runtime configuration |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (billing frontend at app initialisation) |
| **Business Outcome** | Allows the billing frontend to render correctly per market by exposing environment-specific payment methods, bank transfer details, feature flags, and coupon exclusion rules at startup — without requiring authentication. |
| **Entry Point / Surface** | `GET /api/config` — public endpoint consumed by the billing frontend on load |
| **Short Description** | Returns a cached, platform-specific configuration bundle including available payment methods (Stripe + non-Stripe), bank transfer details, subscription config tags, coupon-excluded service codes, feature flags (`SWITCH_TO_SLEEK_BILLINGS`), acquisition links, currency symbol, and server start time. Response is in-memory cached for the lifetime of the server process and HTTP-cached for 1 hour via `Cache-Control: public, max-age=3600`. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Payment request flow (PAYMENT_METHODS drives which Stripe + non-Stripe methods are offered per market); coupon application (COUPON_DEFAULT_EXCLUDED_SERVICE_CODES restricts eligible services); subscription provisioning (SUBCRIPTON_CONFIG_TAGS controls feature tiles); frontend acquisition flows (ACQ_INCORP_LINK, ACQ_TRANSFER_LINK) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | None — reads from environment variables and compile-time static constants only |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | UK `BANK_TRANSFER_DETAILS` reuses SG DBS bank info — likely a copy-paste placeholder; needs verification. `SWITCH_TO_SLEEK_BILLINGS` flag purpose and current state unclear. Which specific frontend apps consume this endpoint (billing app only, or also admin app)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/config/config.controller.ts` — `ConfigController`, registered under `@Controller('api/config')`
- `GET /` handler: `getConfig()` (line 20)
- No auth guards — endpoint is fully public
- `@Header('Cache-Control', 'public, max-age=3600')` applied to the handler (line 19)
- In-memory cache via `this.cachedConfig` field; populated on first request and reused for the process lifetime

### Payload fields (first call builds and caches all except serverStartTime)
| Field | Source |
|---|---|
| `environment` | `NODE_ENV` env var |
| `platform` | `PLATFORM` env var (`sg`, `hk`, `uk`, `au`) |
| `version` | `VERSION` env var |
| `SWITCH_TO_SLEEK_BILLINGS` | env var — feature flag |
| `ACQ_INCORP_LINK` | env var — acquisition incorporation link |
| `ACQ_TRANSFER_LINK` | env var — acquisition transfer link |
| `PAYMENT_METHODS` | `PAYMENT_METHODS[PLATFORM]` from `shared/consts/common.ts` |
| `CURRENCY_SYMBOL` | `CURRENCY_SYMBOL` env var |
| `BANK_TRANSFER_DETAILS` | `BANK_TRANSFER_DETAILS[PLATFORM]` from `shared/consts/common.ts` |
| `SUBCRIPTON_CONFIG_TAGS` | `SUBCRIPTON_CONFIG_TAGS.default` from `shared/consts/common.ts` |
| `COUPON_DEFAULT_EXCLUDED_SERVICE_CODES` | `COUPON_DEFAULT_EXCLUDED_SERVICE_CODES[PLATFORM]` from `shared/consts/common.ts` |
| `serverStartTime` | `Date.now()` captured at controller instantiation — always live |

### Static constants (`src/shared/consts/common.ts`)
- `PAYMENT_METHODS` — per-platform map of Stripe (`card`, `alipay`, `wechat_pay`, `bacs_debit`, `au_becs_debit`) and non-Stripe (`bank_transfer`, `paynow`) methods across four payment contexts: `paymentRequest`, `betaOnboarding`, `manualRenewal`, `default`
- `BANK_TRANSFER_DETAILS` — per-platform local (and international for AU) bank account details with bank name, account number, account name, SWIFT code; HK includes Chinese localisation (`zh`)
- `SUBCRIPTON_CONFIG_TAGS.default` — four tags controlling accounting tile and page visibility in customer + admin apps, and AOQ email suppression
- `COUPON_DEFAULT_EXCLUDED_SERVICE_CODES` — per-platform lists of service codes ineligible for coupon discounts (SG: 28 codes, HK: 17 codes, AU: 7 codes; UK: not present)

### Module registration
- `src/config/config.module.ts` — minimal `@Module({ controllers: [ConfigController] })`, no providers or service layer
- Registered in `src/app.module.ts`
