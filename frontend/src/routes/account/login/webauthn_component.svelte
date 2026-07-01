<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { startAuthentication } from '@simplewebauthn/browser';
	import { getLocalization } from '$lib/i18n';
	import Button from '$lib/ui/Button.svelte';
	import Spinner from '$lib/ui/Spinner.svelte';

	const { t } = getLocalization();
	let {
		session_data,
		selected_method = $bindable(),
		done = $bindable(),
		step = $bindable()
	} = $props();

	let isLoading = $state(false);

	const start_thing = async () => {
		const data = JSON.parse(session_data.webauthn_data);
		let asseResp;
		isLoading = true;
		try {
			asseResp = await startAuthentication({ optionsJSON: data });
		} catch (e) {
			console.error(e);
			alert('Unknown error');
			isLoading = false;
		}
		const res = await fetch(
			`/api/v1/login/step/${step}?session_id=${session_data.session_id}`,
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ auth_type: 'PASSKEY', data: asseResp })
			}
		);
		if (res.status === 200) {
			window.location.reload();
			done = true;
		} else if (res.status === 202) {
			step += 1;
			selected_method = null;
		} else if (res.status === 401) {
			let data;
			try {
				data = await res.json();
			} catch {
				alert('Unknown error');
				window.location.reload();
			}
			if (data.detail === 'webauthn failed') {
				alert('Webauthn failed');
			}
		}
		isLoading = false;
	};
</script>

<div class="px-6 py-6">
	<h2 class="text-center text-sm font-semibold uppercase tracking-[0.32em] text-teal-700 dark:text-cyan-300">
		CyberAsk Admin
	</h2>
	<h3 class="mt-2 text-center text-xl font-semibold text-slate-900 dark:text-white">Security key</h3>
	<p class="mt-2 text-center text-sm text-slate-500 dark:text-slate-400">
		Use your passkey or security key to verify your identity.
	</p>

	<div class="mt-6 flex items-center justify-between gap-3">
		<button
			type="button"
			class="text-sm text-slate-600 hover:text-teal-700 dark:text-slate-300 dark:hover:text-cyan-300"
			onclick={() => {
				selected_method = 'BACKUP';
			}}
		>
			{$t('login_page.use_backup_code')}
		</button>
		<Button disabled={isLoading} onclick={start_thing}>
			{#if isLoading}
				<Spinner size="sm" />
			{:else}
				{$t('words.start')}
			{/if}
		</Button>
	</div>
</div>