import { test, expect } from '@playwright/test';

test('framework guide and player-facing entry surface load cleanly', async ({ page }) => {
	const consoleErrors: string[] = [];
	page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()); });
	await page.goto('/frameworks');
	await expect(page.getByRole('heading', { name: /Frameworks that turn scenarios into evidence/i })).toBeVisible();
	await expect(page.getByRole('link', { name: /NIST CSF/i })).toBeVisible();
	await page.getByRole('link', { name: /NCSC Cyber Assessment Framework/i }).click();
	await expect(page.getByRole('heading', { name: /NCSC Cyber Assessment Framework/i })).toBeVisible();
	await page.getByRole('link', { name: /Official source/i }).getAttribute('href');
	await page.goto('/');
	await expect(page).toHaveTitle(/CyberAsk|CyberQuiz/i);
	expect(consoleErrors).toEqual([]);
});

test.describe('live multi-user exercise', () => {
	const enabled = Boolean(process.env.E2E_GAME_PIN && process.env.E2E_GAME_ID && process.env.E2E_HOST_TOKEN && process.env.E2E_STORAGE_STATE);
	test.skip(!enabled, 'Set E2E_GAME_PIN, E2E_GAME_ID, E2E_HOST_TOKEN, and E2E_STORAGE_STATE to run against live Redis/Postgres.');

	test('facilitator and two players can join, reconnect, and see the same live state', async ({ browser, baseURL }) => {
		const admin = await browser.newContext({ storageState: process.env.E2E_STORAGE_STATE });
		const playerOne = await browser.newContext();
		const playerTwo = await browser.newContext();
		const pin = process.env.E2E_GAME_PIN!;
		const adminPage = await admin.newPage();
		await adminPage.goto(`/admin?connect=1&pin=${pin}&game_id=${process.env.E2E_GAME_ID}&token=${process.env.E2E_HOST_TOKEN}`);
		await expect(adminPage.getByText(/Facilitator|Game|Console/i).first()).toBeVisible({ timeout: 15000 });
		for (const [context, name] of [[playerOne, 'E2E Player One'], [playerTwo, 'E2E Player Two']] as const) {
			const page = await context.newPage();
			await page.goto(`/play?pin=${pin}`);
			await page.getByLabel(/game pin/i).fill(pin);
			await page.getByRole('button', { name: /Continue/i }).click();
			await page.getByLabel(/display name|username/i).fill(name);
			const avatar = page.getByRole('button', { name: /confirm|use avatar|ready/i }).first();
			if (await avatar.isVisible().catch(() => false)) await avatar.click();
			await page.getByRole('button', { name: /Join Quiz/i }).click();
			await expect(page.getByText(name)).toBeVisible({ timeout: 15000 });
		}
		const reconnecting = await playerOne.newPage();
		await reconnecting.goto(`/play?pin=${pin}`);
		await expect(reconnecting).toHaveURL(/play\?pin=/);
		await admin.close(); await playerOne.close(); await playerTwo.close();
	});
});
