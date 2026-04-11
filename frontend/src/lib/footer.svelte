<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import LanguageToggle from './language-toggle.svelte';
</script>

<footer class="w-screen border-t border-slate-200/70 bg-white/65 py-5 text-slate-600 backdrop-blur dark:border-slate-700/70 dark:bg-slate-900/55 dark:text-slate-300">
	<div class="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-4 text-sm md:flex-row">
		<p class="text-center md:text-left">CyberAsk Quiz for live hosted sessions.</p>
		<LanguageToggle />
	</div>
</footer>
