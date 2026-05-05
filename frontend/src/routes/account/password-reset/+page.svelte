<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	let { data } = $props();
	let { token: string } = data;
	let isSubmitting = $state(false);
	interface PasswordData {
		password1: string;
		password2: string;
	}
	let passwordData: PasswordData = $state({
		password1: '',
		password2: ''
	});
	let passwordsValid = $derived(
		passwordData.password1 === passwordData.password2 && passwordData.password1.length >= 8
	);

	const submit = async (e: Event) => {
		e.preventDefault();
		if (!passwordsValid) {
			return;
		}
		isSubmitting = true;
		const response = await fetch('/api/v1/users/reset-password', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				password: passwordData.password1,
				token
			})
		});
		const data = await response.json();
		if (response.status === 200) {
			window.location.assign('/account/login');
		} else {
			alert(data.detail);
		}
		isSubmitting = false;
	};
</script>

<svelte:head>
	<title>CyberAsk — Set New Password</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center px-4 py-10">
	<div class="w-full max-w-sm">
		<div class="overflow-hidden rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_80px_rgba(15,23,42,0.6)]">
			<div class="px-8 pt-8 pb-6">
				<div class="mb-6 text-center">
					<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80 mb-2">CyberAsk</p>
					<h2 class="text-2xl font-semibold text-white">{$t('password_reset_page.reset_password')}</h2>
					<p class="mt-1 text-sm text-slate-400">Enter and confirm your new password.</p>
				</div>

				<form onsubmit={submit} class="flex flex-col gap-4">
					<div class="flex flex-col gap-1">
						<label for="password1" class="text-xs uppercase tracking-[0.25em] text-slate-400/70">{$t('words.password')}</label>
						<input
							id="password1"
							bind:value={passwordData.password1}
							name="password1"
							type="password"
							placeholder="••••••••"
							class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 outline-none focus:border-[#B07156]/60 transition-colors"
						/>
					</div>
					<div class="flex flex-col gap-1">
						<label for="password2" class="text-xs uppercase tracking-[0.25em] text-slate-400/70">{$t('words.repeat_password')}</label>
						<input
							id="password2"
							name="password2"
							type="password"
							bind:value={passwordData.password2}
							placeholder="••••••••"
							class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 outline-none focus:border-[#B07156]/60 transition-colors"
						/>
					</div>

					<div class="flex items-center justify-between mt-2">
						<a href="/account/login" class="text-xs text-slate-500 hover:text-slate-300 transition-colors">{$t('register_page.already_have_account?')}</a>
						<button
							type="submit"
							disabled={!passwordsValid || isSubmitting}
							class="{!passwordsValid || isSubmitting ? 'opacity-50 cursor-not-allowed' : 'hover:bg-[#c07d62]'} rounded-full bg-[#B07156] px-6 py-2.5 text-sm font-semibold text-slate-950 transition-colors flex items-center gap-2"
						>
							{#if isSubmitting}
								<svg class="h-4 w-4 animate-spin" viewBox="3 3 18 18">
									<path class="fill-slate-900" d="M12 5C8.13401 5 5 8.13401 5 12C5 15.866 8.13401 19 12 19C15.866 19 19 15.866 19 12C19 8.13401 15.866 5 12 5ZM3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12Z"/>
									<path class="fill-slate-300" d="M16.9497 7.05015C14.2161 4.31648 9.78392 4.31648 7.05025 7.05015C6.65973 7.44067 6.02656 7.44067 5.63604 7.05015C5.24551 6.65962 5.24551 6.02646 5.63604 5.63593C9.15076 2.12121 14.8492 2.12121 18.364 5.63593C18.7545 6.02646 18.7545 6.65962 18.364 7.05015C17.9734 7.44067 17.3403 7.44067 16.9497 7.05015Z"/>
								</svg>
							{:else}
								{$t('words.submit')}
							{/if}
						</button>
					</div>
				</form>
			</div>

			<div class="flex items-center justify-center gap-2 border-t border-white/8 py-4 text-center">
				<span class="text-sm text-slate-500">{$t('login_page.already_have_account')}</span>
				<a href="/account/register" class="text-sm font-semibold text-[#B07156] hover:text-[#c07d62] transition-colors">{$t('words.register')}</a>
			</div>
		</div>
	</div>
</div>
