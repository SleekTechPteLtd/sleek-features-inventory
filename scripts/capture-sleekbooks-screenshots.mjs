#!/usr/bin/env node
/**
 * Captures screenshots of 16 SleekBooks (ERPNext) features from au-books-staging.sleek.com
 * Auth: opens the browser, navigates to the site, then waits up to 2 minutes for you
 *       to log in. Once the app page is detected, screenshots begin automatically.
 *
 * Usage: node scripts/capture-sleekbooks-screenshots.mjs
 */

import { chromium } from 'playwright';
import { mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUTPUT_BASE = join(__dirname, '..', 'by-surface', 'sleekbooks', 'screenshots');
const BASE_URL = 'https://au-books-staging.sleek.com';
const VIEWPORT = { width: 1400, height: 900 };

// Ensure output directories exist
for (const section of ['banking', 'invoicing', 'reports', 'setup']) {
  mkdirSync(join(OUTPUT_BASE, section), { recursive: true });
}

const features = [
  // ── Banking & Reconciliation ────────────────────────────────────────────────
  {
    slug: 'banking/bank-reconciliation-tool',
    url: '/app/bank-reconciliation-tool',
  },
  {
    slug: 'banking/cash-coding',
    url: '/app/cash-coding',
  },
  {
    slug: 'banking/bank-statement-import',
    url: '/app/bank-statement-import',
  },
  {
    slug: 'banking/bank-transactions',
    url: '/app/bank-transaction',
  },

  // ── Invoicing & Payments ────────────────────────────────────────────────────
  {
    slug: 'invoicing/sales-invoices',
    url: '/app/sales-invoice',
  },
  {
    slug: 'invoicing/purchase-invoices',
    url: '/app/purchase-invoice',
  },
  {
    slug: 'invoicing/payment-entries',
    url: '/app/payment-entry',
  },
  {
    slug: 'invoicing/journal-entries',
    url: '/app/journal-entry',
  },

  // ── Financial Reports ───────────────────────────────────────────────────────
  {
    slug: 'reports/general-ledger',
    url: '/app/query-report/General%20Ledger',
  },
  {
    slug: 'reports/balance-sheet',
    url: '/app/query-report/Balance%20Sheet',
  },
  {
    slug: 'reports/profit-and-loss',
    url: '/app/query-report/Profit%20and%20Loss%20Statement',
  },
  {
    slug: 'reports/accounts-receivable',
    url: '/app/query-report/Accounts%20Receivable',
  },
  {
    slug: 'reports/bas-statement',
    url: '/app/query-report/Simpler%20BAS%20Statement',
  },

  // ── Setup & Config ──────────────────────────────────────────────────────────
  {
    slug: 'setup/chart-of-accounts',
    url: '/app/account/view/tree',
  },
  {
    slug: 'setup/company',
    url: '/app/company',
  },
  {
    slug: 'setup/find-and-recode',
    url: '/app/find-and-recode',
  },
];

async function main() {
  console.log('Launching browser...');
  const browser = await chromium.launch({ headless: false, slowMo: 50 });
  const context = await browser.newContext({ viewport: VIEWPORT });
  const page = await context.newPage();

  // Navigate to the app — may land on login page
  await page.goto(`${BASE_URL}/app`, { waitUntil: 'load', timeout: 30000 });

  const startUrl = page.url();
  if (startUrl.includes('/login') || startUrl.includes('/auth')) {
    console.log('\n⚠  Not authenticated — please log in in the browser window.');
    console.log('   Waiting up to 2 minutes for you to complete login...\n');
    // Wait until we're redirected away from any login page
    await page.waitForURL((url) => !url.href.includes('/login') && !url.href.includes('/auth'), {
      timeout: 120000,
    });
    console.log('✓ Logged in — starting screenshots.\n');
    // Give ERPNext a moment to finish loading after redirect
    await page.waitForTimeout(3000);
  }

  let failed = 0;

  for (const feature of features) {
    const outputPath = join(OUTPUT_BASE, `${feature.slug}.png`);
    console.log(`\n→ ${feature.slug}`);

    try {
      await page.goto(`${BASE_URL}${feature.url}`, { waitUntil: 'load', timeout: 30000 });

      // Bail if somehow kicked to login mid-run
      const currentUrl = page.url();
      if (currentUrl.includes('/login') || currentUrl.includes('/auth')) {
        console.error('  ✗ Redirected to login — session expired mid-run');
        failed++;
        continue;
      }

      // Wait for ERPNext to render
      await page.waitForTimeout(5000);

      if (feature.interact) {
        try {
          await feature.interact(page);
        } catch (err) {
          console.warn(`  ⚠ Interaction skipped: ${err.message}`);
        }
      }

      await page.screenshot({ path: outputPath, fullPage: false });
      console.log(`  ✓ ${outputPath}`);
    } catch (err) {
      console.error(`  ✗ Failed: ${err.message}`);
      failed++;
    }
  }

  await browser.close();
  console.log(`\n${'─'.repeat(60)}`);
  console.log(`Done. ${features.length - failed}/${features.length} screenshots captured.`);
  if (failed > 0) console.log(`${failed} failed — check output above.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
