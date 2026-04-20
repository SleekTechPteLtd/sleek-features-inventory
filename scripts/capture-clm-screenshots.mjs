#!/usr/bin/env node
/**
 * Captures screenshots for CLM inventory features under clm/feature-set (recursive .md files).
 * by parsing the master sheet "Entry Point / Surface" cell for SPA-style routes in backticks.
 * HTTP verb lines (`GET /path`, `POST /path`, …) are skipped — those document APIs, not navigable UI.
 *
 * Uses three origins (and three localStorage exports):
 *   - Sleek Billings Frontend (staff SPA) — CLM_BILLINGS_BASE (default https://sg-billings-sit.sleek.com)
 *   - Admin App — CLM_ADMIN_BASE (default https://admin-sit.sleek.sg)
 *   - Customer App — CLM_CUSTOMER_BASE (default https://sg-app-sit.sleek.com)
 *
 * Auth: inject JSON key/value maps before navigation (export Application → Local Storage from a live session):
 *   CLM_BILLINGS_AUTH   default ~/Downloads/billings-localstorage.json
 *   CLM_ADMIN_AUTH      default ~/Downloads/admin-app-localstorage.json
 *   CLM_CUSTOMER_AUTH   default ~/Downloads/customer-app-localstorage.json
 *
 * Usage:
 *   node scripts/capture-clm-screenshots.mjs --dry-run
 *   node scripts/capture-clm-screenshots.mjs --prune   # delete PNGs not in current inventory plan
 *   node scripts/capture-clm-screenshots.mjs
 *
 * Env:
 *   CLM_BILLINGS_BASE, CLM_ADMIN_BASE, CLM_CUSTOMER_BASE,
 *   CLM_BILLINGS_AUTH, CLM_ADMIN_AUTH, CLM_CUSTOMER_AUTH
 *   CLM_ADMIN_COMPANY_ID — default company id for `/admin/company-billing/` when `cid` is omitted in the inventory cell
 *   CLM_ADMIN_SUBSCRIPTION_ID — optional; replaces placeholder subscriptionId in Entry Point routes
 */

import { chromium } from 'playwright';
import { readFileSync, mkdirSync, readdirSync, statSync, unlinkSync, existsSync } from 'fs';
import { join, dirname, relative, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '..');
const FEATURE_ROOT = join(REPO_ROOT, 'clm', 'feature-set');
const OUTPUT_BASE = join(REPO_ROOT, 'by-surface', 'clm', 'screenshots');

function trimBaseUrl(url) {
  return String(url || '').replace(/\/+$/, '');
}

const BILLINGS_BASE = trimBaseUrl(process.env.CLM_BILLINGS_BASE || 'https://sg-billings-sit.sleek.com');
const ADMIN_BASE = trimBaseUrl(process.env.CLM_ADMIN_BASE || 'https://admin-sit.sleek.sg');
const CUSTOMER_BASE = trimBaseUrl(process.env.CLM_CUSTOMER_BASE || 'https://sg-app-sit.sleek.com');
const BILLINGS_AUTH_FILE = process.env.CLM_BILLINGS_AUTH || join(process.env.HOME, 'Downloads', 'billings-localstorage.json');
const ADMIN_AUTH_FILE = process.env.CLM_ADMIN_AUTH || join(process.env.HOME, 'Downloads', 'admin-app-localstorage.json');
const CUSTOMER_AUTH_FILE = process.env.CLM_CUSTOMER_AUTH || join(process.env.HOME, 'Downloads', 'customer-app-localstorage.json');

const VIEWPORT = { width: 1400, height: 900 };
const WAIT_MS = Number(process.env.CLM_SCREENSHOT_WAIT_MS || 5000);

/** Default SIT company for `/admin/company-billing/` when `cid` is omitted (same default as capture-admin-app-screenshots.mjs). */
const CLM_ADMIN_COMPANY_ID =
  process.env.CLM_ADMIN_COMPANY_ID || '6768ce4b939e53003e993169';
/** Optional subscription id for deep-linking subscription detail (`subscriptionId=` query). */
const CLM_ADMIN_SUBSCRIPTION_ID = process.env.CLM_ADMIN_SUBSCRIPTION_ID || '';

