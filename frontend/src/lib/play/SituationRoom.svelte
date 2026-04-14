<!--
SPDX-FileCopyrightText: 2025

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Inject, SituationStatus } from '$lib/quiz_types';
	import type { Socket } from 'socket.io-client';
	import { fade, fly } from 'svelte/transition';

	interface Props {
		open: boolean;
		situation_status: SituationStatus | null;
		injects_log: Array<{ inject: Inject; triggered_by: string; timestamp: string }>;
		socket: Socket;
	}

	let {
		open = $bindable(),
		situation_status,
		injects_log,
		socket
	}: Props = $props();

	const severity_colors: Record<string, string> = {
		low: 'bg-green-600',
		medium: 'bg-yellow-600',
		high: 'bg-orange-600',
		critical: 'bg-red-600'
	};

	const inject_severity_colors: Record<string, { border: string; bg: string; text: string }> = {
		info: { border: 'border-blue-400', bg: 'bg-blue-50 dark:bg-blue-900/40', text: 'text-blue-700 dark:text-blue-300' },
		warning: { border: 'border-yellow-400', bg: 'bg-yellow-50 dark:bg-yellow-900/40', text: 'text-yellow-700 dark:text-yellow-300' },
		critical: { border: 'border-red-400', bg: 'bg-red-50 dark:bg-red-900/40', text: 'text-red-700 dark:text-red-300' }
	};

	const refresh = () => {
		socket.emit('get_situation', {});
	};
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
	</button>
{/if}

<!-- Situation Room Panel -->
{#if open}
	<div
		class="fixed inset-0 z-50 flex"
		transition:fade={{ duration: 150 }}
	>
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
			<div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-purple-600 text-white">
				<h2 class="text-lg font-bold">Situation Room</h2>
				<button
					onclick={() => { open = false; }}
					class="text-white/80 hover:text-white text-2xl leading-none"
				>&times;</button>
			</div>

			<!-- Content -->
			<div class="flex-1 overflow-y-auto p-4 space-y-4">
				<!-- Current Status -->
				<div>
					<h3 class="text-sm font-bold uppercase text-gray-500 dark:text-gray-400 mb-2">Incident Status</h3>
					{#if situation_status}
						<div class="rounded-lg border border-gray-200 dark:border-gray-600 p-3 space-y-2">
							<div class="flex items-center gap-2">
								<span class="text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">Severity:</span>
								<span class="rounded-full px-2 py-0.5 text-xs font-bold text-white {severity_colors[situation_status.severity] ?? 'bg-gray-500'}">
									{situation_status.severity}
								</span>
							</div>
							<div class="flex items-center gap-2">
								<span class="text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">Phase:</span>
								<span class="text-sm font-medium">{situation_status.phase || 'N/A'}</span>
							</div>
							{#if situation_status.affected_systems?.length}
								<div>
									<span class="text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">Affected Systems:</span>
									<div class="flex flex-wrap gap-1 mt-1">
										{#each situation_status.affected_systems as sys}
											<span class="rounded-full bg-purple-100 dark:bg-purple-800 px-2 py-0.5 text-xs text-purple-800 dark:text-purple-200">
												{sys}
											</span>
										{/each}
									</div>
								</div>
							{/if}
							{#if situation_status.summary}
								<div>
									<span class="text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">Summary:</span>
									<p class="text-sm mt-1 whitespace-pre-wrap">{situation_status.summary}</p>
								</div>
							{/if}
						</div>
					{:else}
						<p class="text-sm text-gray-400 italic">No incident status reported yet.</p>
					{/if}
				</div>

				<!-- Inject History -->
				<div>
					<h3 class="text-sm font-bold uppercase text-gray-500 dark:text-gray-400 mb-2">
						Inject History ({injects_log.length})
					</h3>
					{#if injects_log.length === 0}
						<p class="text-sm text-gray-400 italic">No injects received yet.</p>
					{:else}
						<div class="space-y-2">
							{#each [...injects_log].reverse() as entry}
								{@const colors = inject_severity_colors[entry.inject?.severity ?? 'info'] ?? inject_severity_colors.info}
								<div class="rounded-lg border-l-4 p-3 {colors.border} {colors.bg}">
									<div class="flex items-center justify-between">
										<span class="text-xs font-bold uppercase {colors.text}">
											{entry.inject?.severity ?? 'info'}
										</span>
										<span class="text-[10px] text-gray-500 dark:text-gray-400">
											{entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString() : ''}
										</span>
									</div>
									<h4 class="font-semibold text-sm mt-1">{entry.inject?.title ?? 'Inject'}</h4>
									{#if entry.inject?.content}
										<p class="text-xs mt-1 whitespace-pre-wrap text-gray-700 dark:text-gray-300">{entry.inject.content}</p>
									{/if}
								</div>
							{/each}
						</div>
					{/if}
				</div>
			</div>

			<!-- Footer -->
			<div class="border-t border-gray-200 dark:border-gray-700 px-4 py-2">
				<button
					class="w-full rounded bg-purple-600 px-3 py-1.5 text-sm text-white hover:bg-purple-700"
					onclick={refresh}
				>Refresh</button>
			</div>
		</div>
	</div>
{/if}
