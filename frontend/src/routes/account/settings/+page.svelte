<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import { DateTime } from 'luxon';
	import { UAParser } from 'ua-parser-js';
	import Spinner from '$lib/Spinner.svelte';
	import { onMount } from 'svelte';
	import BrownButton from '$lib/components/buttons/brown.svelte';

	const { t } = getLocalization();

	interface UserAccount {
		id: string;
		email: string;
		username: string;
		verified: boolean;
		created_at: string;
	}

	interface ChangePasswordData {
		oldPassword: string;
		newPassword: string;
		newPasswordConfirm: string;
	}

	let changePasswordData: ChangePasswordData = $state({
		oldPassword: '',
		newPassword: '',
		newPasswordConfirm: ''
	});

	let locationData;
	let this_session = $state();

	let passwordChangeDataValid = $derived(
		changePasswordData.newPassword === changePasswordData.newPasswordConfirm &&
			changePasswordData.newPassword.length >= 8 &&
			changePasswordData.oldPassword !== changePasswordData.newPassword &&
			changePasswordData.oldPassword !== ''
	);

	const changePassword = async (e: Event) => {
		e.preventDefault();
		if (!passwordChangeDataValid) {
			return;
		}
		const res = await fetch('/api/v1/users/password/update', {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				old_password: changePasswordData.oldPassword,
				new_password: changePasswordData.newPassword
			})
		});
		if (res.status === 200) {
			alert('Password changed');
			window.location.assign('/account/login');
		} else {
			alert('Password change failed');
		}
	};

	const getUser = async (): Promise<UserAccount> => {
		const response = await fetch('/api/v1/users/me', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		if (response.status === 200) {
			return await response.json();
		} else {
			window.location.assign('/account/login');
		}
	};

	onMount(() => {
		api_keys = get_api_keys();
	});

	const get_api_keys = async (): Promise<Array<string>> => {
		const res = await fetch('/api/v1/users/api_keys');
		const api_keys_temp = await res.json();
		console.log(api_keys_temp);
		return api_keys_temp;
	};

	let api_keys = $state();

	const add_api_key = async () => {
		await fetch('/api/v1/users/api_keys', { method: 'POST' });
		api_keys = get_api_keys();
	};
	const formatDate = (date: string): string => {
		const dt = DateTime.fromISO(date);
		return dt.toLocaleString(DateTime.DATETIME_MED);
	};

	const delete_api_key = async (key: string) => {
		if (confirm('Do you really want to delete this API-Key?')) {
			await fetch(`/api/v1/users/api_keys?api_key=${key}`, { method: 'DELETE' });
			api_keys = get_api_keys();
		}
	};

	const getSessions = async () => {
		const res = await fetch('/api/v1/users/sessions/list');
		if (res.status === 200) {
			const res2 = await fetch('/api/v1/users/session');
			if (res2.status === 200) {
				this_session = await res2.json();
			}
			return await res.json();
		} else {
			window.location.assign('/account/login?returnTo=/account/settings');
		}
		return await res.json();
	};

	const getFormattedUserAgent = (userAgent: string): string => {
		const parser = new UAParser(userAgent);
		const result = parser.getResult();
		return `${result.browser.name} ${result.browser.version} (${result.os.name})`;
	};

	const deleteSession = async (session_id: string) => {
		const res = await fetch(`/api/v1/users/sessions/${session_id}`, {
			method: 'DELETE'
		});
		if (res.status === 200) {
			window.location.reload();
		}
	};
</script>

<svelte:head>
	<title>CyberAsk — Settings</title>
</svelte:head>

{#await getUser()}
	<Spinner />
{:then user}
	<div class="min-h-screen text-white px-4 py-8 max-w-4xl mx-auto flex flex-col gap-8">

		<!-- Profile card -->
		<div class="rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_80px_rgba(15,23,42,0.6)] p-6 flex flex-col sm:flex-row gap-6 items-start">
			<div class="flex flex-col items-center gap-3 shrink-0">
				<img class="rounded-2xl w-24 h-24 object-cover border border-white/15" src="/api/v1/users/avatar" alt="Profile image of {user.username}" />
				<a href="/account/settings/avatar" class="rounded-full border border-white/15 px-4 py-1.5 text-xs font-semibold text-white/90 hover:bg-white/6 transition-colors">
					{$t('settings_page.change_avatar')}
				</a>
			</div>
			<div class="flex-1 flex flex-col gap-4">
				<div>
					<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80 mb-1">Account</p>
					<h1 class="text-2xl font-semibold text-white">{user.username}</h1>
					<p class="text-sm text-slate-400 mt-0.5">{user.email}</p>
				</div>
				<div class="flex flex-wrap gap-2">
					<a href="/account/settings/security" class="rounded-full border border-white/15 px-4 py-2 text-xs font-semibold text-white/90 hover:bg-white/6 transition-colors">
						{$t('settings_page.security_settings')}
					</a>
					<a href="/account/controllers" class="rounded-full border border-white/15 px-4 py-2 text-xs font-semibold text-white/90 hover:bg-white/6 transition-colors">
						Controller
					</a>
					<a href="/user/{user.id}" class="rounded-full border border-white/15 px-4 py-2 text-xs font-semibold text-white/90 hover:bg-white/6 transition-colors">
						Public profile
					</a>
				</div>
			</div>
		</div>

		<!-- Change password card -->
		<div class="rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_80px_rgba(15,23,42,0.6)] p-6 flex flex-col gap-5">
			<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80">{$t('settings_page.change_password_submit')}</p>
			<form class="flex flex-col sm:flex-row gap-4 flex-wrap" onsubmit={changePassword}>
				<div class="flex flex-col gap-1 flex-1 min-w-[160px]">
					<label class="text-xs uppercase tracking-[0.25em] text-slate-400/70">{$t('settings_page.old_password')}</label>
					<input type="password" class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 outline-none focus:border-[#B07156]/60 transition-colors" bind:value={changePasswordData.oldPassword} />
				</div>
				<div class="flex flex-col gap-1 flex-1 min-w-[160px]">
					<label class="text-xs uppercase tracking-[0.25em] text-slate-400/70">{$t('settings_page.new_password')}</label>
					<input type="password" class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 outline-none focus:border-[#B07156]/60 transition-colors" bind:value={changePasswordData.newPassword} />
				</div>
				<div class="flex flex-col gap-1 flex-1 min-w-[160px]">
					<label class="text-xs uppercase tracking-[0.25em] text-slate-400/70">{$t('settings_page.repeat_password')}</label>
					<input type="password" class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 outline-none focus:border-[#B07156]/60 transition-colors" bind:value={changePasswordData.newPasswordConfirm} />
				</div>
				<div class="flex items-end">
					<button type="submit" disabled={!passwordChangeDataValid} class="{passwordChangeDataValid ? 'bg-[#B07156] hover:bg-[#c07d62] text-slate-950' : 'bg-white/10 text-slate-500 cursor-not-allowed'} rounded-full px-6 py-2.5 text-sm font-semibold transition-colors">
						{$t('settings_page.change_password_submit')}
					</button>
				</div>
			</form>
		</div>

		<!-- API Keys card -->
		<div class="rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_80px_rgba(15,23,42,0.6)] p-6 flex flex-col gap-5">
			<div class="flex items-center justify-between">
				<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80">{$t('settings_page.add_api_key')}</p>
				<button onclick={add_api_key} class="rounded-full bg-[#B07156] px-5 py-2 text-xs font-semibold text-slate-950 hover:bg-[#c07d62] transition-colors">
					+ {$t('settings_page.add_api_key')}
				</button>
			</div>
			{#await api_keys}
				<Spinner />
			{:then keys}
				{#if keys && keys.length > 0}
					<div class="flex flex-col gap-2">
						{#each keys as key}
							<div class="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
								<span class="font-mono text-xs truncate flex-1 mr-4">{key.key}</span>
								<button onclick={() => delete_api_key(key.key)} class="rounded-full border border-red-500/40 px-3 py-1 text-xs font-semibold text-red-400 hover:bg-red-500/10 transition-colors">
									{$t('words.delete')}
								</button>
							</div>
						{/each}
					</div>
				{:else}
					<p class="text-sm text-slate-500">No API keys yet.</p>
				{/if}
			{/await}
		</div>

		<!-- Sessions card -->
		<div class="rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_80px_rgba(15,23,42,0.6)] p-6 flex flex-col gap-5">
			<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80">Active Sessions</p>
			{#await getSessions()}
				<Spinner />
			{:then sessions}
				<div class="overflow-x-auto">
					<table class="w-full text-sm">
						<thead>
							<tr class="border-b border-white/8">
								<th class="py-2 px-3 text-left text-xs uppercase tracking-[0.25em] text-slate-400/70 font-normal">{$t('overview_page.created_at')}</th>
								<th class="py-2 px-3 text-left text-xs uppercase tracking-[0.25em] text-slate-400/70 font-normal">{$t('settings_page.last_seen')}</th>
								<th class="py-2 px-3 text-left text-xs uppercase tracking-[0.25em] text-slate-400/70 font-normal">{$t('words.browser')}</th>
								<th class="py-2 px-3 text-left text-xs uppercase tracking-[0.25em] text-slate-400/70 font-normal">{$t('settings_page.this_session?')}</th>
								<th class="py-2 px-3"></th>
							</tr>
						</thead>
						<tbody>
							{#each sessions as session}
								<tr class="border-b border-white/5 hover:bg-white/3 transition-colors">
									<td class="py-3 px-3 text-slate-400 whitespace-nowrap">{formatDate(session.created_at)}</td>
									<td class="py-3 px-3 text-slate-400 whitespace-nowrap">{formatDate(session.last_seen)}</td>
									<td class="py-3 px-3 text-slate-300 whitespace-nowrap">{getFormattedUserAgent(session.user_agent)}</td>
									<td class="py-3 px-3 text-center">
										{#if session.id === this_session?.id}
											<span class="text-emerald-400 text-xs font-semibold">Current</span>
										{:else}
											<span class="text-slate-600 text-xs">—</span>
										{/if}
									</td>
									<td class="py-3 px-3">
										<button onclick={() => deleteSession(session.id)} class="rounded-full border border-red-500/40 px-3 py-1 text-xs font-semibold text-red-400 hover:bg-red-500/10 transition-colors">
											{$t('words.delete')}
										</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/await}
		</div>

	</div>
{/await}
