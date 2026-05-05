<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import QRCode from 'qrcode';
	import Spinner from '$lib/Spinner.svelte';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	interface Props {
		totp_data: { url: string; secret: string } | undefined;
	}

	let { totp_data = $bindable() }: Props = $props();

	const get_image_url = async () => {
		return await QRCode.toDataURL(totp_data.url);
	};
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
	<div class="rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_80px_rgba(15,23,42,0.6)] text-white w-full max-w-2xl flex flex-col gap-6 p-8">
		<div class="flex items-center justify-between">
			<h2 class="text-xl font-semibold text-white">{$t('security_settings.totp_setup.totp_setup')}</h2>
			<button onclick={() => { totp_data = undefined; }} class="rounded-full border border-white/15 px-4 py-1.5 text-xs font-semibold text-white/90 hover:bg-white/6 transition-colors">
				{$t('words.close')}
			</button>
		</div>
		<div class="border-t border-white/8"></div>
		<div class="grid grid-cols-1 sm:grid-cols-3 gap-6 items-center">
			<div class="flex flex-col gap-3 text-sm text-slate-400">
				<p>{$t('security_settings.totp_setup.scan_to_set_up')}</p>
				<p class="text-xs text-slate-500">{$t('security_settings.totp_setup.enter_as_secret_if_no_see_code')}</p>
			</div>
			<div class="flex flex-col items-center gap-3">
				{#await get_image_url()}
					<Spinner my_20={false} />
				{:then data}
					<img src={data} alt="QR-Code for TOTP setup" class="w-48 h-48 rounded-xl border border-white/10" />
				{/await}
				<p class="select-all font-mono text-xs bg-white/5 rounded-lg px-3 py-1.5 border border-white/10 text-slate-300">{totp_data.secret}</p>
			</div>
			<div class="rounded-2xl border border-[#B07156]/40 bg-[#B07156]/8 p-4 text-sm text-[#c07d62]">
				<p class="font-semibold mb-1">Important</p>
				<p>{$t('security_settings.totp_setup.do_not_forget_backup_code')}</p>
			</div>
		</div>
	</div>
</div>
