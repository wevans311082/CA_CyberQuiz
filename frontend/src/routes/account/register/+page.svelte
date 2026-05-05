<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { createForm } from 'felte';
	import { getLocalization } from '$lib/i18n';
	import { validateSchema } from '@felte/validator-yup';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import Footer from '$lib/footer.svelte';

	const { t } = getLocalization();
	import reporter from '@felte/reporter-tippy';

	navbarVisible.visible = true;
	import * as yup from 'yup';

	const registerSchema = yup.object({
		email: yup.string().email('Email must be valid!').required(),
		password1: yup
			.string()
			.required()
			.min(8, 'Password must be at least 8 characters long!')
			.max(100, 'Password must be at most 100 characters long!'),
		password2: yup
			.string()
			.required()
			.test('equal', 'Passwords do not match!', function (v) {
				const ref = yup.ref('password1');
				return v === this.resolve(ref);
			}),
		username: yup
			.string()
			.required()
			.min(3, 'Username must be at least 3 characters long')
			.max(20, 'Username must be at most 20 characters long'),
		privacy_accept: yup
			.boolean()
			.oneOf([true], 'You must accept the privacy policy to register!'),
		tos_accept: yup.boolean().oneOf([true], 'You must accept the terms of service to register!')
	});

	const { form, errors, touched, isValid, isSubmitting } = createForm<
		yup.InferType<typeof registerSchema>
	>({
		validate: validateSchema(registerSchema),
		extend: [reporter()],
		onSubmit: async (values) => {
			const res = await fetch('/api/v1/users/create', {
				method: 'post',
				body: JSON.stringify({
					email: values.email,
					password: values.password1,
					username: values.username
				}),
				headers: {
					'Content-Type': 'application/json'
				}
			});
			if (res.status === 200) {
				responseData.data = '200';
			} else if (res.status === 409) {
				responseData.data = '409';
			} else if (res.status === 400) {
				responseData.data = '400';
			} else {
				responseData.data = 'error';
			}
			responseData.open = true;
		}
	});
	let responseData = $state({
		open: false,
		data: ''
	});
</script>

