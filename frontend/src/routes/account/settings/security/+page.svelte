<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import Spinner from '$lib/Spinner.svelte';
	import { browser } from '$app/environment';
	import { startRegistration } from '@simplewebauthn/browser';
	import TotpSetup from './totp_setup.svelte';
	import BackupCodes from './backup_codes.svelte';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	let user_data: object | undefined = $state();
	let security_keys: Array<{ id: number }> | undefined = $state();
	let totp_activated: boolean | undefined = $state();
	let totp_data = $state();
	let backup_code = $state();

	const get_data = async () => {
		const res1 = await fetch('/api/v1/users/me');
		user_data = await res1.json();
		const res2 = await fetch('/api/v1/users/webauthn/list');
		security_keys = await res2.json();
		const res3 = await fetch('/api/v1/users/2fa/totp');
		totp_activated = (await res3.json()).activated;
	};
	let data = $state(get_data());

	const save_password_required = async () => {
		console.log(user_data?.require_password, 'here');
		if (!browser || user_data?.require_password === undefined) {
			return;
		}
		const pw = require_password();
		const res = await fetch('/api/v1/users/2fa/require_password', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ require_password: user_data?.require_password, password: pw })
		});
		user_data.require_password = (await res.json()).require_password;
	};

	const require_password = (): string | null => {
		return prompt('Please enter your password to continue');
	};

	const add_security_key = async () => {
		const pw = require_password();
		if (!pw) return;
		const res1 = await fetch('/api/v1/users/webauthn/add_key_init', {
			method: 'POST',
			body: JSON.stringify({ password: pw }),
			headers: { 'Content-Type': 'application/json' }
		});
		if (res1.status === 401) {
			alert('Password probably wrong');
			return;
		}
		if (!res1.ok) {
			throw Error('Response not ok');
		}
		let attResp;
		const resp_data = await res1.json();
		// eslint-disable-next-line no-useless-catch
		try {
			resp_data.authenticatorSelection.authenticatorAttachment = 'cross-platform';
			for (let i = 0; i++; i < resp_data.excludeCredentials.length) {
				resp_data.excludeCredentials[i].transports = undefined;
			}
			attResp = await startRegistration({ optionsJSON: resp_data });
		} catch (e) {
			throw e;
		}
		await fetch('/api/v1/users/webauthn/add_key', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(attResp)
		});
		data = get_data();
	};

	const remove_security_key = async (key_id: number) => {
		const pw = require_password();
		if (!pw) return;
		const res = await fetch(`/api/v1/users/webauthn/key/${key_id}`, {
			method: 'DELETE',
			body: JSON.stringify({ password: pw }),
			headers: { 'Content-Type': 'application/json' }
		});
		if (res.status === 401) {
			alert('Password probably wrong');
			return;
		}
		data = get_data();
	};

	const disable_totp = async () => {
		const pw = require_password();
		if (!pw) return;
		const res = await fetch(`/api/v1/users/2fa/totp`, {
			method: 'DELETE',
			body: JSON.stringify({ password: pw }),
			headers: { 'Content-Type': 'application/json' }
		});
		if (res.status === 401) {
			alert('Password probably wrong');
			return;
		}
		data = get_data();
	};

	const enable_totp = async () => {
		const pw = require_password();
		if (!pw) return;
		const res = await fetch('/api/v1/users/2fa/totp', {
			method: 'POST',
			body: JSON.stringify({ password: pw }),
			headers: { 'Content-Type': 'application/json' }
		});
		if (res.status === 401) {
			alert('Password probably wrong');
			return;
		}
		data = get_data();
		totp_data = await res.json();
	};

	const get_backup_code = async () => {
		const pw = require_password();
		if (!pw) return;
		if (!confirm('If you continue, your old backup-code will be removed.')) {
			return;
		}
		const res = await fetch('/api/v1/users/2fa/backup_code', {
			method: 'POST',
			body: JSON.stringify({ password: pw }),
			headers: { 'Content-Type': 'application/json' }
		});
		if (res.status === 401) {
			alert('Password probably wrong');
			return;
		}
		backup_code = (await res.json()).code;
	};
</script>

