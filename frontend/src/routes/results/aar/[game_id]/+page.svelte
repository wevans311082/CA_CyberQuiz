<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->
<script lang="ts">
	import type { PageData } from './$types';
	import { fade } from 'svelte/transition';

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();

	const aar = data.aar;

	// Tabs
	type Tab = 'summary' | 'scores' | 'decisions' | 'timeline' | 'badges';
	let active_tab = $state<Tab>('summary');

	// Replay state
	let replay_step = $state(-1); // -1 = show all, 0..n = step through
	const timeline: Array<{ question_index: number; score: number; timestamp?: string }> =
		aar?.scores?.company_score_timeline ?? [];

	const replay_active = $derived(replay_step >= 0);

	const replay_visible_score = $derived.by(() => {
		if (!replay_active || timeline.length === 0) return aar?.scores?.company_score ?? 0;
		const entry = timeline[Math.min(replay_step, timeline.length - 1)];
		return entry?.score ?? 0;
	});

	// Sorted players by score
	const sorted_players = $derived.by(() => {
		const scores = aar?.scores?.players ?? {};
		return Object.entries(scores)
			.map(([name, score]) => ({ name, score: Number(score) }))
			.sort((a, b) => b.score - a.score);
	});

	const max_score = $derived(sorted_players.length ? sorted_players[0].score : 1);

	// Badge colors
	const badge_color: Record<string, string> = {
		'Perfect Score': 'bg-yellow-400/20 text-yellow-300 border-yellow-400/40',
		'Top Player': 'bg-[#B07156]/20 text-[#B07156] border-[#B07156]/40',
		'Fastest Answer': 'bg-teal-400/20 text-teal-300 border-teal-400/40',
	};

	function fmt_date(iso: string | undefined) {
		if (!iso) return '';
		return new Date(iso).toLocaleString();
	}
</script>

