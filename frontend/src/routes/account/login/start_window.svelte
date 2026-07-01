<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import Button from '$lib/ui/Button.svelte';
	import Input from '$lib/ui/Input.svelte';
	import Spinner from '$lib/ui/Spinner.svelte';

	let { session_data = $bindable({}), step = $bindable() } = $props();

	const { t } = getLocalization();
	let email = $state('');
	let emailEmpty = $derived(email === '');
	let isSubmitting = $state(false);

	const start_login = async (e: Event): Promise<void> => {
		e.preventDefault();
		if (emailEmpty) {
			return;
		}
		isSubmitting = true;

		const res = await fetch('/api/v1/login/start', {
			method: 'post',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ email: email })
		});
		session_data = await res.json();
		step = 1;
		isSubmitting = false;
	};
</script>

<div class="px-6 py-6">
	<h2 class="text-center text-sm font-semibold uppercase tracking-[0.32em] text-teal-700 dark:text-cyan-300">
		CyberAsk Admin
	</h2>
	<h3 class="mt-2 text-center text-xl font-semibold text-slate-900 dark:text-white">Admin sign-in</h3>
	<p class="mt-2 text-center text-sm text-slate-500 dark:text-slate-400">
		Use your administrator email or username to continue.
	</p>

	<form class="mt-6 space-y-4" onsubmit={start_login}>
		<Input
			id="email"
			bind:value={email}
			placeholder={$t('login_page.email_or_username')}
			ariaLabel={$t('login_page.email_or_username')}
			autocomplete="email"
		/>
		<div class="flex items-center justify-between gap-3">
			<a
				href="/account/reset-password"
				class="text-sm text-slate-600 hover:text-teal-700 dark:text-slate-300 dark:hover:text-cyan-300"
			>
				{$t('register_page.forgot_password?')}
			</a>
			<Button type="submit" disabled={emailEmpty || isSubmitting}>
				{#if isSubmitting}
					<Spinner size="sm" />
				{:else}
					{$t('words.continue')}
				{/if}
			</Button>
		</div>
	</form>
</div>

<div class="border-t border-slate-700/50 px-6 py-4 text-center text-sm text-slate-400">
	Authorised administrators only.
</div>