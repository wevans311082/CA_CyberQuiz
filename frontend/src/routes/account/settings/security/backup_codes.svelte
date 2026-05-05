<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	let { backup_code = $bindable() } = $props();

	let already_downloaded = false;

	const download_code = (force = false) => {
		if (already_downloaded && !force) {
			return;
		}
		const el = document.createElement('a');
		el.setAttribute('href', `data:text/plain;charset=utf-8,${backup_code}`);
		el.setAttribute('download', 'ClassQuiz-Backup-Code.txt');
		el.style.display = 'none';
		document.body.appendChild(el);
		el.click();
		document.body.removeChild(el);
		already_downloaded = true;
	};
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
	<div class="rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_80px_rgba(15,23,42,0.6)] text-white w-full max-w-md flex flex-col gap-6 p-8">
		<div class="flex items-center justify-between">
			<h2 class="text-xl font-semibold text-white">{$t('security_settings.backup_codes.your_backup_code')}</h2>
			<button onclick={() => { backup_code = undefined; }} class="rounded-full border border-white/15 px-4 py-1.5 text-xs font-semibold text-white/90 hover:bg-white/6 transition-colors">
				{$t('words.close')}
			</button>
		</div>
		<div class="border-t border-white/8"></div>
		<div class="rounded-xl border border-white/10 bg-white/5 p-4 text-center">
			<p class="select-all font-mono text-lg text-white cursor-pointer" onclick={() => download_code(false)}>
				{backup_code}
			</p>
		</div>
		<p class="text-sm text-slate-400 text-center">{$t('security_settings.backup_codes.save_somewhere_save')}</p>
		<div class="flex gap-3 justify-center">
			<button onclick={() => download_code(true)} class="rounded-full bg-[#B07156] px-6 py-2.5 text-sm font-semibold text-slate-950 hover:bg-[#c07d62] transition-colors">
				{$t('security_settings.backup_codes.download_code')}
			</button>
			<button onclick={() => { backup_code = undefined; }} class="rounded-full border border-white/15 px-5 py-2.5 text-sm font-semibold text-white/90 hover:bg-white/6 transition-colors">
				{$t('words.close')}
			</button>
		</div>
	</div>
</div>
