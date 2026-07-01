<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import Button from '$lib/ui/Button.svelte';
	import Input from '$lib/ui/Input.svelte';
	import Spinner from '$lib/ui/Spinner.svelte';

	const { t } = getLocalization();
	let {
		session_data,
		selected_method = $bindable(),
		done = $bindable(),
		step = $bindable()
	} = $props();

	let backup_code = $state('');
	let isSubmitting = $state(false);
	let backup_code_valid = $derived(backup_code.length === 64);

	const continue_in_login = async (e: Event) => {
		e.preventDefault();
		if (!backup_code_valid) {
			return;
		}
		isSubmitting = true;
		const res = await fetch(`/api/v1/login/step/1?session_id=${session_data.session_id}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ auth_type: 'BACKUP', data: backup_code })
		});
		if (res.status === 200) {
			window.location.reload();
			done = true;
		} else {
			step += 1;
			selected_method = null;
		}
		isSubmitting = false;
	};
</script>

<div class="px-6 py-6">
	<h2 class="text-center text-2xl font-semibold text-slate-900 dark:text-white">CyberAsk Quiz</h2>
	<p class="mt-2 text-center text-sm text-slate-500 dark:text-slate-400">Enter your backup code to continue.</p>

	<form class="mt-6 space-y-4" onsubmit={continue_in_login}>
		<Input
			id="backup_code"
			bind:value={backup_code}
			placeholder={$t('login_page.backup_code')}
			ariaLabel={$t('login_page.backup_code')}
		/>
		<div class="flex items-center justify-between gap-3">
			<button
				type="button"
				class="text-sm text-slate-600 hover:text-teal-700 dark:text-slate-300 dark:hover:text-cyan-300"
				onclick={() => {
					selected_method = 'PASSWORD';
				}}
			>
				{$t('login_page.use_password')}
			</button>
			<Button type="submit" disabled={!backup_code_valid || isSubmitting}>
				{#if isSubmitting}
					<Spinner size="sm" />
				{:else}
					{$t('words.continue')}
				{/if}
			</Button>
		</div>
	</form>
</div>