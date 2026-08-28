import { test, expect } from '@playwright/test';

test.describe('Chat page', () => {
  test('shows the empty-state invitation on load', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'Ask ComptaRAG' })).toBeVisible();
  });

  test('asks a question and displays the categorized answer', async ({ page }) => {
    await page.route('**/chat/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Under IAS 37, a provision is recognized when three conditions are met.',
          category: 'IFRS'
        })
      });
    });

    await page.goto('/');

    await page.getByLabel('Ask a question').fill('When is a provision recognized under IFRS?');
    await page.getByRole('button', { name: 'Ask' }).click();

    await expect(page.getByText('When is a provision recognized under IFRS?')).toBeVisible();
    await expect(
      page.getByText('Under IAS 37, a provision is recognized when three conditions are met.')
    ).toBeVisible();
    await expect(page.getByText('IFRS')).toBeVisible();
  });

  test('shows an error message when the backend request fails', async ({ page }) => {
    await page.route('**/chat/', async (route) => {
      await route.fulfill({ status: 500, contentType: 'application/json', body: '{}' });
    });

    await page.goto('/');

    await page.getByLabel('Ask a question').fill('This will fail');
    await page.getByRole('button', { name: 'Ask' }).click();

    await expect(page.getByRole('alert')).toContainText(/something went wrong/i);
  });
});