{#if !aar}
	<div class="flex min-h-screen items-center justify-center text-slate-400">
		<p>{data.error ?? 'Report unavailable.'}</p>
	</div>
{:else}
<div class="min-h-screen bg-[#0a0f1e] text-white">
	<!-- Header -->
	<div class="border-b border-white/10 bg-[#0f172a]/80 px-6 py-5 backdrop-blur-xl">
		<div class="mx-auto max-w-5xl">
			<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80">After-Action Report</p>
			<h1 class="mt-1 text-2xl font-bold">{aar.metadata.title}</h1>
			<div class="mt-1 flex flex-wrap items-center gap-4 text-sm text-slate-400">
				<span>{fmt_date(aar.metadata.timestamp)}</span>
				<span>{aar.metadata.player_count} players</span>
				{#if aar.metadata.scenario_type}
					<span class="rounded-full border border-teal-400/30 px-2 py-0.5 text-xs text-teal-300">
						{aar.metadata.scenario_type}
					</span>
				{/if}
				{#if aar.scores.company_score != null}
					<span class="rounded-full border border-[#B07156]/30 px-2 py-0.5 text-xs text-[#B07156]">
						Company Score: {aar.scores.company_score}
					</span>
				{/if}
			</div>
			<div class="mt-4 flex flex-wrap items-center gap-2">
				<a
					href="/results/{aar.metadata.game_id}"
					class="rounded-full border border-white/15 px-4 py-1.5 text-xs font-semibold hover:bg-white/5 transition-colors"
				>â† Back to Results</a>
				<a
					href="/api/v1/results/aar/{aar.metadata.game_id}"
					download="aar-{aar.metadata.game_id}.json"
					class="rounded-full border border-white/15 px-4 py-1.5 text-xs font-semibold hover:bg-white/5 transition-colors"
				>Download JSON</a>
				<a
					href="/api/v1/results/export-csv/{aar.metadata.game_id}"
					download
					class="rounded-full border border-white/15 px-4 py-1.5 text-xs font-semibold hover:bg-white/5 transition-colors"
				>Download CSV</a>
			</div>
		</div>
	</div>

	<!-- Tab bar -->
	<div class="border-b border-white/10 bg-[#0f172a]/60 px-6">
		<div class="mx-auto max-w-5xl flex gap-1">
			{#each ([['summary','Summary'],['scores','Scores'],['decisions','Decisions'],['timeline','Timeline'],['badges','Badges']] as const) as [tab, label]}
				<button
					onclick={() => { active_tab = tab; }}
					class="{active_tab === tab ? 'border-b-2 border-[#B07156] text-white' : 'text-slate-400 hover:text-slate-200'} px-4 py-3 text-sm font-medium transition-colors"
				>{label}</button>
			{/each}
		</div>
	</div>

	<!-- Tab content -->
	<div class="mx-auto max-w-5xl px-6 py-8">

		<!-- SUMMARY TAB -->
		{#if active_tab === 'summary'}
		<div in:fade={{ duration: 150 }}>
			<div class="grid gap-4 sm:grid-cols-3">
				<div class="rounded-[1.25rem] border border-white/10 bg-white/4 p-5">
					<p class="text-xs uppercase tracking-widest text-slate-400">Players</p>
					<p class="mt-1 text-3xl font-bold">{aar.metadata.player_count}</p>
				</div>
				<div class="rounded-[1.25rem] border border-white/10 bg-white/4 p-5">
					<p class="text-xs uppercase tracking-widest text-slate-400">Questions</p>
					<p class="mt-1 text-3xl font-bold">{aar.questions?.length ?? 'â€”'}</p>
				</div>
				<div class="rounded-[1.25rem] border border-white/10 bg-white/4 p-5">
					<p class="text-xs uppercase tracking-widest text-slate-400">Company Score</p>
					<p class="mt-1 text-3xl font-bold text-[#B07156]">{aar.scores.company_score ?? 'â€”'}</p>
				</div>
			</div>

			{#if aar.metadata.note}
				<div class="mt-6 rounded-xl border border-white/10 bg-white/4 p-4">
					<p class="text-xs uppercase tracking-widest text-slate-400 mb-1">Facilitator Note</p>
					<p class="text-sm text-slate-200 whitespace-pre-wrap">{aar.metadata.note}</p>
				</div>
			{/if}

			{#if aar.branch_path?.length}
				<div class="mt-6">
					<p class="text-xs uppercase tracking-widest text-slate-400 mb-2">Branch Path Taken</p>
					<div class="flex flex-wrap gap-2">
						{#each aar.branch_path as step, i}
							<span class="rounded-full border border-white/15 px-3 py-1 text-xs">{i + 1}. {step}</span>
						{/each}
					</div>
				</div>
			{/if}

			{#if aar.player_roles && Object.keys(aar.player_roles).length}
				<div class="mt-6">
					<p class="text-xs uppercase tracking-widest text-slate-400 mb-2">Player Roles</p>
					<div class="flex flex-wrap gap-2">
						{#each Object.entries(aar.player_roles) as [player, role]}
							<span class="rounded-full border border-teal-400/30 bg-teal-400/10 px-3 py-1 text-xs text-teal-300">
								{player}: {role}
							</span>
						{/each}
					</div>
				</div>
			{/if}
		</div>

		<!-- SCORES TAB -->
		{:else if active_tab === 'scores'}
		<div in:fade={{ duration: 150 }}>
			<div class="space-y-3">
				{#each sorted_players as { name, score }, i}
					<div class="rounded-xl border border-white/10 bg-white/4 px-4 py-3">
						<div class="mb-2 flex items-center justify-between">
							<span class="flex items-center gap-2">
								<span class="text-sm font-bold {i === 0 ? 'text-yellow-400' : i === 1 ? 'text-slate-300' : i === 2 ? 'text-amber-600' : 'text-slate-400'}">#{i + 1}</span>
								<span class="text-sm text-slate-200">{name}</span>
								{#if aar.player_roles?.[name]}
									<span class="rounded-full border border-teal-400/30 px-2 py-0.5 text-[10px] text-teal-300">{aar.player_roles[name]}</span>
								{/if}
							</span>
							<span class="text-sm font-semibold text-[#B07156]">{score}</span>
						</div>
						<div class="h-2 w-full overflow-hidden rounded-full bg-white/10">
							<div
								class="h-full rounded-full bg-[#B07156] transition-all"
								style="width: {max_score > 0 ? Math.round((score / max_score) * 100) : 0}%"
							></div>
						</div>
						{#if aar.achievements?.[name]?.length}
							<div class="mt-2 flex flex-wrap gap-1">
								{#each aar.achievements[name] as badge}
									<span class="rounded-full border px-2 py-0.5 text-[10px] font-semibold {badge_color[badge] ?? 'bg-slate-700 text-slate-300 border-slate-600'}">
										{badge}
									</span>
								{/each}
							</div>
						{/if}
					</div>
				{/each}
			</div>
		</div>

		<!-- DECISIONS TAB -->
		{:else if active_tab === 'decisions'}
		<div in:fade={{ duration: 150 }}>
			{#if !aar.decision_log?.length}
				<p class="text-center text-slate-400 mt-12">No decision log recorded for this session.</p>
			{:else}
				<div class="overflow-x-auto">
					<table class="w-full text-sm">
						<thead>
							<tr class="border-b border-white/10 text-xs uppercase tracking-wider text-slate-400">
								<th class="py-2 px-3 text-left">Q#</th>
								<th class="py-2 px-3 text-left">Question</th>
								<th class="py-2 px-3 text-left">Winning Answer</th>
								<th class="py-2 px-3 text-left">Rationale</th>
								<th class="py-2 px-3 text-left">Time</th>
							</tr>
						</thead>
						<tbody>
							{#each aar.decision_log as entry, i}
								<tr class="border-b border-white/5 hover:bg-white/3">
									<td class="py-2.5 px-3 text-slate-400">{(entry.question_index ?? i) + 1}</td>
									<td class="py-2.5 px-3 text-slate-200 max-w-[18rem]">
										<span class="line-clamp-2">{entry.question ?? entry.winning_answer ?? 'â€”'}</span>
									</td>
									<td class="py-2.5 px-3 text-slate-300">{entry.winning_answer ?? entry.answer ?? 'â€”'}</td>
									<td class="py-2.5 px-3 text-slate-400 max-w-[16rem]">
										<span class="line-clamp-2 italic">{entry.rationale ?? entry.decision_rationale ?? 'â€”'}</span>
									</td>
									<td class="py-2.5 px-3 text-slate-500 whitespace-nowrap text-xs">{fmt_date(entry.timestamp)}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>

		<!-- TIMELINE TAB -->
		{:else if active_tab === 'timeline'}
		<div in:fade={{ duration: 150 }}>
			{#if !timeline.length}
				<p class="text-center text-slate-400 mt-12">No score timeline recorded for this session.</p>
			{:else}
				<div class="mb-6 flex items-center justify-between">
					<p class="text-sm text-slate-400">Company score progression â€” {timeline.length} checkpoint{timeline.length !== 1 ? 's' : ''}</p>
					<div class="flex items-center gap-2">
						{#if replay_active}
							<span class="text-xs text-slate-400">Step {replay_step + 1} / {timeline.length}</span>
							<button
								onclick={() => { replay_step = Math.max(0, replay_step - 1); }}
								disabled={replay_step <= 0}
								class="rounded-full border border-white/15 px-3 py-1 text-xs disabled:opacity-30 hover:bg-white/5"
							>â† Prev</button>
							<button
								onclick={() => {
									if (replay_step < timeline.length - 1) { replay_step++; }
									else { replay_step = -1; }
								}}
								class="rounded-full border border-white/15 px-3 py-1 text-xs hover:bg-white/5"
							>{replay_step < timeline.length - 1 ? 'Next â†’' : 'Done'}</button>
						{:else}
							<button
								onclick={() => { replay_step = 0; }}
								class="rounded-full bg-[#B07156] px-4 py-1.5 text-xs font-semibold text-slate-950 hover:bg-[#c07d62]"
							>â–¶ Replay</button>
						{/if}
					</div>
				</div>
				<!-- Score gauge -->
				{#if replay_active}
					<div class="mb-6 rounded-[1.25rem] border border-white/10 bg-white/4 p-6 text-center">
						<p class="text-xs uppercase tracking-widest text-slate-400">Company Score at Q{(timeline[replay_step]?.question_index ?? replay_step) + 1}</p>
						<p class="mt-2 text-5xl font-bold text-[#B07156]">{replay_visible_score}</p>
					</div>
				{/if}
				<!-- Bar chart -->
				<div class="flex items-end gap-1" style="height: 180px;">
					{#each timeline as entry, i}
						{@const max_tl = Math.max(...timeline.map(e => e.score), 1)}
						{@const pct = Math.round((entry.score / max_tl) * 100)}
						{@const is_active = !replay_active || i === replay_step}
						<div
							class="relative flex-1 rounded-t-sm transition-all duration-300 {is_active ? 'bg-[#B07156]' : 'bg-white/10'}"
							style="height: {pct}%"
							title="Q{entry.question_index + 1}: {entry.score}"
						>
							{#if is_active}
								<span class="absolute -top-5 left-1/2 -translate-x-1/2 text-[9px] text-slate-300 whitespace-nowrap">{entry.score}</span>
							{/if}
						</div>
					{/each}
				</div>
				<div class="mt-1 flex gap-1">
					{#each timeline as entry, i}
						<div class="flex-1 text-center text-[9px] text-slate-500">Q{entry.question_index + 1}</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- BADGES TAB -->
		{:else if active_tab === 'badges'}
		<div in:fade={{ duration: 150 }}>
			{#if Object.keys(aar.achievements ?? {}).length === 0}
				<p class="text-center text-slate-400 mt-12">No badges were earned this session.</p>
			{:else}
				{@const badge_entries = Object.entries(aar.achievements ?? {})}
				<div class="grid gap-4 sm:grid-cols-2">
					{#each badge_entries as [player, badges]}
						<div class="rounded-[1.25rem] border border-white/10 bg-white/4 p-5">
							<p class="mb-3 text-sm font-semibold text-slate-200">{player}</p>
							<div class="flex flex-wrap gap-2">
								{#each badges as badge}
									<span class="rounded-full border px-3 py-1 text-xs font-semibold {badge_color[badge] ?? 'bg-slate-700 text-slate-300 border-slate-600'}">
										{badge}
									</span>
								{/each}
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
                {/if}

                <!-- ANOMALY FLAGS (shown below tabs if any detected) -->
                {#if aar.anomaly_flags && aar.anomaly_flags.length > 0}
                <div class="mt-6 rounded-[1.25rem] border border-yellow-400/30 bg-yellow-400/5 p-5" in:fade={{ duration: 150 }}>
                        <p class="mb-3 text-sm font-semibold text-yellow-300">âš  Score Anomalies Detected</p>
                        <p class="text-xs text-slate-400 mb-4">These flags indicate potentially unusual scoring patterns and may warrant facilitator review. They do not automatically affect scores.</p>
                        <div class="flex flex-col gap-2">
                                {#each aar.anomaly_flags as flag}
                                        <div class="rounded-xl border border-yellow-400/20 bg-yellow-400/10 px-4 py-2.5 flex flex-col gap-0.5">
                                                <div class="flex items-center gap-2">
                                                        <span class="text-xs font-semibold text-yellow-300 uppercase tracking-wide">{flag.type === 'outlier' ? 'Score Outlier' : 'Confidence Mismatch'}</span>
                                                        <span class="text-xs text-slate-400">Q{flag.question_index + 1}</span>
                                                        <span class="ml-auto text-xs font-medium text-slate-300">{flag.player}</span>
                                                </div>
                                                <p class="text-xs text-slate-400">{flag.detail}</p>
                                        </div>
                                {/each}
                        </div>
                </div>
                {/if}

        </div>
</div>
{/if}
