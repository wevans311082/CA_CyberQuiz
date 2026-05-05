<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount } from 'svelte';
	import { getLocalization } from '$lib/i18n';
	import PlayerAvatarChip from '$lib/play/player_avatar_chip.svelte';

	const { t } = getLocalization();

	import { fly } from 'svelte/transition';
	import confetti from 'canvas-confetti';
	interface Props {
		data: any;
		username?: any;
		show_final_results: boolean;
		raw_final_results?: any;
		avatar_map?: Record<string, any>;
	}

	let { data = $bindable(), username, show_final_results, raw_final_results = {}, avatar_map = {} }: Props = $props();

	interface PodiumPlayer {
		username: string;
		points: number;
		correct_answers: number;
		avatar_params?: any;
	}

	const correct_by_user = $derived.by(() => {
		const count_map: Record<string, number> = {};
		for (const key of Object.keys(raw_final_results ?? {})) {
			const question_results = raw_final_results[key] ?? [];
			for (const answer of question_results) {
				if (!answer?.username) {
					continue;
				}
				if (count_map[answer.username] === undefined) {
					count_map[answer.username] = 0;
				}
				if (answer.right) {
					count_map[answer.username] += 1;
				}
			}
		}
		return count_map;
	});

	const podium_players = $derived.by(() => {
		const names = Object.keys(data ?? {});
		const players: PodiumPlayer[] = names.map((name) => ({
			username: name,
			points: parseFloat(data[name]) || 0,
			correct_answers: correct_by_user[name] ?? 0,
			avatar_params: avatar_map[name]
		}));
		players.sort((a, b) => {
			if (b.points !== a.points) {
				return b.points - a.points;
			}
			return b.correct_answers - a.correct_answers;
		});
		return players;
	});

	let top_three = $derived(podium_players.slice(0, 3));
	let rest_players = $derived(podium_players.slice(3));
	let my_rank = $derived(podium_players.findIndex((player) => player.username === username) + 1);
	let reveal_leaderboard = $state(!Boolean(username));

	let canvas: HTMLCanvasElement = $state();
	onMount(() => {
		setTimeout(() => {
			confetti.create(canvas, {
				resize: true,
				useWorker: true
			});
			confetti({ particleCount: 220, spread: 160 });
		}, 600);
	});
</script>

{#if show_final_results}
	<canvas bind:this={canvas}></canvas>
	<div class="mx-auto mt-8 max-w-6xl px-4">
		<h2 class="text-center text-4xl font-semibold">Final Podium</h2>
		{#if username}
			<div class="mt-4 flex justify-center">
				<button class="rounded-full border border-white/15 px-5 py-2 text-sm font-semibold text-white/90 hover:bg-white/6 transition-colors" onclick={() => (reveal_leaderboard = !reveal_leaderboard)}>
					{reveal_leaderboard ? 'Hide Leaderboard' : 'Show Leaderboard'}
				</button>
			</div>
		{/if}

		{#if reveal_leaderboard}
			<div class="mt-8 grid gap-4 sm:grid-cols-3">
				{#each top_three as player, index}
					<div
						in:fly|global={{ y: -120, delay: index * 160 }}
						class="rounded-3xl border border-slate-300/70 bg-white/85 p-4 shadow-xl backdrop-blur dark:border-slate-700 dark:bg-slate-900/75"
					>
						<p class="text-3xl">{index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}</p>
						<p class="mt-2 text-sm font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">#{index + 1}</p>
						<div class="mt-3">
							<PlayerAvatarChip username={player.username} avatar_params={player.avatar_params} />
						</div>
						<p class="mt-3 text-base font-semibold">Points: {player.points}</p>
						<p class="text-sm text-slate-600 dark:text-slate-300">Correct answers: {player.correct_answers}</p>
					</div>
				{/each}
			</div>

			{#if rest_players.length > 0}
				<div class="mt-6 rounded-2xl border border-slate-300/70 bg-white/80 p-4 dark:border-slate-700 dark:bg-slate-900/75">
					<p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Leaderboard</p>
					<div class="mt-3 space-y-2">
						{#each rest_players as player, idx}
							<div class="flex items-center justify-between rounded-xl bg-slate-100/80 px-3 py-2 text-sm dark:bg-slate-800/80">
								<div class="flex items-center gap-2">
									<span class="w-8 text-slate-500">#{idx + 4}</span>
									<span class="font-semibold">{player.username}</span>
								</div>
								<div class="text-right text-xs">
									<p>{player.points} pts</p>
									<p class="text-slate-500">{player.correct_answers} correct</p>
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}
		{/if}
	</div>
	{#if data[username] !== undefined}
		<div class="fixed bottom-0 left-0 flex justify-center w-full mb-6">
			<div class="mx-auto rounded-2xl border-2 border-amber-500 bg-white/90 px-4 py-2 shadow-lg dark:bg-slate-900/90">
				<p class="text-center text-sm">{$t('play_page.your_score', { score: data[username] })}</p>
				<p class="text-center text-sm">{$t('play_page.your_place', { place: my_rank })}</p>
				<p class="text-center text-xs text-slate-600 dark:text-slate-300">
					Correct: {correct_by_user[username] ?? 0}
				</p>
			</div>
		</div>
	{/if}
{/if}
