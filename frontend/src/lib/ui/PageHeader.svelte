<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	interface Props {
		eyebrow?: string;
		title: string;
		description?: string;
		actions?: import('svelte').Snippet;
	}

	let { eyebrow = undefined, title, description = undefined, actions }: Props = $props();
</script>

<div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
	<div class="max-w-2xl">
		{#if eyebrow}
			<p
				class="mb-2 text-xs font-semibold uppercase tracking-[0.28em] text-teal-700 dark:text-cyan-300"
			>
				{eyebrow}
			</p>
		{/if}
		<h1 class="text-3xl font-semibold tracking-tight text-slate-950 dark:text-white sm:text-4xl">
			{title}
		</h1>
		{#if description}
			<p class="mt-3 text-base leading-7 text-slate-600 dark:text-slate-300">
				{description}
			</p>
		{/if}
	</div>
	{#if actions}
		<div class="flex flex-wrap gap-2">
			{@render actions()}
		</div>
	{/if}
</div>