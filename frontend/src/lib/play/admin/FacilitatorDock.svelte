<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	export type FacilitatorTab = 'situation' | 'injects' | 'hands' | 'roles' | 'timeline';

	interface Props {
		open?: boolean;
		activeTab?: FacilitatorTab;
		handsCount?: number;
		timelineCount?: number;
		severity?: string;
		phase?: string;
		showRoles?: boolean;
		onclose?: () => void;
		onopenprojector?: () => void;
		situation?: import('svelte').Snippet;
		injects?: import('svelte').Snippet;
		hands?: import('svelte').Snippet;
		roles?: import('svelte').Snippet;
		timeline?: import('svelte').Snippet;
	}

	let {
		open = $bindable(false),
		activeTab = $bindable<FacilitatorTab>('situation'),
		handsCount = 0,
		timelineCount = 0,
		severity = 'low',
		phase = 'Detection',
		showRoles = true,
		onclose,
		onopenprojector,
		situation,
		injects,
		hands,
		roles,
		timeline
	}: Props = $props();

	const tabs = $derived(
		[
			{ id: 'situation' as FacilitatorTab, label: 'Situation', accent: 'text-purple-300' },
			{ id: 'injects' as FacilitatorTab, label: 'Injects', accent: 'text-orange-300' },
			{ id: 'hands' as FacilitatorTab, label: 'Hands', accent: 'text-amber-300', badge: handsCount },
			{ id: 'timeline' as FacilitatorTab, label: 'Timeline', accent: 'text-slate-300', badge: timelineCount },
			...(showRoles ? [{ id: 'roles' as FacilitatorTab, label: 'Roles', accent: 'text-cyan-300' }] : [])
		]
	);

	const severityClass = $derived(
		({
			low: 'bg-emerald-400',
			medium: 'bg-amber-400',
			high: 'bg-orange-500',
			critical: 'bg-red-500'
		})[severity] ?? 'bg-slate-400'
	);

	const close = () => {
		open = false;
		onclose?.();
	};
</script>

{#if open}
	<div
		class="fixed inset-0 z-40 bg-black/40 backdrop-blur-[2px] lg:bg-transparent lg:backdrop-blur-none"
		onclick={close}
		role="button"
		tabindex="-1"
		aria-label="Close facilitator console"
		onkeydown={(e) => {
			if (e.key === 'Escape') close();
		}}
	></div>

	<aside
		class="host-panel fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-slate-700/80 rounded-none"
		aria-label="Facilitator console"
	>
		<header class="border-b border-slate-700/60 px-4 py-3">
			<div class="flex items-start justify-between gap-3">
				<div>
					<p class="text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-400">
						Facilitator Console
					</p>
					<div class="mt-1 flex flex-wrap items-center gap-2">
						<span class="inline-flex items-center gap-1.5 rounded-full border border-slate-600/60 bg-slate-800/80 px-2.5 py-1 text-xs text-slate-200">
							<span class="h-2 w-2 rounded-full {severityClass}"></span>
							{severity}
						</span>
						<span class="rounded-full border border-purple-500/30 bg-purple-500/10 px-2.5 py-1 text-xs text-purple-200">
							{phase}
						</span>
						{#if handsCount > 0}
							<span class="rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-1 text-xs text-amber-200">
								✋ {handsCount}
							</span>
						{/if}
					</div>
				</div>
				<div class="flex gap-1">
					{#if onopenprojector}
						<button type="button" class="host-btn" onclick={onopenprojector} title="Open projector display">Projector</button>
					{/if}
					<button type="button" class="host-btn px-2.5" onclick={close} aria-label="Close">✕</button>
				</div>
			</div>

			<div class="mt-3 flex gap-1 overflow-x-auto">
				{#each tabs as tab}
					<button
						type="button"
						class="relative shrink-0 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors"
						class:bg-slate-800={activeTab !== tab.id}
						class:text-slate-400={activeTab !== tab.id}
						class:bg-brand-accent={activeTab === tab.id}
						class:text-slate-950={activeTab === tab.id}
						onclick={() => {
							activeTab = tab.id;
						}}
					>
						{tab.label}
						{#if tab.badge && tab.badge > 0}
							<span
								class="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white"
							>{tab.badge}</span>
						{/if}
					</button>
				{/each}
			</div>
		</header>

		<div class="flex-1 overflow-y-auto px-4 py-4">
			{#if activeTab === 'situation' && situation}
				{@render situation()}
			{:else if activeTab === 'injects' && injects}
				{@render injects()}
			{:else if activeTab === 'hands' && hands}
				{@render hands()}
			{:else if activeTab === 'roles' && roles}
				{@render roles()}
			{:else if activeTab === 'timeline' && timeline}
				{@render timeline()}
			{/if}
		</div>
	</aside>
{/if}