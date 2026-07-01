<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Inject, SituationStatus } from '$lib/quiz_types';

	interface Props {
		title?: string;
		situation_status: SituationStatus | null;
		latest_inject?: Inject | null;
		clock?: string;
	}

	let { title = 'Incident Status', situation_status, latest_inject = null, clock = '' }: Props = $props();

	const severityBar = $derived(
		({
			low: 'from-emerald-600 to-emerald-800',
			medium: 'from-amber-500 to-amber-700',
			high: 'from-orange-500 to-orange-700',
			critical: 'from-red-600 to-red-900'
		})[situation_status?.severity ?? 'low'] ?? 'from-slate-600 to-slate-800'
	);

	const severityGlow = $derived(
		({
			low: 'shadow-emerald-500/20',
			medium: 'shadow-amber-500/25',
			high: 'shadow-orange-500/30',
			critical: 'shadow-red-500/40 animate-pulse'
		})[situation_status?.severity ?? 'low'] ?? ''
	);
</script>

<div class="flex min-h-screen flex-col bg-slate-950 text-white">
	<header class="bg-gradient-to-r {severityBar} px-8 py-6 shadow-2xl {severityGlow}">
		<div class="mx-auto flex max-w-6xl items-center justify-between gap-4">
			<div>
				<p class="text-xs font-semibold uppercase tracking-[0.35em] text-white/70">CyberAsk Situation Board</p>
				<h1 class="mt-1 text-3xl font-bold tracking-tight">{title}</h1>
			</div>
			{#if clock}
				<p class="font-mono text-sm text-white/80">{clock}</p>
			{/if}
		</div>
	</header>

	<main class="mx-auto grid w-full max-w-6xl flex-1 gap-6 px-8 py-8 lg:grid-cols-3">
		<section class="lg:col-span-2 space-y-6">
			{#if situation_status}
				<div class="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
					<div class="flex flex-wrap items-center gap-3">
						<span class="rounded-full bg-white/15 px-4 py-1.5 text-sm font-bold uppercase tracking-wider">
							{situation_status.severity}
						</span>
						<span class="text-lg font-semibold text-cyan-200">{situation_status.phase}</span>
					</div>

					{#if situation_status.summary}
						<p class="mt-5 text-xl leading-relaxed text-slate-100">{situation_status.summary}</p>
					{/if}

					{#if situation_status.affected_systems?.length}
						<div class="mt-5">
							<p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Affected systems</p>
							<div class="mt-2 flex flex-wrap gap-2">
								{#each situation_status.affected_systems as sys}
									<span class="rounded-full border border-purple-400/40 bg-purple-500/20 px-3 py-1 text-sm text-purple-100">{sys}</span>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			{:else}
				<div class="rounded-2xl border border-dashed border-slate-700 p-12 text-center text-slate-500">
					Waiting for facilitator to broadcast incident status…
				</div>
			{/if}

			{#if latest_inject}
				<div class="rounded-2xl border border-orange-500/40 bg-orange-500/10 p-6">
					<p class="text-xs font-semibold uppercase tracking-[0.25em] text-orange-300">Latest inject</p>
					<h2 class="mt-2 text-2xl font-bold text-orange-100">{latest_inject.title}</h2>
					{#if latest_inject.content}
						<p class="mt-3 whitespace-pre-wrap text-lg leading-relaxed text-orange-50/90">{latest_inject.content}</p>
					{/if}
				</div>
			{/if}
		</section>

		<aside class="space-y-4">
			{#if situation_status?.context_notes}
				<div class="rounded-2xl border border-white/10 bg-white/5 p-5">
					<p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Background</p>
					<p class="mt-2 text-sm leading-relaxed text-slate-300 whitespace-pre-wrap">{situation_status.context_notes}</p>
				</div>
			{/if}

			<div class="rounded-2xl border border-cyan-500/30 bg-cyan-500/10 p-5">
				<p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">Facilitator display</p>
				<p class="mt-2 text-sm text-cyan-100/80">
					This board updates live as the facilitator pushes injects and broadcasts situation changes.
				</p>
			</div>
		</aside>
	</main>
</div>