#!/usr/bin/env node
/**
 * Captures screenshots of all 28 coding engine features from acct-sit.sleek.com
 * Auth is injected from ~/Downloads/sleek-localstorage.json (exported from live session)
 *
 * Usage: node scripts/capture-coding-engine-screenshots.mjs
 */

import { chromium } from 'playwright';
import { readFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUTPUT_BASE = join(__dirname, '..', 'by-surface', 'coding-engine', 'screenshots');
const AUTH_FILE = join(process.env.HOME, 'Downloads', 'sleek-localstorage.json');
const BASE_URL = 'https://acct-sit.sleek.com';
const VIEWPORT = { width: 1400, height: 900 };

// Load session auth from downloaded localStorage export
const authData = JSON.parse(readFileSync(AUTH_FILE, 'utf8'));

// Ensure output directories exist
for (const section of ['documents', 'bank-statements', 'suppliers', 'clients']) {
  mkdirSync(join(OUTPUT_BASE, section), { recursive: true });
}

/**
 * Feature definitions: slug → url + optional interaction before screenshot
 * interact(page) runs after networkidle, before screenshot
 */
const features = [
  // ── Documents ──────────────────────────────────────────────────────────────
  {
    slug: 'documents/document-queue-to-review',
    url: '/home/documents?tab=To+Review&limit=50&skip=0',
  },
  {
    slug: 'documents/document-queue-to-reconcile',
    url: '/home/documents?tab=To+Reconcile&limit=50&skip=0',
  },
  {
    slug: 'documents/document-queue-completed',
    url: '/home/documents?tab=Completed&limit=50&skip=0',
  },
  {
    slug: 'documents/document-queue-all',
    url: '/home/documents?tab=All+documents&limit=50&skip=0',
  },
  {
    slug: 'documents/document-upload',
    url: '/home/documents?tab=To+Review&limit=50&skip=0',
    interact: async (page) => {
      await page.click('button:has-text("Upload document")');
      await page.waitForTimeout(1200);
    },
  },
  {
    slug: 'documents/document-search',
    url: '/home/documents?tab=To+Review&limit=50&skip=0',
    interact: async (page) => {
      await page.click('input[placeholder="Search"]');
      await page.fill('input[placeholder="Search"]', 'amazon');
      await page.waitForTimeout(800);
    },
  },
  {
    slug: 'documents/document-filters',
    url: '/home/documents?tab=To+Review&limit=50&skip=0',
    interact: async (page) => {
      await page.click('button:has-text("Filters")');
      await page.waitForTimeout(1000);
    },
  },
  {
    slug: 'documents/country-scope',
    url: '/home/documents?tab=To+Review&limit=50&skip=0',
    interact: async (page) => {
      // Click the country/region selector in the header
      await page.click('.ant-select-selector');
      await page.waitForTimeout(600);
    },
  },
  {
    slug: 'documents/document-status',
    url: '/home/documents?tab=To+Review&limit=50&skip=0',
    interact: async (page) => {
      // Show the status badge by hovering over the first status column cell
      const statusCell = page.locator('td').filter({ hasText: /Verifying|Publishing|Completed|Pending/ }).first();
      if (await statusCell.count()) await statusCell.hover();
      await page.waitForTimeout(500);
    },
  },
  {
    slug: 'documents/document-assign',
    url: '/home/documents?tab=To+Review&limit=50&skip=0',
    interact: async (page) => {
      // Click the first doc row eye icon to open detail, or hover assign column
      const eyeIcon = page.locator('span[aria-label="eye"]').first();
      if (await eyeIcon.count()) {
        await eyeIcon.click();
        await page.waitForTimeout(1500);
      }
    },
  },

  // ── Bank Statements ────────────────────────────────────────────────────────
  {
    slug: 'bank-statements/bank-statement-list',
    url: '/home/bank-statements',
  },
  {
    slug: 'bank-statements/bank-statement-upload',
    url: '/home/bank-statements',
    interact: async (page) => {
      await page.click('button:has-text("Upload statement")');
      await page.waitForTimeout(1200);
    },
  },
  {
    slug: 'bank-statements/bank-statement-metadata',
    url: '/home/bank-statements',
    interact: async (page) => {
      // Click first row to see statement metadata/detail
      const firstRow = page.locator('tbody tr').first();
      if (await firstRow.count()) {
        await firstRow.click();
        await page.waitForTimeout(1500);
      }
    },
  },
  {
    slug: 'bank-statements/bank-statement-filters',
    url: '/home/bank-statements',
    interact: async (page) => {
      await page.click('button:has-text("Filters")');
      await page.waitForTimeout(1000);
    },
  },
  {
    slug: 'bank-statements/bank-statement-source',
    url: '/home/bank-statements',
  },
  {
    slug: 'bank-statements/bank-statement-export-status',
    url: '/home/bank-statements',
  },
  {
    slug: 'bank-statements/bank-statement-tags',
    url: '/home/bank-statements',
  },
  {
    slug: 'bank-statements/bank-statement-review',
    url: '/home/bank-statements',
    interact: async (page) => {
      await page.click('button:has-text("Review needed")');
      await page.waitForTimeout(1000);
    },
  },
  {
    slug: 'bank-statements/bank-statement-tool',
    url: '/home/bank-statements',
  },

  // ── Suppliers ──────────────────────────────────────────────────────────────
  {
    slug: 'suppliers/supplier-list',
    url: '/home/suppliers',
  },
  {
    slug: 'suppliers/supplier-search',
    url: '/home/suppliers',
    interact: async (page) => {
      const searchInput = page.locator('input[placeholder*="Search"], input[placeholder*="search"]').first();
      if (await searchInput.count()) {
        await searchInput.click();
        await searchInput.fill('amazon');
        await page.waitForTimeout(800);
      }
    },
  },
  {
    slug: 'suppliers/supplier-rules',
    url: '/home/suppliers',
    interact: async (page) => {
      // Look for a Rules tab or button
      const rulesBtn = page.locator('text=Rules').first();
      if (await rulesBtn.count()) {
        await rulesBtn.click();
        await page.waitForTimeout(1000);
      }
    },
  },
  {
    slug: 'suppliers/supplier-detail',
    url: '/home/suppliers',
    interact: async (page) => {
      const firstRow = page.locator('tbody tr').first();
      if (await firstRow.count()) {
        await firstRow.click();
        await page.waitForTimeout(1500);
      }
    },
  },

  // ── Clients ────────────────────────────────────────────────────────────────
  {
    slug: 'clients/client-list',
    url: '/home/clients',
  },
  {
    slug: 'clients/client-search',
    url: '/home/clients',
    interact: async (page) => {
      const searchInput = page.locator('input[placeholder*="Search"], input[placeholder*="search"]').first();
      if (await searchInput.count()) {
        await searchInput.click();
        await searchInput.fill('test');
        await page.waitForTimeout(800);
      }
    },
  },
  {
    slug: 'clients/client-plan',
    url: '/home/clients',
    interact: async (page) => {
      const planBtn = page.locator('text=Plan').first();
      if (await planBtn.count()) {
        await planBtn.click();
        await page.waitForTimeout(1000);
      }
    },
  },
  {
    slug: 'clients/client-counts',
    url: '/home/clients',
  },
  {
    slug: 'clients/client-detail',
    url: '/home/clients',
    interact: async (page) => {
      const firstRow = page.locator('tbody tr').first();
      if (await firstRow.count()) {
        await firstRow.click();
        await page.waitForTimeout(1500);
      }
    },
  },
];

async function main() {
  console.log(`Launching browser...`);
  const browser = await chromium.launch({ headless: false, slowMo: 50 });

  const context = await browser.newContext({ viewport: VIEWPORT });

  // Inject all localStorage values before any page loads
  await context.addInitScript((data) => {
    for (const [key, value] of Object.entries(data)) {
      if (value !== null && value !== undefined) {
        localStorage.setItem(key, value);
      }
    }
  }, authData);

  const page = await context.newPage();
  let failed = 0;

  for (const feature of features) {
    const outputPath = join(OUTPUT_BASE, `${feature.slug}.png`);
    console.log(`\n→ ${feature.slug}`);

    try {
      await page.goto(`${BASE_URL}${feature.url}`, { waitUntil: 'load', timeout: 30000 });

      // Check for redirect to login
      const currentUrl = page.url();
      if (currentUrl.includes('/login') || currentUrl.includes('/auth0') || currentUrl.includes('auth.sleek')) {
        console.error('  ✗ Redirected to login — token may be expired');
        failed++;
        continue;
      }

      // Wait for data to fully load from API
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
