<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import Button from '$lib/ui/Button.svelte';
	import Input from '$lib/ui/Input.svelte';
	import Spinner from '$lib/ui/Spinner.svelte';

	interface Props {
		session_data: any;
		selected_method: any;
		done: any;
		step: any;
	}

	let {
		session_data,
		selected_method = $bindable(),
		done = $bindable(),
		step = $bindable()
	}: Props = $props();

	const { t } = getLocalization();
	let isSubmitting = $state(false);
	let totp = $state('');

	let totp_valid = $derived(totp.length === 6);

	const continue_in_login = async (e: Event) => {
		e.preventDefault();
		if (!totp_valid) {
			return;
		}
		isSubmitting = true;
		const res = await fetch(
			`/api/v1/login/step/${step}?session_id=${session_data.session_id}`,
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ auth_type: 'TOTP', data: totp })
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
			if (data.detail === 'totp wrong') {
				alert('TOTP code was incorrect');
				totp = '';
			}
		}
		isSubmitting = false;
	};
</script>

<div class="px-6 py-6">
	<h2 class="text-center text-sm font-semibold uppercase tracking-[0.32em] text-teal-700 dark:text-cyan-300">
		CyberAsk Admin
	</h2>
	<h3 class="mt-2 text-center text-xl font-semibold text-slate-900 dark:text-white">Authenticator app</h3>
	<p class="mt-2 text-center text-sm text-slate-500 dark:text-slate-400">
		Enter the 6-digit code from your authenticator app.
	</p>

	<form class="mt-6 space-y-4" onsubmit={continue_in_login}>
		<Input
			id="totp"
			bind:value={totp}
			maxlength={6}
			placeholder={$t('words.totp')}
			ariaLabel={$t('words.totp')}
			autocomplete="one-time-code"
			class="text-center text-lg tracking-[0.3em]"
		/>
		<div class="flex items-center justify-between gap-3">
			<button
				type="button"
				class="text-sm text-slate-600 hover:text-teal-700 dark:text-slate-300 dark:hover:text-cyan-300"
				onclick={() => {
					selected_method = 'BACKUP';
				}}
			>
				{$t('login_page.use_backup_code')}
			</button>
			<Button type="submit" disabled={!totp_valid || isSubmitting}>
				{#if isSubmitting}
					<Spinner size="sm" />
				{:else}
					{$t('words.continue')}
				{/if}
			</Button>
		</div>
	</form>
</div>