<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	interface Tab {
		id: string;
		label: string;
	}

	interface Props {
		tabs: Tab[];
		active: string;
		onchange?: (id: string) => void;
	}

	let { tabs, active = $bindable(), onchange }: Props = $props();

	const select = (id: string) => {
		active = id;
		onchange?.(id);
	};
</script>

<div
	class="flex flex-wrap gap-1 rounded-2xl border border-slate-200/70 bg-white/80 p-1 dark:border-slate-700/80 dark:bg-slate-900/60"
	role="tablist"
>
	{#each tabs as tab}
		<button
			type="button"
			role="tab"
			aria-selected={active === tab.id}
			class="flex-1 rounded-xl px-4 py-2.5 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent {active ===
			tab.id
				? 'bg-brand-accent text-slate-950 shadow-sm'
				: 'text-slate-600 hover:bg-slate-100/80 dark:text-slate-300 dark:hover:bg-slate-800/60'}"
			onclick={() => select(tab.id)}
		>
			{tab.label}
		</button>
	{/each}
</div>