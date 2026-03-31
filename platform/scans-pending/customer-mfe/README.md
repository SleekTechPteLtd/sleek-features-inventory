# customer-mfe — scan notes (placeholder)

**Vue** customer application (`customer-mfe`, mainly `customer-main/`).

See [../../inventory-scope-and-domains.md](../../inventory-scope-and-domains.md) (customer-mfe section) for matching UI proxies to the correct spreadsheet **Domain**, not only **Platform**. Full three-repo map: [../../cross-repo-sleek-surfaces-map.md](../../cross-repo-sleek-surfaces-map.md).

## Authentication UI / proxies

**Do not** create parallel **Authentication** inventory rows for login, OTP, password reset, or registration that duplicate **Sleek Auth** — see [../../authentication/README.md](../../authentication/README.md#scope-no-duplicate-auth-rows). Legacy proxies (`login-proxy.js`, `two-factor-authentication/*`, etc.) call **sleek-back**; treat as legacy stack only.

## In scope

Document capabilities where the **customer app** is the right surface and the story is **not** “same as Sleek Auth.” File `.md` under the appropriate `platform/<category>/` folder with **Evidence** pointing here and to backends (often `sleek-back`).

## Evidence hotspots

- `customer-main/src/proxies/back-end/**`
- `customer-main/src/modules/**`

## Partner white-label

When the shell runs on a **non-Sleek hostname**, browser `Origin` is how `sleek-back` resolves `req.partner` — see [../../external-integrations/sleek-back-partner-origin-white-label.md](../../external-integrations/sleek-back-partner-origin-white-label.md).

## Related

- [sleek-back README](../sleek-back/README.md)
- [Platform root README](../../README.md)