const ARGS = new Set(process.argv.slice(2));
const DRY_RUN = ARGS.has('--dry-run');
const PRUNE = ARGS.has('--prune');

/** Entry cells containing these substrings are treated as non-UI (no screenshot). */
const SKIP_ENTRY_SUBSTRINGS = [
  'no ui surface',
  'no direct frontend',
  'no user-facing',
  'system-to-system',
  'network-restricted',
  'background system',
  'internal cron',
  'cron job',
  'scheduled cron',
  'daily cron',
  'automated —',
  'automated -',
  'internal test infrastructure',
  'internal rest api',
  'stripe-facing http endpoint',
  'tokenized email link',
  'customer-facing checkout',
  'external payment portal',
  'no dedicated frontend',
  'no dedicated ui',
  'internal api:',
  'no ui —',
  'no ui -',
];

/** Path patterns that are REST/API, not SPA routes (exclude from capture). */
function isExcludedApiPath(path) {
  const p = path.toLowerCase();
  if (p.includes('*')) return true;
  if (p.startsWith('/v1/') || p.startsWith('/v2/') || p.startsWith('/api/')) return true;
  if (p === '/webhooks' || p.startsWith('/webhooks/')) return true;
  if (p.match(/^\/(get|post|put|delete|patch)\b/)) return true;
  // Xero REST mounts under /xero/ except known SPA pages
  if (p.startsWith('/xero/') && !p.startsWith('/xero-webhook')) return true;
  if (p === '/xero') return true;
  // Common NestJS paths mistaken for UI in inventory text
  if (
    p.startsWith('/invoices/reconcile') ||
    p.startsWith('/invoices/consider') ||
    p.startsWith('/invoices/auto-upgrade')
  )
    return true;
  if (p.startsWith('/tasks/retry') || p.startsWith('/tasks/change-task') || p.startsWith('/tasks/bulk-')) return true;
  if (p.startsWith('/subscription-auto-renewal/')) return true;
  if (p.startsWith('/queue-jobs/')) return true;
  if (p.startsWith('/jobs/')) return true;
  // Subscription-config: Nest sync / promote endpoints (not navigable SPA pages)
  if (p === '/subscription-config/sync' || p === '/subscription-config/changes/sync') return true;
  return false;
}

/**
 * Staff-only billings surfaces: never treat as customer app even if the cell mentions "customer" elsewhere.
 */
function isBillingsStaffSpaPath(path) {
  const p = path.toLowerCase();
  if (p.startsWith('/admin')) return true;
  if (
    p.startsWith('/subscription-config') ||
    p.startsWith('/delivery-config') ||
    p.startsWith('/delivery/') ||
    p.startsWith('/stripe-webhook') ||
    p.startsWith('/xero-webhook') ||
    p.startsWith('/queue-jobs') ||
    p.startsWith('/jobs/')
  )
    return true;
  return false;
}

