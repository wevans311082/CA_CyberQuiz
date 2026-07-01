<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { TimelineEvent } from '$lib/quiz_types';

	interface Props {
		events: TimelineEvent[];
		compact?: boolean;
	}

	let { events, compact = false }: Props = $props();

	const fmt_time = (ts: string) => {
		try {
			return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
		} catch {
			return '';
		}
	};

	const dotClass = (type: TimelineEvent['type']) =>
		({
			inject: 'bg-orange-500',
			situation_update: 'bg-red-500',
			game_started: 'bg-teal-500',
			branch_resolved: 'bg-emerald-500',
			role_assigned: 'bg-cyan-500'
		})[type] ?? 'bg-slate-500';
</script>

{#if events.length === 0}
	<p class="text-center text-xs italic text-slate-500 py-6">
		No timeline events yet. Pushed injects and situation broadcasts will appear here.
	</p>
{:else}
	<ol class="relative space-y-3 {compact ? '' : 'pl-1'}">
		<div class="absolute left-[0.65rem] top-2 bottom-2 w-px bg-slate-700/80"></div>
		{#each events as ev (ev.id)}
			<li class="relative flex gap-3 pl-0">
				<span class="relative z-10 mt-1 h-3 w-3 shrink-0 rounded-full {dotClass(ev.type)} ring-2 ring-slate-900"></span>
				<div class="min-w-0 flex-1 rounded-lg border border-slate-700/50 bg-slate-800/40 px-3 py-2">
					<div class="flex flex-wrap items-baseline justify-between gap-2">
						<p class="text-xs font-semibold text-slate-100">{ev.title}</p>
						<span class="text-[10px] text-slate-500">{fmt_time(ev.timestamp)}</span>
					</div>
					{#if ev.detail}
						<p class="mt-1 text-xs leading-relaxed text-slate-400">{ev.detail}</p>
					{/if}
				</div>
			</li>
		{/each}
	</ol>
{/if}