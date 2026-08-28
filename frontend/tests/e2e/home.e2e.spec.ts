import { test, expect } from '@playwright/test';

test.describe('Home page', () => {
  test('loads and displays the welcome heading', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
  });

  test('increments the counter on click', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByText('Count: 0')).toBeVisible();
    await page.getByRole('button', { name: 'Increment' }).click();
    await expect(page.getByText('Count: 1')).toBeVisible();
  });
});
