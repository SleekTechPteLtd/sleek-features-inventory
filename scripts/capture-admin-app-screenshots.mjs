#!/usr/bin/env node
/**
 * Captures screenshots of 17 admin app accounting features from admin-sit.sleek.sg
 * Auth is injected from ~/Downloads/admin-app-localstorage.json (exported from live session)
 *
 * Usage: node scripts/capture-admin-app-screenshots.mjs
 */

import { chromium } from 'playwright';
import { readFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUTPUT_BASE = join(__dirname, '..', 'by-surface', 'admin-app', 'screenshots');
const AUTH_FILE = join(process.env.HOME, 'Downloads', 'admin-app-localstorage.json');
const BASE_URL = 'https://admin-sit.sleek.sg';
const CID = '6768ce4b939e53003e993169';
const VIEWPORT = { width: 1400, height: 900 };

// Load session auth from downloaded localStorage export
const authData = JSON.parse(readFileSync(AUTH_FILE, 'utf8'));

// Ensure output directories exist
for (const section of ['company', 'workflows', 'users', 'tools']) {
  mkdirSync(join(OUTPUT_BASE, section), { recursive: true });
}

const features = [
  // ── Company Management ─────────────────────────────────────────────────────
  {
    slug: 'company/company-list',
    url: '/admin/companies/',
  },
  {
    slug: 'company/company-overview',
    url: `/admin/company-overview/?cid=${CID}`,
  },
  {
    slug: 'company/company-accounting',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Accounting`,
  },
  {
    slug: 'company/company-billing-subscriptions',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Billing+Beta`,
  },
  {
    slug: 'company/company-billing-invoices',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Billing+Beta`,
    interact: async (page) => {
      const tab = page.locator('text=INVOICES & CREDIT NOTE').first();
      if (await tab.count()) {
        await tab.click();
        await page.waitForTimeout(1500);
      }
    },
  },
  {
    slug: 'company/company-billing-payment-request',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Billing+Beta`,
    interact: async (page) => {
      const btn = page.locator('text=PAYMENT REQUEST, button:has-text("Payment Request")').first();
      if (await btn.count()) {
        await btn.click();
        await page.waitForTimeout(1500);
      }
    },
  },
  {
    slug: 'company/company-deadlines',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Deadlines`,
  },

  // ── Workflows & Requests ───────────────────────────────────────────────────
  {
    slug: 'workflows/workflow-list',
    url: '/admin/new-workflow/',
  },
  {
    slug: 'workflows/camunda-workflows',
    url: '/admin/sleek-workflow/',
  },
  {
    slug: 'workflows/requests-list',
    url: '/admin/requests/',
  },
  {
    slug: 'workflows/request-detail',
    url: '/admin/requests/',
    interact: async (page) => {
      // Hover over the first row to highlight it — avoid clicking Edit (may trigger dialog)
      const firstRow = page.locator('table tbody tr, [class*="row"]').first();
      if (await firstRow.count()) await firstRow.hover();
      await page.waitForTimeout(500);
    },
  },

  // ── Users & KYC ───────────────────────────────────────────────────────────
  {
    slug: 'users/user-list',
    url: '/admin/user-management/',
  },
  {
    slug: 'users/user-detail',
    url: '/admin/user-management/',
    interact: async (page) => {
      // Navigate directly via the EDIT link href (avoids dialog risk)
      const editLink = page.locator('a:has-text("EDIT"), a[href*="user"]').first();
      if (await editLink.count()) {
        const href = await editLink.getAttribute('href');
        if (href) {
          await page.goto(`https://admin-sit.sleek.sg${href}`, { waitUntil: 'load', timeout: 30000 });
          await page.waitForTimeout(5000);
        }
      }
    },
  },
  {
    slug: 'users/user-kyc',
    url: '/admin/user-management/',
    interact: async (page) => {
      // Navigate to user detail, then scroll to KYC section
      const editLink = page.locator('a:has-text("EDIT"), a[href*="user"]').first();
      if (await editLink.count()) {
        const href = await editLink.getAttribute('href');
        if (href) {
          await page.goto(`https://admin-sit.sleek.sg${href}`, { waitUntil: 'load', timeout: 30000 });
          await page.waitForTimeout(5000);
          const kycSection = page.locator('text=KYC').first();
          if (await kycSection.count()) await kycSection.scrollIntoViewIfNeeded();
          await page.waitForTimeout(500);
        }
      }
    },
  },

  // ── Admin Tools ────────────────────────────────────────────────────────────
  {
    slug: 'tools/audit-logs',
    url: '/admin/audit-logs/',
  },
  {
    slug: 'tools/document-templates',
    url: '/admin/documents/',
  },
  {
    slug: 'tools/request-templates',
    url: '/admin/request-templates/',
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
      if (currentUrl.includes('/login') || currentUrl.includes('/auth') || currentUrl.includes('auth0')) {
        console.error('  ✗ Redirected to login — token may be expired');
        failed++;
        continue;
      }

      // Wait for data to fully load
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