const HTTP_VERB_RE = /\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(\/[^\s`'"<>]+)/gi;

function normalizeRoute(raw) {
  let s = raw.trim();
  s = s.replace(/^[`'" ]+|[`'" ]+$/g, '');
  if (!s.startsWith('/')) s = `/${s}`;
  // Vue/React param segments — list pages still work if we drop /:id tail
  s = s.replace(/\/:[a-zA-Z_][a-zA-Z0-9_]*/g, '');
  if (s.length > 1 && s.endsWith('/')) s = s.slice(0, -1);
  return s;
}

/** Strip `VERB /path` API fragments so we only match standalone SPA paths in mixed prose. */
function stripHttpVerbApiSegments(s) {
  return s.replace(HTTP_VERB_RE, ' ').replace(/\s+/g, ' ').trim();
}

/**
 * Pull route-like strings from the Entry Point / Surface markdown cell.
 * Skips backticks that look like code snippets (devMode, ternary, etc.).
 */
function extractRoutesFromEntryCell(cell) {
  const routes = new Set();
  const ticked = cell.match(/`([^`]+)`/g) || [];
  for (const block of ticked) {
    const inner = block.slice(1, -1).trim();
    if (inner.includes('===') || inner.includes('!==')) continue;
    const parts = inner.split(',').map((p) => p.trim());
    for (let part of parts) {
      part = part.replace(/^\(\s*|\s*\)$/g, '').replace(/^\s*and\s+/i, '');
      // `GET /path`, `POST /path`, … = REST documentation — not a SPA route to open in a browser
      const verbPath = part.match(/^\s*(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(\/[^\s`]+)/i);
      if (verbPath) {
        continue;
      }
      // Paths documented without a leading slash, e.g. `analytics/user-activity` (must run before
      // the slash-regex pass, which would otherwise match only `/user-activity`).
      if (/^[a-z][a-z0-9/-]*$/i.test(part) && part.includes('/')) {
        const r = normalizeRoute(`/${part}`);
        if (!isExcludedApiPath(r)) routes.add(r);
        continue;
      }
      // Remove embedded `VERB /path` segments so slash-regex does not pick API paths from mixed text
      const withoutVerbs = stripHttpVerbApiSegments(part);
      // Include optional query string so `/admin/company-billing/?cid=…&tab=1` is one route.
      const pathMatches = withoutVerbs.match(
        /\/[a-zA-Z0-9_./-]+(?:\?[a-zA-Z0-9_=&.%<>+-]*)?/gi,
      );
      if (pathMatches) {
        for (const pm of pathMatches) {
          const r = normalizeRoute(pm);
          if (!isExcludedApiPath(r)) routes.add(r);
        }
      }
    }
  }
  return [...routes]
    .map((r) => finalizeAdminCompanyBillingRoute(r))
    .filter((r) => r.length > 1 && !isExcludedApiPath(r));
}

/**
 * Ensures `cid` on Company Billing admin routes; replaces placeholder subscription ids when env is set.
 */
function finalizeAdminCompanyBillingRoute(route) {
  let r = route;
  const lower = r.toLowerCase();
  if (!lower.startsWith('/admin/company-billing')) return r;

  if (!/[?&]cid=/.test(r)) {
    const sep = r.includes('?') ? '&' : '?';
    r = `${r}${sep}cid=${encodeURIComponent(CLM_ADMIN_COMPANY_ID)}`;
  }

  if (CLM_ADMIN_SUBSCRIPTION_ID && /subscriptionId=(<[^>]+>|YOUR_|PLACEHOLDER|TBD)/i.test(r)) {
    r = r.replace(/subscriptionId=[^&]*/, `subscriptionId=${encodeURIComponent(CLM_ADMIN_SUBSCRIPTION_ID)}`);
  }

  return r;
}

function parseEntryPoint(md) {
  const line = md.split('\n').find((l) => l.includes('**Entry Point / Surface**'));
  if (!line) return { cell: '', raw: '' };
  const m = line.match(/\|\s*\*\*Entry Point \/ Surface\*\*\s*\|\s*([^|]*)\|/);
  const cell = m ? m[1].trim() : '';
  return { cell, raw: line };
}

function shouldSkipEntryCell(cell) {
  const lower = cell.toLowerCase();
  return SKIP_ENTRY_SUBSTRINGS.some((s) => lower.includes(s.toLowerCase()));
}

/**
 * Resolves capture target: admin-sit (admin), sg-app (customer), or billings SPA (billings).
 * Customer is driven by Entry Point / Surface text (Customer App, Sleek Customer App, …) and path.
 */
function resolveSurface(cell, path) {
  const lower = cell.toLowerCase();
  if (lower.includes('ops portal') || lower.includes('service-delivery-api')) return 'skip';

  if (path.startsWith('/admin')) return 'admin';

  const customerHints =
    lower.includes('customer app') ||
    lower.includes('sleek customer app') ||
    lower.includes('sg-app-sit') ||
    (lower.includes('client-facing') && lower.includes('customer'));

  const billingsHints =
    lower.includes('sleek billings') ||
    lower.includes('billings app') ||
    lower.includes('billings admin') ||
    lower.includes('billings frontend') ||
    lower.includes('developer tools') ||
    lower.includes('sleek billings admin');

  const adminHints =
    (lower.includes('admin app') && !lower.includes('billings')) ||
    lower.includes('sleek admin app') ||
    (lower.includes('sleek admin') &&
      !lower.includes('billings') &&
      (lower.includes('company overview') || lower.includes('analytics >') || lower.includes('/admin/')));

  if (path.startsWith('/customer')) return 'customer';

  if (customerHints && billingsHints) {
    if (isBillingsStaffSpaPath(path)) return 'billings';
    if (path.startsWith('/customer')) return 'customer';
    return 'billings';
  }

  if (customerHints && !isBillingsStaffSpaPath(path)) return 'customer';

  if (adminHints && !billingsHints) return 'admin';
  if (billingsHints) return 'billings';
  return 'billings';
}

