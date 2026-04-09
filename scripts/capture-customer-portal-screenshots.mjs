#!/usr/bin/env node
/**
 * Captures screenshots of 16 customer portal accounting features from sg-app-sit.sleek.com
 * Auth is injected from ~/Downloads/sg-app-localstorage.json (exported from live session)
 *
 * Usage: node scripts/capture-customer-portal-screenshots.mjs
 */

import { chromium } from 'playwright';
import { readFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUTPUT_BASE = join(__dirname, '..', 'by-surface', 'customer-portal', 'screenshots');
// Derive auth from the coding engine export — same JWT, different key names
const CE_AUTH_FILE = join(process.env.HOME, 'Downloads', 'sleek-localstorage.json');
const BASE_URL = 'https://sg-app-sit.sleek.com';
const VIEWPORT = { width: 1400, height: 900 };

// Build the customer portal localStorage from the coding engine export
const ceAuth = JSON.parse(readFileSync(CE_AUTH_FILE, 'utf8'));
const jwt = JSON.parse(ceAuth.access_token); // strip surrounding quotes from stored value
const ceUserDetails = JSON.parse(ceAuth.sg_user_details);

const authData = {
  authToken: `Bearer ${jwt}`,
  auth_token: jwt,
  userId: ceUserDetails._id,
  companyId: ceUserDetails.last_accessed_company_id,
  email: ceUserDetails.email,
  firstName: ceUserDetails.first_name,
  lastName: ceUserDetails.last_name,
  phone: 'null',
  initializedViaLogin: 'true',
  isAdmin: 'true',
  isAccounting: 'false',
  isAccountingAdmin: 'true',
  isBookkeeping: 'false',
  isBookkeepingAdmin: 'true',
  isItSupport: 'false',
  isSleekAdmin: 'true',
  isSuperAdmin: 'false',
  isPartner: 'false',
  isPartnerAdmin: 'false',
  isEmailVerified: 'true',
  needsToPay: 'false',
  DISABLE_CUSTOMER_APP: 'false',
  microserviceEnable: 'true',
  companyStatus: 'live_post_incorporation',
  companySubStatus: 'processing_by_sleek',
  partner: 'null',
};

// Ensure output directories exist
for (const section of ['expenses', 'sales-invoices', 'bank-statements', 'files']) {
  mkdirSync(join(OUTPUT_BASE, section), { recursive: true });
}

/**
 * Feature definitions: slug → url + optional interaction before screenshot
 * interact(page) runs after the 20s wait, before screenshot
 */
const features = [
  // ── Expenses ───────────────────────────────────────────────────────────────
  {
    slug: 'expenses/expense-list',
    url: '/customer/bookkeeping/expenses',
  },
  {
    slug: 'expenses/expense-upload',
    url: '/customer/bookkeeping/expenses',
    interact: async (page) => {
      // Scroll to and hover over the upload dropzone area
      const uploadArea = page.locator('[class*="upload"], [class*="dropzone"], .v-card:has-text("Upload expenses")').first();
      if (await uploadArea.count()) await uploadArea.scrollIntoViewIfNeeded();
      await page.waitForTimeout(500);
    },
  },
  {
    slug: 'expenses/expense-submission-channels',
    url: '/customer/bookkeeping/expenses',
    interact: async (page) => {
      // Click the arrow link "More ways to submit document →"
      const btn = page.locator('a:has-text("More ways"), span:has-text("More ways"), [class*="more-ways"], p:has-text("More ways")').first();
      if (await btn.count()) {
        await btn.click();
        await page.waitForTimeout(1200);
      }
    },
  },
  {
    slug: 'expenses/expense-document-viewer',
    url: '/customer/bookkeeping/expenses',
    interact: async (page) => {
      // Click eye icon on the first expense row
      const eyeIcon = page.locator('span[aria-label="eye"], svg[data-icon="eye"], button:has(svg)').first();
      // Try clicking the first row's view button by looking for the eye-shaped button
      const viewBtns = page.locator('[class*="eye"], [title*="view"], [title*="View"]');
      if (await viewBtns.count()) {
        await viewBtns.first().click();
        await page.waitForTimeout(2000);
      }
    },
  },
  {
    slug: 'expenses/expense-search',
    url: '/customer/bookkeeping/expenses',
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
    slug: 'expenses/expense-user-filter',
    url: '/customer/bookkeeping/expenses',
    interact: async (page) => {
      // Click one of the user avatar filter chips (not "All")
      const chip = page.locator('.v-chip:not(:has-text("All")), [class*="chip"]:not(:has-text("All"))').first();
      if (await chip.count()) {
        await chip.click();
        await page.waitForTimeout(800);
      }
    },
  },
  {
    slug: 'expenses/expense-archived',
    url: '/customer/bookkeeping/expenses',
    interact: async (page) => {
      const archivedBtn = page.locator('text=Archived expenses').first();
      if (await archivedBtn.count()) {
        await archivedBtn.click();
        await page.waitForTimeout(1500);
      }
    },
  },

  // ── Sales Invoices ─────────────────────────────────────────────────────────
  {
    slug: 'sales-invoices/invoice-list',
    url: '/customer/bookkeeping/sales-invoices',
  },
  {
    slug: 'sales-invoices/invoice-create',
    url: '/customer/bookkeeping/sales-invoices',
    interact: async (page) => {
      const btn = page.locator('text=NEW SALES INVOICE, text=New Sales Invoice').first();
      if (await btn.count()) {
        await btn.click();
        await page.waitForTimeout(2000);
      }
    },
  },
  {
    slug: 'sales-invoices/invoice-submission-channels',
    url: '/customer/bookkeeping/sales-invoices',
    interact: async (page) => {
      const btn = page.locator('a:has-text("More ways"), span:has-text("More ways"), p:has-text("More ways")').first();
      if (await btn.count()) {
        await btn.click();
        await page.waitForTimeout(1200);
      }
    },
  },
  {
    slug: 'sales-invoices/invoice-archived',
    url: '/customer/bookkeeping/sales-invoices',
    interact: async (page) => {
      const archivedBtn = page.locator('text=Archived sales invoices').first();
      if (await archivedBtn.count()) {
        await archivedBtn.click();
        await page.waitForTimeout(1500);
      }
    },
  },

  // ── Bank Statements ────────────────────────────────────────────────────────
  {
    slug: 'bank-statements/statement-overview',
    url: '/customer/bookkeeping/statements',
  },
  {
    slug: 'bank-statements/statement-month-status',
    url: '/customer/bookkeeping/statements',
    interact: async (page) => {
      // Scroll to the month status grid section
      const statusSection = page.locator('text=Statements upload status').first();
      if (await statusSection.count()) await statusSection.scrollIntoViewIfNeeded();
      await page.waitForTimeout(500);
    },
  },
  {
    slug: 'bank-statements/statement-bank-filter',
    url: '/customer/bookkeeping/statements',
    interact: async (page) => {
      // Click a specific bank filter chip (e.g. "Wise")
      const wiseChip = page.locator('text=Wise').first();
      if (await wiseChip.count()) {
        await wiseChip.click();
        await page.waitForTimeout(800);
      }
    },
  },
  {
    slug: 'bank-statements/statement-upload',
    url: '/customer/bookkeeping/statements',
    interact: async (page) => {
      // Scroll to the missing statements section to show Upload buttons
      const missingSection = page.locator('text=Missing statements').first();
      if (await missingSection.count()) await missingSection.scrollIntoViewIfNeeded();
      await page.waitForTimeout(800);
    },
  },

  // ── Files ──────────────────────────────────────────────────────────────────
  {
    slug: 'files/files-list',
    url: '/customer/bookkeeping/files',
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

      // Check for redirect to login/auth
      const currentUrl = page.url();
      if (currentUrl.includes('/auth') || currentUrl.includes('auth0') || currentUrl.includes('/login')) {
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
