<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->
<script lang="ts">
	let { session_data = {}, step, selected_method = $bindable() } = $props();

	const set_available_methods = (step_var: number): string => {
		if (step_var === 1) {
			return session_data.step_1;
		} else if (step_var === 2) {
			return session_data.step_2;
		}
	};
	let available_methods = $derived(set_available_methods(step));

	const methods = [
		{
			id: 'PASSKEY',
			title: 'Security key',
			description: 'Authenticate using a passkey or security key',
			icon: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z'
		},
		{
			id: 'PASSWORD',
			title: 'Password',
			description: 'Authenticate using your account password',
			icon: 'M21 13V8a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h7'
		},
		{
			id: 'TOTP',
			title: 'Authenticator app',
			description: 'Authenticate using a one-time password',
			icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
		}
	];
</script>

<div class="px-6 py-6">
	<h2 class="text-center text-2xl font-semibold text-slate-900 dark:text-white">CyberAsk Quiz</h2>
	<p class="mt-2 text-center text-sm text-slate-500 dark:text-slate-400">Choose how you want to sign in.</p>

	<div class="mt-6 flex flex-col gap-3">
		{#each methods as method}
			{#if available_methods.includes(method.id)}
				<button
					type="button"
					class="flex items-center gap-4 rounded-2xl border border-slate-200/70 bg-white/80 p-4 text-left transition hover:border-brand-accent/40 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900/60 dark:hover:bg-slate-800/80"
					onclick={() => {
						selected_method = method.id;
					}}
				>
					<svg class="h-10 w-10 shrink-0 text-teal-700 dark:text-cyan-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={method.icon} />
					</svg>
					<div>
						<p class="font-semibold text-slate-900 dark:text-white">{method.title}</p>
						<p class="text-sm text-slate-500 dark:text-slate-400">{method.description}</p>
					</div>
				</button>
			{/if}
		{/each}
	</div>
</div>