<!--
SPDX-FileCopyrightText: 2025

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Inject, SituationStatus, TimelineEvent } from '$lib/quiz_types';
	import type { Socket } from 'socket.io-client';
	import { fade, fly } from 'svelte/transition';

	interface Props {
		open: boolean;
		situation_status: SituationStatus | null;
		injects_log: Array<{ inject: Inject; triggered_by: string; timestamp: string }>;
		event_log?: TimelineEvent[];
		socket: Socket;
	}

	let {
		open = $bindable(),
		situation_status,
		injects_log,
		event_log = [],
		socket
	}: Props = $props();

	let active_tab = $state<'timeline' | 'status'>('timeline');

	const severity_colors: Record<string, string> = {
		low: 'bg-green-600',
		medium: 'bg-yellow-600',
		high: 'bg-orange-600',
		critical: 'bg-red-600'
	};

	// Timeline: merge event_log (player events) + injects_log entries not already represented
	const timeline = $derived.by(() => {
		// Convert injects_log entries that don't appear in event_log into synthetic events
		const inject_ids_in_log = new Set(
			event_log.filter(e => e.type === 'inject').map(e => (e.data?.id as string) ?? '')
		);
		const synthetic: TimelineEvent[] = injects_log
			.filter(entry => !inject_ids_in_log.has(entry.inject?.id ?? ''))
			.map((entry, idx) => ({
				id: `inj-${idx}`,
				type: 'inject' as const,
				timestamp: entry.timestamp,
				title: entry.inject?.title ?? 'Inject',
				detail: entry.inject?.content?.slice(0, 80),
				data: { severity: entry.inject?.severity } as Record<string, unknown>
			}));

		return [...event_log, ...synthetic].sort(
			(a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
		);
	});

	interface EventStyle {
		icon: string;
		dot: string;
		label_class: string;
	}

	const event_style: Record<string, EventStyle> = {
		game_started:     { icon: 'â–¶', dot: 'bg-teal-500', label_class: 'text-teal-700 dark:text-teal-300' },
		question_asked:   { icon: 'â“', dot: 'bg-indigo-500', label_class: 'text-indigo-700 dark:text-indigo-300' },
		answer_results:   { icon: 'ðŸ“Š', dot: 'bg-blue-400', label_class: 'text-blue-700 dark:text-blue-300' },
		inject:           { icon: 'âš ï¸', dot: 'bg-orange-500', label_class: 'text-orange-700 dark:text-orange-300' },
		situation_update: { icon: 'ðŸš¨', dot: 'bg-red-500', label_class: 'text-red-700 dark:text-red-300' },
		role_assigned:    { icon: 'ðŸ‘¤', dot: 'bg-violet-500', label_class: 'text-violet-700 dark:text-violet-300' },
		branch_resolved:  { icon: 'ðŸ”€', dot: 'bg-emerald-500', label_class: 'text-emerald-700 dark:text-emerald-300' },
		decision_made:    { icon: 'âœ…', dot: 'bg-green-500', label_class: 'text-green-700 dark:text-green-300' },
		scenario_complete: { icon: 'ðŸ', dot: 'bg-gray-600', label_class: 'text-gray-700 dark:text-gray-300' }
	};

	const inject_severity_bg: Record<string, string> = {
		info:     'border-l-blue-400 bg-blue-50/60 dark:bg-blue-900/30',
		warning:  'border-l-yellow-400 bg-yellow-50/60 dark:bg-yellow-900/30',
		critical: 'border-l-red-500 bg-red-50/60 dark:bg-red-900/30'
	};

	const fmt_time = (ts: string) => {
		try { return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }); }
		catch { return ''; }
	};

	const refresh = () => { socket.emit('get_situation', {}); };
</script>

