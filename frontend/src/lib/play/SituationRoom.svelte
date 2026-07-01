<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Inject, SituationStatus, TimelineEvent } from '$lib/quiz_types';
	import type { Socket } from 'socket.io-client';
	import { fade, fly } from 'svelte/transition';
	import FacilitatorTimeline from '$lib/play/admin/FacilitatorTimeline.svelte';
	import {
		buildFacilitatorTimeline,
		type SituationLogEntry
	} from '$lib/facilitator/timeline';

	interface Props {
		open: boolean;
		situation_status: SituationStatus | null;
		injects_log: Array<{ inject: Inject; triggered_by: string; timestamp: string }>;
		situation_log?: SituationLogEntry[];
		event_log?: TimelineEvent[];
		socket: Socket;
	}

	let {
		open = $bindable(),
		situation_status,
		injects_log,
		situation_log = [],
		event_log = [],
		socket
	}: Props = $props();

	let active_tab = $state<'timeline' | 'status'>('timeline');

	const severity_dot: Record<string, string> = {
		low: 'bg-emerald-400',
		medium: 'bg-amber-400',
		high: 'bg-orange-500',
		critical: 'bg-red-500'
	};

	const inject_border: Record<string, string> = {
		info: 'border-cyan-500/40 bg-cyan-500/10',
		warning: 'border-amber-500/40 bg-amber-500/10',
		critical: 'border-red-500/40 bg-red-500/10'
	};

	const timeline = $derived.by(() => {
		const serverTimeline = buildFacilitatorTimeline(injects_log, situation_log);
		const clientOnly = event_log.filter(
			(e) => e.type !== 'inject' && e.type !== 'situation_update'
		);
		return [...clientOnly, ...serverTimeline].sort(
			(a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
		);
	});

	const fmt_time = (ts: string) => {
		try {
			return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
		} catch {
			return '';
		}
	};

	const refresh = () => {
		socket.emit('get_situation', {});
	};
</script>

{#if !open}
	<button
		type="button"
		class="fixed bottom-4 left-4 z-50 flex h-12 w-12 items-center justify-center rounded-full border border-cyan-500/40 bg-slate-900/90 text-cyan-200 shadow-lg backdrop-blur-xl transition hover:bg-slate-800"
		onclick={() => {
			open = true;
			refresh();
		}}
		transition:fade={{ duration: 150 }}
		title="Open Situation Room"
	>
		<svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
			/>
		</svg>
		{#if timeline.length > 0}
			<span
				class="absolute -right-1 -top-1 flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-orange-500 px-1 text-[10px] font-bold text-white"
			>
				{timeline.length}
			</span>
		{/if}
	</button>
{/if}

{#if open}
	<div class="fixed inset-0 z-50 flex" transition:fade={{ duration: 150 }}>
		<button
			type="button"
			class="absolute inset-0 bg-black/50 backdrop-blur-[2px]"
			onclick={() => {
				open = false;
			}}
			aria-label="Close situation room"
		></button>

		<aside
			class="host-panel relative ml-auto flex h-full w-full max-w-md flex-col rounded-none border-l border-slate-700/80"
			transition:fly={{ x: 400, duration: 250 }}
		>
			<header class="shrink-0 border-b border-slate-700/60 px-4 py-3">
				<div class="flex items-center justify-between gap-3">
					<div>
						<p class="text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-400">Situation Room</p>
						{#if situation_status}
							<div class="mt-1 flex flex-wrap items-center gap-2">
								<span class="inline-flex items-center gap-1.5 rounded-full border border-slate-600/60 bg-slate-800/80 px-2.5 py-1 text-xs text-slate-200">
									<span class="h-2 w-2 rounded-full {severity_dot[situation_status.severity] ?? 'bg-slate-400'}"></span>
									{situation_status.severity}
								</span>
								<span class="rounded-full border border-purple-500/30 bg-purple-500/10 px-2.5 py-1 text-xs text-purple-200">
									{situation_status.phase}
								</span>
							</div>
						{/if}
					</div>
					<button type="button" class="host-btn px-2.5" onclick={() => (open = false)} aria-label="Close">✕</button>
				</div>

				<div class="mt-3 flex gap-1">
					<button
						type="button"
						class="relative flex-1 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors"
						class:bg-brand-accent={active_tab === 'timeline'}
						class:text-slate-950={active_tab === 'timeline'}
						class:bg-slate-800={active_tab !== 'timeline'}
						class:text-slate-400={active_tab !== 'timeline'}
						onclick={() => {
							active_tab = 'timeline';
						}}
					>
						Timeline
						{#if timeline.length > 0}
							<span class="ml-1 text-[10px] opacity-80">({timeline.length})</span>
						{/if}
					</button>
					<button
						type="button"
						class="flex-1 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors"
						class:bg-brand-accent={active_tab === 'status'}
						class:text-slate-950={active_tab === 'status'}
						class:bg-slate-800={active_tab !== 'status'}
						class:text-slate-400={active_tab !== 'status'}
						onclick={() => {
							active_tab = 'status';
						}}
					>
						Incident Status
					</button>
				</div>
			</header>

			<div class="flex-1 overflow-y-auto px-4 py-4">
				{#if active_tab === 'timeline'}
					<FacilitatorTimeline events={timeline} />
				{:else if situation_status}
					<div class="space-y-4">
						<div class="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4">
							<div class="flex flex-wrap items-center gap-2">
								<span class="host-label mb-0">Severity</span>
								<span class="inline-flex items-center gap-1.5 rounded-full border border-slate-600/60 bg-slate-800/80 px-2.5 py-1 text-xs text-slate-200">
									<span class="h-2 w-2 rounded-full {severity_dot[situation_status.severity] ?? 'bg-slate-400'}"></span>
									{situation_status.severity}
								</span>
							</div>
							<div class="mt-3">
								<span class="host-label">Phase</span>
								<p class="mt-1 text-sm text-slate-200">{situation_status.phase || 'N/A'}</p>
							</div>
							{#if situation_status.affected_systems?.length}
								<div class="mt-3">
									<span class="host-label">Affected systems</span>
									<div class="mt-1 flex flex-wrap gap-1">
										{#each situation_status.affected_systems as sys}
											<span class="rounded-full border border-purple-500/40 bg-purple-500/20 px-2 py-0.5 text-[10px] text-purple-200">{sys}</span>
										{/each}
									</div>
								</div>
							{/if}
							{#if situation_status.summary}
								<div class="mt-3">
									<span class="host-label">Summary</span>
									<p class="mt-1 whitespace-pre-wrap text-sm text-slate-300">{situation_status.summary}</p>
								</div>
							{/if}
							{#if situation_status.context_notes}
								<div class="mt-3">
									<span class="host-label">Context</span>
									<p class="mt-1 whitespace-pre-wrap text-sm text-slate-400">{situation_status.context_notes}</p>
								</div>
							{/if}
						</div>

						{#if injects_log.length}
							<div>
								<span class="host-label">Inject history ({injects_log.length})</span>
								<div class="mt-2 space-y-2">
									{#each [...injects_log].reverse() as entry}
										{@const sev = entry.inject?.severity ?? 'info'}
										<div class="rounded-lg border p-3 text-xs {inject_border[sev] ?? inject_border.info}">
											<div class="flex items-center justify-between gap-2">
												<span class="font-semibold uppercase text-slate-200">{sev}</span>
												<span class="text-[10px] text-slate-500">{fmt_time(entry.timestamp)}</span>
											</div>
											<p class="mt-1 font-medium text-slate-100">{entry.inject?.title}</p>
											{#if entry.inject?.content}
												<p class="mt-1 whitespace-pre-wrap text-slate-400">{entry.inject.content}</p>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{/if}
					</div>
				{:else}
					<p class="py-8 text-center text-xs italic text-slate-500">No incident status reported yet.</p>
				{/if}
			</div>

			<footer class="shrink-0 border-t border-slate-700/60 px-4 py-3">
				<button type="button" class="host-btn-accent w-full" onclick={refresh}>Refresh status</button>
			</footer>
		</aside>
	</div>
{/if}