<svelte:head>
	<title>CyberAsk — Register</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center px-4 py-10">
	<div class="w-full max-w-sm">
		<div class="overflow-hidden rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_80px_rgba(15,23,42,0.6)]">
			<div class="px-8 pt-8 pb-6">
				<div class="mb-6 text-center">
					<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80 mb-2">CyberAsk</p>
					<h2 class="text-2xl font-semibold text-white">{$t('register_page.greeting')}</h2>
					<p class="mt-1 text-sm text-slate-400">{$t('register_page.create_account')}</p>
				</div>

				<form use:form class="flex flex-col gap-4">
					<!-- Email -->
					<div class="flex flex-col gap-1">
						<label for="email" class="text-xs uppercase tracking-[0.25em] text-slate-400/70">{$t('words.email')}</label>
						<input
							id="email"
							name="email"
							type="email"
							placeholder="you@example.com"
							class="{$errors.email !== null ? 'border-red-500/60' : ($touched.email && $errors.email === null ? 'border-emerald-500/60' : 'border-white/10')} w-full rounded-xl border bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 outline-none focus:border-[#B07156]/60 transition-colors"
						/>
					</div>

					<!-- Username -->
					<div class="flex flex-col gap-1">
						<label for="username" class="text-xs uppercase tracking-[0.25em] text-slate-400/70">{$t('words.username')}</label>
						<input
							id="username"
							name="username"
							type="text"
							placeholder="your_username"
							class="{$errors.username !== null ? 'border-red-500/60' : ($touched.username && $errors.username === null ? 'border-emerald-500/60' : 'border-white/10')} w-full rounded-xl border bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 outline-none focus:border-[#B07156]/60 transition-colors"
						/>
					</div>

					<!-- Password -->
					<div class="flex flex-col gap-1">
						<label for="password1" class="text-xs uppercase tracking-[0.25em] text-slate-400/70">{$t('words.password')}</label>
						<input
							id="password1"
							name="password1"
							type="password"
							placeholder="••••••••"
							class="{$errors.password1 !== null ? 'border-red-500/60' : ($touched.password1 && $errors.password1 === null ? 'border-emerald-500/60' : 'border-white/10')} w-full rounded-xl border bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 outline-none focus:border-[#B07156]/60 transition-colors"
						/>
					</div>

					<!-- Confirm Password -->
					<div class="flex flex-col gap-1">
						<label for="password2" class="text-xs uppercase tracking-[0.25em] text-slate-400/70">Confirm Password</label>
						<input
							id="password2"
							name="password2"
							type="password"
							placeholder="••••••••"
							class="{$errors.password2 !== null ? 'border-red-500/60' : ($touched.password2 && $errors.password2 === null ? 'border-emerald-500/60' : 'border-white/10')} w-full rounded-xl border bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 outline-none focus:border-[#B07156]/60 transition-colors"
						/>
					</div>

					<!-- Privacy / ToS -->
					<div class="flex flex-col gap-2 mt-1">
						<label class="flex items-start gap-3 cursor-pointer">
							<input type="checkbox" name="privacy_accept" class="mt-0.5 accent-[#B07156]" />
							<span class="text-xs text-slate-400">I've read the <a href="/docs/privacy-policy" class="text-[#B07156] underline hover:text-[#c07d62]">Privacy Policy</a>.</span>
						</label>
						<label class="flex items-start gap-3 cursor-pointer">
							<input type="checkbox" name="tos_accept" class="mt-0.5 accent-[#B07156]" />
							<span class="text-xs text-slate-400">I agree to the <a href="/docs/tos" class="text-[#B07156] underline hover:text-[#c07d62]">Terms of Service</a>.</span>
						</label>
					</div>

					<div class="flex items-center justify-between mt-2">
						<a href="/account/reset-password" class="text-xs text-slate-500 hover:text-slate-300 transition-colors">{$t('register_page.forgot_password?')}</a>
						<button
							type="submit"
							disabled={!$isValid || $isSubmitting}
							class="{!$isValid || $isSubmitting ? 'opacity-50 cursor-not-allowed' : 'hover:bg-[#c07d62]'} rounded-full bg-[#B07156] px-6 py-2.5 text-sm font-semibold text-slate-950 transition-colors flex items-center gap-2"
						>
							{#if $isSubmitting}
								<svg class="h-4 w-4 animate-spin" viewBox="3 3 18 18">
									<path class="fill-slate-900" d="M12 5C8.13401 5 5 8.13401 5 12C5 15.866 8.13401 19 12 19C15.866 19 19 15.866 19 12C19 8.13401 15.866 5 12 5ZM3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12Z"/>
									<path class="fill-slate-300" d="M16.9497 7.05015C14.2161 4.31648 9.78392 4.31648 7.05025 7.05015C6.65973 7.44067 6.02656 7.44067 5.63604 7.05015C5.24551 6.65962 5.24551 6.02646 5.63604 5.63593C9.15076 2.12121 14.8492 2.12121 18.364 5.63593C18.7545 6.02646 18.7545 6.65962 18.364 7.05015C17.9734 7.44067 17.3403 7.44067 16.9497 7.05015Z"/>
								</svg>
							{:else}
								{$t('words.register')}
							{/if}
						</button>
					</div>
				</form>
			</div>

			<div class="flex items-center justify-center gap-2 border-t border-white/8 py-4 text-center">
				<span class="text-sm text-slate-500">{$t('register_page.already_have_account?')}</span>
				<a href="/account/login" class="text-sm font-semibold text-[#B07156] hover:text-[#c07d62] transition-colors">{$t('words.login')}</a>
			</div>
		</div>
	</div>
</div>
<Footer />

<!-- Response modal -->
<div
	class="fixed z-10 inset-0 flex items-center justify-center bg-black/70"
	role="dialog"
	aria-modal="true"
	aria-labelledby="register-modal-title"
	class:hidden={!responseData.open}
>
	<div class="w-full max-w-md mx-4 rounded-[2rem] border border-white/15 bg-[#0f172a]/97 backdrop-blur-2xl shadow-[0_30px_120px_rgba(15,23,42,0.8)] p-8 text-white">
		<div class="flex items-start gap-4 mb-6">
			<div class="{responseData.data === '200' ? 'bg-emerald-500/15 border-emerald-500/30' : 'bg-red-500/15 border-red-500/30'} shrink-0 flex items-center justify-center w-10 h-10 rounded-full border">
				{#if responseData.data === '200'}
					<svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				{:else}
					<svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
					</svg>
				{/if}
			</div>
			<div>
				<h3 class="text-base font-semibold text-white" id="register-modal-title">
					{#if responseData.data === '409'}Account already exists!
					{:else if responseData.data === 'error'}Unexpected error!
					{:else if responseData.data === '200'}Registration successful!
					{:else if responseData.data === '400'}Invalid email address!
					{/if}
				</h3>
				<p class="mt-1 text-sm text-slate-400">
					{#if responseData.data === '200'}Please check your mailbox to confirm your email address.
					{:else if responseData.data === '409'}An account with that email already exists.
					{:else if responseData.data === '400'}That email address doesn't appear to exist.
					{:else if responseData.data === 'error'}An unexpected error occurred. Please try again.
					{/if}
				</p>
			</div>
		</div>
		<div class="flex justify-end">
			<button
				type="button"
				onclick={() => { responseData.open = false; window.location.assign('/'); }}
				class="rounded-full bg-[#B07156] px-6 py-2.5 text-sm font-semibold text-slate-950 hover:bg-[#c07d62] transition-colors"
			>{$t('words.close')}</button>
		</div>
	</div>
</div>