<!-- Toggle Button -->
{#if !open}
	<button
		class="fixed bottom-4 left-4 z-50 rounded-full bg-purple-600 p-3 text-white shadow-lg hover:bg-purple-700 transition"
		onclick={() => { open = true; refresh(); }}
		transition:fade={{ duration: 150 }}
		title="Open Situation Room"
	>
		<svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
		</svg>
		{#if timeline.length > 0}
			<span class="absolute -top-1 -right-1 min-w-[1.1rem] h-[1.1rem] rounded-full bg-orange-500 text-[10px] font-bold text-white flex items-center justify-center px-0.5">
				{timeline.length}
			</span>
		{/if}
	</button>
{/if}

<!-- Situation Room Panel -->
{#if open}
	<div class="fixed inset-0 z-50 flex" transition:fade={{ duration: 150 }}>
		<!-- Backdrop -->
		<button
			class="absolute inset-0 bg-black/40"
			onclick={() => { open = false; }}
			aria-label="Close situation room"
		></button>

		<!-- Panel -->
		<div
			class="relative ml-auto w-full max-w-md h-full bg-white dark:bg-gray-800 shadow-2xl flex flex-col overflow-hidden"
			transition:fly={{ x: 400, duration: 250 }}
		>
			<!-- Header -->
			<div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-purple-600 text-white shrink-0">
				<h2 class="text-lg font-bold">Situation Room</h2>
				<button onclick={() => { open = false; }} class="text-white/80 hover:text-white text-2xl leading-none">&times;</button>
			</div>

			<!-- Tabs -->
			<div class="flex border-b border-gray-200 dark:border-gray-700 shrink-0">
				<button
					class="flex-1 py-2 text-sm font-semibold transition border-b-2"
					class:border-purple-600={active_tab === 'timeline'}
					class:text-purple-600={active_tab === 'timeline'}
					class:border-transparent={active_tab !== 'timeline'}
					class:text-gray-500={active_tab !== 'timeline'}
					onclick={() => { active_tab = 'timeline'; }}
				>
					Timeline
					{#if timeline.length > 0}
						<span class="ml-1 rounded-full bg-purple-100 dark:bg-purple-800 px-1.5 py-0.5 text-[10px] text-purple-700 dark:text-purple-300">{timeline.length}</span>
					{/if}
				</button>
				<button
					class="flex-1 py-2 text-sm font-semibold transition border-b-2"
					class:border-purple-600={active_tab === 'status'}
					class:text-purple-600={active_tab === 'status'}
					class:border-transparent={active_tab !== 'status'}
					class:text-gray-500={active_tab !== 'status'}
					onclick={() => { active_tab = 'status'; }}
				>Incident Status</button>
			</div>

			<!-- Content -->
			<div class="flex-1 overflow-y-auto">

				<!-- TIMELINE TAB -->
				{#if active_tab === 'timeline'}
					{#if timeline.length === 0}
						<div class="p-6 text-center text-sm text-gray-400 italic">No events yet. Events will appear here as the exercise progresses.</div>
					{:else}
						<div class="relative px-4 py-4">
							<!-- Vertical line -->
							<div class="absolute left-[2.15rem] top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>

							<ol class="space-y-4">
								{#each timeline as ev (ev.id)}
									{@const style = event_style[ev.type] ?? { icon: 'â€¢', dot: 'bg-gray-400', label_class: 'text-gray-600' }}
									{@const inject_sev = ev.type === 'inject' ? (ev.data?.severity as string ?? 'info') : null}
									<li class="flex gap-3">
										<!-- Dot -->
										<div class="relative z-10 flex shrink-0 w-7 h-7 items-center justify-center rounded-full {style.dot} text-white text-xs font-bold shadow">
											{style.icon}
										</div>

										<!-- Content -->
										<div class="flex-1 min-w-0 pt-0.5">
											<div class="flex items-baseline gap-2 flex-wrap">
												<span class="text-sm font-semibold {style.label_class} leading-tight">{ev.title}</span>
												<span class="text-[10px] text-gray-400 dark:text-gray-500 shrink-0">{fmt_time(ev.timestamp)}</span>
											</div>
											{#if ev.detail}
												{#if inject_sev}
													<div class="mt-1 border-l-4 rounded-r pl-2 py-1 text-xs text-gray-700 dark:text-gray-300 {inject_severity_bg[inject_sev] ?? inject_severity_bg.info}">
														{ev.detail}
													</div>
												{:else}
													<p class="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{ev.detail}</p>
												{/if}
											{/if}
										</div>
									</li>
								{/each}
							</ol>
						</div>
					{/if}
				{/if}

				<!-- STATUS TAB -->
				{#if active_tab === 'status'}
					<div class="p-4 space-y-4">
						{#if situation_status}
							<div class="rounded-lg border border-gray-200 dark:border-gray-600 p-3 space-y-3">
								<div class="flex items-center gap-2 flex-wrap">
									<span class="text-xs font-semibold uppercase text-gray-500">Severity:</span>
									<span class="rounded-full px-2.5 py-0.5 text-xs font-bold text-white {severity_colors[situation_status.severity] ?? 'bg-gray-500'}">
										{situation_status.severity}
									</span>
								</div>
								<div class="flex items-center gap-2">
									<span class="text-xs font-semibold uppercase text-gray-500">Phase:</span>
									<span class="text-sm font-medium">{situation_status.phase || 'N/A'}</span>
								</div>
								{#if situation_status.affected_systems?.length}
									<div>
										<span class="text-xs font-semibold uppercase text-gray-500 block mb-1">Affected Systems:</span>
										<div class="flex flex-wrap gap-1">
											{#each situation_status.affected_systems as sys}
												<span class="rounded-full bg-purple-100 dark:bg-purple-800 px-2 py-0.5 text-xs text-purple-800 dark:text-purple-200">{sys}</span>
											{/each}
										</div>
									</div>
								{/if}
								{#if situation_status.summary}
									<div>
										<span class="text-xs font-semibold uppercase text-gray-500 block mb-1">Summary:</span>
										<p class="text-sm whitespace-pre-wrap rounded bg-gray-50 dark:bg-gray-700/60 p-2">{situation_status.summary}</p>
									</div>
								{/if}
								{#if situation_status.context_notes}
									<div>
										<span class="text-xs font-semibold uppercase text-gray-500 block mb-1">Context / Background:</span>
										<p class="text-sm whitespace-pre-wrap rounded bg-gray-50 dark:bg-gray-700/60 p-2">{situation_status.context_notes}</p>
									</div>
								{/if}
							</div>
						{:else}
							<p class="text-sm text-gray-400 italic">No incident status reported yet.</p>
						{/if}

						<!-- Inject History in status tab too -->
						{#if injects_log.length}
							<div>
								<h3 class="text-xs font-bold uppercase text-gray-500 mb-2">Inject History ({injects_log.length})</h3>
								<div class="space-y-2">
									{#each [...injects_log].reverse() as entry}
										{@const sev = entry.inject?.severity ?? 'info'}
										<div class="rounded border-l-4 p-2 text-xs {inject_severity_bg[sev] ?? inject_severity_bg.info}">
											<div class="flex justify-between items-center gap-2">
												<span class="font-bold uppercase text-orange-700 dark:text-orange-300">{entry.inject?.severity}</span>
												<span class="text-[10px] text-gray-400">{fmt_time(entry.timestamp)}</span>
											</div>
											<p class="font-semibold mt-0.5">{entry.inject?.title}</p>
											{#if entry.inject?.content}
												<p class="mt-0.5 text-gray-600 dark:text-gray-300 whitespace-pre-wrap">{entry.inject.content}</p>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{/if}
					</div>
				{/if}
			</div>

			<!-- Footer -->
			<div class="border-t border-gray-200 dark:border-gray-700 px-4 py-2 shrink-0">
				<button
					class="w-full rounded bg-purple-600 px-3 py-1.5 text-sm text-white hover:bg-purple-700"
					onclick={refresh}
				>Refresh Status</button>
			</div>
		</div>
	</div>
{/if}
<!--
SPDX-FileCopyrightText: 2025

SPDX-License-Identifier: MPL-2.0
-->