function walkMarkdownFiles(dir, acc = []) {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) walkMarkdownFiles(full, acc);
    else if (name.endsWith('.md')) acc.push(full);
  }
  return acc;
}

function loadAuthJson(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return null;
  }
}

function slugFromFile(filePath, route) {
  const rel = relative(FEATURE_ROOT, filePath).replace(/\.md$/, '');
  const qIndex = route.indexOf('?');
  let pathPart = qIndex === -1 ? route : route.slice(0, qIndex);
  pathPart = pathPart.replace(/\/+$/, '');
  let safeRoute = pathPart.replace(/^\//, '').replace(/\//g, '__');
  if (qIndex !== -1) {
    const params = new URLSearchParams(route.slice(qIndex + 1));
    const tab = params.get('tab');
    if (tab !== null && tab !== '') safeRoute += `-tab${tab}`;
    if (params.get('subscriptionId')) safeRoute += '-subscriptionDetail';
  }
  return `${rel}__${safeRoute}`;
}

/**
 * Same route → output mapping as capture; used for --prune and --dry-run.
 * @returns {{ seen: Map, billingsJobs: object[], adminJobs: object[], customerJobs: object[] }}
 */
function buildScreenshotPlan() {
  const files = walkMarkdownFiles(FEATURE_ROOT);
  /** @type {Map<string, { file: string, route: string, cell: string, surface: string }>} */
  const seen = new Map();

  for (const file of files) {
    const md = readFileSync(file, 'utf8');
    const { cell } = parseEntryPoint(md);
    if (!cell || shouldSkipEntryCell(cell)) continue;

    const routes = extractRoutesFromEntryCell(cell);
    for (const route of routes) {
      if (isExcludedApiPath(route)) continue;
      const surface = resolveSurface(cell, route);
      if (surface === 'skip') continue;
      // Per markdown file so multiple features can share the same SPA URL with different screenshots.
      const key = `${file}|${surface}|${route}`;
      if (seen.has(key)) continue;
      seen.set(key, { file, route, cell, surface });
    }
  }

  const billingsJobs = [];
  const adminJobs = [];
  const customerJobs = [];

  for (const { file, route, surface } of seen.values()) {
    const slug = slugFromFile(file, route);
    const subdir = dirname(relative(FEATURE_ROOT, file));
    const outDir = join(OUTPUT_BASE, subdir);
    mkdirSync(outDir, { recursive: true });
    const outputPath = join(outDir, `${slug.split('/').pop()}.png`);

    const job = { slug, route, outputPath, file };
    if (surface === 'admin') adminJobs.push(job);
    else if (surface === 'customer') customerJobs.push(job);
    else billingsJobs.push(job);
  }

  return { seen, billingsJobs, adminJobs, customerJobs };
}

function walkPngFiles(dir, acc = []) {
  if (!existsSync(dir)) return acc;
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) walkPngFiles(full, acc);
    else if (name.endsWith('.png')) acc.push(full);
  }
  return acc;
}

/**
 * Remove PNGs under OUTPUT_BASE that are not in the current plan (absolute paths).
 */
function pruneOrphanScreenshots(expectedAbsolutePaths) {
  const expected = new Set(expectedAbsolutePaths.map((p) => resolve(p)));
  const all = walkPngFiles(OUTPUT_BASE);
  let removed = 0;
  for (const p of all) {
    const abs = resolve(p);
    if (!expected.has(abs)) {
      unlinkSync(abs);
      console.log(`  removed: ${relative(REPO_ROOT, abs)}`);
      removed++;
    }
  }
  return removed;
}