{#await data}
	<Spinner my_20={false} />
{:then _}
	<div class="min-h-screen text-white px-4 py-8 max-w-3xl mx-auto flex flex-col gap-6">

		<h1 class="text-2xl font-semibold text-white">{$t('settings_page.security_settings')}</h1>

		<!-- Backup Code card -->
		<div class="rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_80px_rgba(15,23,42,0.6)] p-6 flex flex-col gap-4">
			<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80">{$t('security_settings.backup_code')}</p>
			<p class="text-sm text-slate-400">Generate a backup code for account recovery if you lose access to your 2FA methods.</p>
			<div>
				<button onclick={get_backup_code} class="rounded-full border border-white/15 px-5 py-2.5 text-sm font-semibold text-white/90 hover:bg-white/6 transition-colors">
					{$t('security_settings.get_backup_code')}
				</button>
			</div>
		</div>

		<!-- 2FA / TOTP card -->
		<div class="rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_80px_rgba(15,23,42,0.6)] p-6 flex flex-col gap-5">
			<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80">{$t('security_settings.activate_2fa')}</p>

			<!-- Require password toggle -->
			<div class="{!totp_activated ? 'opacity-40 pointer-events-none' : ''} flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3">
				<div>
					<p class="text-sm font-medium text-white">Require password on 2FA</p>
					<p class="text-xs text-slate-400 mt-0.5">
						{user_data?.require_password ? $t('security_settings.2fa_activated') : $t('security_settings.2fa_deactivated')}
					</p>
				</div>
				<button
					disabled={!totp_activated}
					onclick={() => { user_data.require_password = !user_data.require_password; save_password_required(); }}
					type="button"
					role="switch"
					aria-checked={user_data?.require_password}
					class="{user_data?.require_password ? 'bg-[#B07156]' : 'bg-white/15'} relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full transition-colors"
				>
					<span class="{user_data?.require_password ? 'translate-x-5' : 'translate-x-0.5'} pointer-events-none inline-block h-5 w-5 mt-0.5 rounded-full bg-white transition-transform will-change-transform"></span>
				</button>
			</div>

			<!-- TOTP section -->
			<div class="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3">
				<div>
					<p class="text-sm font-medium text-white">{$t('security_settings.totp')}</p>
					<p class="text-xs text-slate-400 mt-0.5">
						{totp_activated ? $t('security_settings.totp_available') : $t('security_settings.totp_unavailable')}
					</p>
				</div>
				{#if totp_activated}
					<button onclick={disable_totp} class="rounded-full border border-red-500/40 px-4 py-2 text-xs font-semibold text-red-400 hover:bg-red-500/10 transition-colors">
						{$t('security_settings.disable_totp')}
					</button>
				{:else}
					<button onclick={enable_totp} class="rounded-full bg-[#B07156] px-4 py-2 text-xs font-semibold text-slate-950 hover:bg-[#c07d62] transition-colors">
						{$t('security_settings.enable_totp')}
					</button>
				{/if}
			</div>
		</div>

		<!-- WebAuthn card -->
		<div class="rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_80px_rgba(15,23,42,0.6)] p-6 flex flex-col gap-4">
			<div class="flex items-center justify-between">
				<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80">{$t('security_settings.webauthn')}</p>
				<button onclick={add_security_key} class="rounded-full bg-[#B07156] px-4 py-2 text-xs font-semibold text-slate-950 hover:bg-[#c07d62] transition-colors">
					{$t('security_settings.add_security_key')}
				</button>
			</div>
			{#if security_keys.length > 0}
				<p class="text-xs text-slate-400">{$t('security_settings.webauthn_available')}</p>
				<div class="flex flex-col gap-2">
					{#each security_keys as key, i}
						<div class="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
							<span>Security key {i + 1}</span>
							<button onclick={() => remove_security_key(key.id)} class="rounded-full border border-red-500/40 px-3 py-1 text-xs font-semibold text-red-400 hover:bg-red-500/10 transition-colors">
								Remove
							</button>
						</div>
					{/each}
				</div>
			{:else}
				<p class="text-sm text-slate-500">{$t('security_settings.webauthn_unavailable')}</p>
			{/if}
		</div>

	</div>
{/await}

{#if totp_data}
	<TotpSetup bind:totp_data />
{/if}

{#if backup_code}
	<BackupCodes bind:backup_code />
{/if}
