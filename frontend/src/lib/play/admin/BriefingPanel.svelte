<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';
	import Card from '$lib/ui/Card.svelte';
	import Button from '$lib/ui/Button.svelte';

	interface Props {
		quiz_data: QuizData;
		player_count?: number;
		onstart?: () => void;
		onopenprojector?: () => void;
		start_disabled?: boolean;
	}

	let { quiz_data, player_count = 0, onstart, onopenprojector, start_disabled = false }: Props = $props();

	let expanded = $state(true);

	const facilitator_notes = $derived(
		(quiz_data.questions ?? [])
			.map((q, i) => ({ index: i, notes: q.facilitator_notes?.trim() }))
			.filter((q) => q.notes)
	);

	const roles = $derived(quiz_data.roles ?? []);
	const injects = $derived(quiz_data.injects ?? []);
</script>

<Card variant="glass" padding="lg" class="mx-auto mt-6 max-w-5xl border-cyan-500/20">
	<div class="flex items-start justify-between gap-4">
		<div>
			<p class="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700 dark:text-cyan-300">Pre-session briefing</p>
			<h2 class="mt-1 text-2xl font-semibold text-slate-900 dark:text-white">Facilitator readiness check</h2>
			<p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
				Review scenario context, roles, and available injects before you go live. {player_count} player{player_count === 1 ? '' : 's'} in lobby.
			</p>
		</div>
		<Button variant="ghost" size="sm" onclick={() => (expanded = !expanded)}>
			{expanded ? 'Collapse' : 'Expand'}
		</Button>
	</div>

	{#if expanded}
		<div class="mt-6 grid gap-4 md:grid-cols-2">
			<div class="rounded-xl border border-slate-200/70 bg-slate-50/80 p-4 dark:border-slate-700 dark:bg-slate-900/50">
				<h3 class="text-sm font-semibold text-slate-900 dark:text-white">Exercise overview</h3>
				<p class="mt-2 text-sm text-slate-600 dark:text-slate-300">{@html quiz_data.description || 'No description provided.'}</p>
			</div>

			<div class="rounded-xl border border-slate-200/70 bg-slate-50/80 p-4 dark:border-slate-700 dark:bg-slate-900/50">
				<h3 class="text-sm font-semibold text-slate-900 dark:text-white">Roles ({roles.length})</h3>
				{#if roles.length === 0}
					<p class="mt-2 text-sm italic text-slate-500">No roles configured.</p>
				{:else}
					<ul class="mt-2 space-y-2 text-sm">
						{#each roles as role}
							<li>
								<span class="font-medium text-teal-700 dark:text-cyan-300">{role}</span>
								{#if quiz_data.role_descriptions?.[role]}
									<p class="text-xs text-slate-500 dark:text-slate-400">{quiz_data.role_descriptions[role]}</p>
								{/if}
							</li>
						{/each}
					</ul>
				{/if}
			</div>

			<div class="rounded-xl border border-slate-200/70 bg-slate-50/80 p-4 dark:border-slate-700 dark:bg-slate-900/50">
				<h3 class="text-sm font-semibold text-slate-900 dark:text-white">Pre-defined injects ({injects.length})</h3>
				{#if injects.length === 0}
					<p class="mt-2 text-sm italic text-slate-500">No injects configured — use quick presets during play.</p>
				{:else}
					<ul class="mt-2 space-y-1 text-sm text-slate-600 dark:text-slate-300">
						{#each injects as inj}
							<li><span class="font-medium">{inj.title}</span> <span class="text-xs uppercase text-slate-400">({inj.severity})</span></li>
						{/each}
					</ul>
				{/if}
			</div>

			<div class="rounded-xl border border-slate-200/70 bg-slate-50/80 p-4 dark:border-slate-700 dark:bg-slate-900/50">
				<h3 class="text-sm font-semibold text-slate-900 dark:text-white">Facilitator notes</h3>
				{#if facilitator_notes.length === 0}
					<p class="mt-2 text-sm italic text-slate-500">Add per-question facilitator notes in the editor for in-session guidance.</p>
				{:else}
					<ul class="mt-2 max-h-40 space-y-2 overflow-y-auto text-sm">
						{#each facilitator_notes as item}
							<li class="rounded-lg bg-white/60 p-2 dark:bg-slate-800/60">
								<span class="text-xs font-semibold text-slate-400">Q{item.index + 1}</span>
								<p class="mt-0.5 whitespace-pre-wrap text-slate-700 dark:text-slate-200">{item.notes}</p>
							</li>
						{/each}
					</ul>
				{/if}
			</div>
		</div>

		<div class="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-slate-200/70 pt-4 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				Tip: open the projector display on a second screen for the audience view.
			</p>
			<div class="flex flex-wrap gap-2">
				{#if onopenprojector}
					<Button variant="secondary" onclick={onopenprojector}>Open projector</Button>
				{/if}
				{#if onstart}
					<Button onclick={onstart} disabled={start_disabled}>Start exercise</Button>
				{/if}
			</div>
		</div>
	{/if}
</Card>