async function captureWithContext(browser, label, baseUrl, authData, jobs) {
  if (jobs.length === 0) return { ok: 0, fail: 0 };
  if (!authData) {
    console.error(`\n✗ Missing or unreadable auth file for ${label}. Skipping ${jobs.length} screenshot(s).`);
    return { ok: 0, fail: jobs.length };
  }

  const context = await browser.newContext({ viewport: VIEWPORT });
  await context.addInitScript((data) => {
    for (const [key, value] of Object.entries(data)) {
      if (value !== null && value !== undefined) localStorage.setItem(key, value);
    }
  }, authData);

  const page = await context.newPage();
  let ok = 0;
  let fail = 0;

  for (const job of jobs) {
    const outputPath = job.outputPath;
    console.log(`\n→ [${label}] ${job.slug}`);

    try {
      await page.goto(`${baseUrl}${job.route}`, { waitUntil: 'load', timeout: 45000 });
      const currentUrl = page.url();
      if (currentUrl.includes('/login') || currentUrl.includes('/auth') || currentUrl.includes('auth0')) {
        console.error('  ✗ Redirected to login — token may be expired or wrong origin');
        fail++;
        continue;
      }
      await page.waitForTimeout(WAIT_MS);
      if (job.interact) {
        try {
          await job.interact(page);
        } catch (err) {
          console.warn(`  ⚠ Interaction skipped: ${err.message}`);
        }
      }
      await page.screenshot({ path: outputPath, fullPage: false });
      console.log(`  ✓ ${outputPath}`);
      ok++;
    } catch (err) {
      console.error(`  ✗ Failed: ${err.message}`);
      fail++;
    }
  }

  await context.close();
  return { ok, fail };
}

async function main() {
  const { seen, billingsJobs, adminJobs, customerJobs } = buildScreenshotPlan();

  const allJobs = [...billingsJobs, ...adminJobs, ...customerJobs];
  const expectedPaths = allJobs.map((j) => resolve(j.outputPath));

  if (PRUNE) {
    const n = pruneOrphanScreenshots(expectedPaths);
    console.log(`\nPrune: removed ${n} orphan PNG(s) not in the current capture plan.`);
    console.log(`Expected: ${expectedPaths.length} screenshot(s) under by-surface/clm/screenshots/`);
    return;
  }

  console.log(
    `CLM screenshot plan: ${billingsJobs.length} billings (${BILLINGS_BASE}), ${adminJobs.length} admin (${ADMIN_BASE}), ${customerJobs.length} customer (${CUSTOMER_BASE})`
  );
  console.log(`Unique routes from Entry Point / Surface: ${seen.size}`);

  if (DRY_RUN) {
    for (const j of billingsJobs) console.log(`  [billings] ${BILLINGS_BASE}${j.route}  →  ${j.outputPath}`);
    for (const j of adminJobs) console.log(`  [admin] ${ADMIN_BASE}${j.route}  →  ${j.outputPath}`);
    for (const j of customerJobs) console.log(`  [customer] ${CUSTOMER_BASE}${j.route}  →  ${j.outputPath}`);
    console.log('\n--dry-run: no browser launched.');
    return;
  }

  const billingsAuth = loadAuthJson(BILLINGS_AUTH_FILE);
  const adminAuth = loadAuthJson(ADMIN_AUTH_FILE);
  const customerAuth = loadAuthJson(CUSTOMER_AUTH_FILE);

  console.log(`Launching browser...`);
  const browser = await chromium.launch({ headless: false, slowMo: 50 });

  const r1 = await captureWithContext(browser, 'billings', BILLINGS_BASE, billingsAuth, billingsJobs);
  const r2 = await captureWithContext(browser, 'admin', ADMIN_BASE, adminAuth, adminJobs);
  const r3 = await captureWithContext(browser, 'customer', CUSTOMER_BASE, customerAuth, customerJobs);

  await browser.close();

  const ok = r1.ok + r2.ok + r3.ok;
  const fail = r1.fail + r2.fail + r3.fail;
  console.log(`\n${'─'.repeat(60)}`);
  console.log(`Done. ${ok}/${ok + fail} screenshots captured.`);
  if (fail > 0) console.log(`${fail} failed — check output above.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
