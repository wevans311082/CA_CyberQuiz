<!-- SPDX-License-Identifier: MPL-2.0 -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import confetti from 'canvas-confetti';
	import { getLocalization } from '$lib/i18n';
	const { t } = getLocalization();
	interface Props { data: any; username?: string; show_final_results: boolean; raw_final_results?: any; avatar_map?: Record<string, any>; }
	let { data = $bindable(), username, show_final_results, raw_final_results = {}, avatar_map = {} }: Props = $props();
	interface Player { username: string; points: number; correct: number; avatar?: any; }
	const correct_by_user = $derived.by(() => {
		const counts: Record<string, number> = {};
		for (const key of Object.keys(raw_final_results ?? {})) for (const answer of (Array.isArray(raw_final_results[key]) ? raw_final_results[key] : [])) {
			if (!answer?.username) continue;
			counts[answer.username] = counts[answer.username] ?? 0;
			if (answer.right === true || answer.right === 'true') counts[answer.username]++;
		}
		return counts;
	});
	const players = $derived.by(() => {
		const scores = data && typeof data === 'object' && !Array.isArray(data) ? data : {};
		const names = new Set([...Object.keys(scores), ...Object.keys(avatar_map ?? {}), ...Object.keys(correct_by_user)]);
		return [...names].filter(Boolean).map((name): Player => ({ username: name, points: Number(scores[name]) || 0, correct: correct_by_user[name] ?? 0, avatar: avatar_map?.[name] })).sort((a, b) => b.points - a.points || b.correct - a.correct || a.username.localeCompare(b.username));
	});
	const first = $derived(players[0]);
	const second = $derived(players[1]);
	const third = $derived(players[2]);
	const rest = $derived(players.slice(3));
	const my_rank = $derived(players.findIndex((player) => player.username === username) + 1);
	let reveal = $state(false);
	$effect(() => { reveal = !Boolean(username); });
	let canvas: HTMLCanvasElement = $state();
	const avatar_url = (params: any) => {
		const defaults = { skin_color: 0, hair_color: 0, facial_hair_type: 0, facial_hair_color: 0, top_type: 0, hat_color: 0, mouth_type: 0, eyebrow_type: 0, nose_type: 0, accessories_type: 0, clothe_type: 0, clothe_color: 0, clothe_graphic_type: 0 };
		return `/api/v1/avatar/custom?${new URLSearchParams(Object.fromEntries(Object.entries({ ...defaults, ...(params ?? {}) }).map(([key, value]) => [key, String(value)]))).toString()}`;
	};
	const initials = (name: string) => (name || '?').slice(0, 2).toUpperCase();
	onMount(() => {
		const timer = setTimeout(() => { if (canvas) confetti.create(canvas, { resize: true, useWorker: true })({ particleCount: 180, spread: 150, origin: { y: 0.55 }, colors: ['#fbbf24', '#38bdf8', '#14b8a6', '#f8fafc'] }); }, 850);
		return () => clearTimeout(timer);
	});
</script>

{#if show_final_results}
	<canvas bind:this={canvas} class="pointer-events-none fixed inset-0 z-20 h-full w-full"></canvas>
	<div class="podium-shell mx-auto mt-6 max-w-6xl px-4 pb-32 text-slate-900">
		<div class="relative overflow-hidden rounded-[2rem] border border-slate-200/80 bg-gradient-to-br from-white via-sky-50 to-teal-50 px-5 py-8 shadow-2xl dark:border-slate-700 dark:from-slate-900 dark:via-slate-900 dark:to-slate-800 sm:px-10 sm:py-10">
			<div class="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-amber-300/20 blur-3xl"></div><div class="absolute -left-24 bottom-0 h-64 w-64 rounded-full bg-cyan-300/20 blur-3xl"></div>
			<div class="relative text-center"><p class="text-xs font-bold uppercase tracking-[0.35em] text-teal-600 dark:text-teal-300">Exercise complete</p><h2 class="mt-2 text-4xl font-black tracking-tight sm:text-5xl">Final podium</h2><p class="mx-auto mt-3 max-w-xl text-sm text-slate-600 dark:text-slate-300">Celebrating the teams who made the strongest decisions under pressure.</p></div>
			{#if players.length === 0}<div class="relative mt-12 rounded-2xl border border-dashed border-slate-300 p-8 text-center text-slate-500 dark:border-slate-600">No scored players were returned for this exercise.</div>{:else}<div class="relative mx-auto mt-14 flex max-w-4xl items-end justify-center gap-2 sm:gap-5">
				{#if second}<div in:fly={{ y: 100, duration: 700, delay: 180 }} class="podium-entry order-1 w-[31%]"><div class="podium-person podium-silver">{@render Avatar(second)}<p class="podium-medal">2</p><p class="podium-name">{second.username}</p><p class="podium-score">{second.points} <span>pts</span></p></div><div class="podium-block podium-block-silver"><span>SECOND</span></div></div>{/if}
				{#if first}<div in:fly={{ y: 150, duration: 850, delay: 360 }} class="podium-entry order-2 z-10 w-[36%]"><div class="podium-person podium-gold"><div class="crown">✦</div>{@render Avatar(first, true)}<p class="podium-medal">1</p><p class="podium-name text-lg">{first.username}</p><p class="podium-score">{first.points} <span>pts</span></p></div><div class="podium-block podium-block-gold"><span>CHAMPION</span></div></div>{/if}
				{#if third}<div in:fly={{ y: 80, duration: 700, delay: 40 }} class="podium-entry order-3 w-[31%]"><div class="podium-person podium-bronze">{@render Avatar(third)}<p class="podium-medal">3</p><p class="podium-name">{third.username}</p><p class="podium-score">{third.points} <span>pts</span></p></div><div class="podium-block podium-block-bronze"><span>THIRD</span></div></div>{/if}
			</div>{/if}
			{#if username}<div class="relative mt-10 flex justify-center"><button class="rounded-full border border-slate-300 bg-white/80 px-5 py-2 text-sm font-bold shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-600 dark:bg-slate-800" onclick={() => (reveal = !reveal)}>{reveal ? 'Hide leaderboard' : 'Show full leaderboard'}</button></div>{/if}
		</div>
		{#if reveal && rest.length > 0}<div class="mt-6 rounded-2xl border border-slate-200 bg-white p-4 shadow-lg dark:border-slate-700 dark:bg-slate-900"><p class="px-2 text-xs font-bold uppercase tracking-[0.25em] text-slate-500">Leaderboard</p><div class="mt-3 space-y-2">{#each rest as player, index}<div class="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-3 dark:bg-slate-800"><div class="flex items-center gap-3"><span class="w-7 text-sm font-bold text-slate-500">#{index + 4}</span><span class="font-semibold">{player.username}</span></div><span class="text-sm font-bold">{player.points} pts</span></div>{/each}</div></div>{/if}
	</div>
	{#if username && data?.[username] !== undefined}<div class="fixed bottom-5 left-1/2 z-30 -translate-x-1/2 rounded-2xl border-2 border-amber-400 bg-white/95 px-5 py-3 text-center shadow-2xl dark:bg-slate-900/95"><p class="text-sm font-bold">{$t('play_page.your_score', { score: data[username] })}</p><p class="text-sm">{$t('play_page.your_place', { place: my_rank })}</p><p class="text-xs text-slate-500">Correct: {correct_by_user[username] ?? 0}</p></div>{/if}
{/if}

{#snippet Avatar(player: Player, large = false)}<div class:podium-avatar-large={large} class="podium-avatar"><img src={avatar_url(player.avatar)} alt={`${player.username} avatar`} onerror={(event) => ((event.currentTarget as HTMLImageElement).style.display = 'none')} /><span>{initials(player.username)}</span></div>{/snippet}

<style>
	.podium-entry { min-width: 0; text-align: center; }.podium-person { position: relative; border-radius: 1.5rem 1.5rem 0 0; padding: 1.2rem 0.35rem 0.9rem; color: #0f172a; }.podium-gold { background: linear-gradient(145deg, #fff7bf, #fbbf24); box-shadow: 0 0 45px rgb(251 191 36 / 35%); }.podium-silver { background: linear-gradient(145deg, #f8fafc, #cbd5e1); }.podium-bronze { background: linear-gradient(145deg, #fed7aa, #c27845); }.podium-avatar { position: relative; width: 4.4rem; height: 4.4rem; margin: -3.5rem auto 0.45rem; overflow: hidden; border: 4px solid rgb(255 255 255 / 90%); border-radius: 999px; background: linear-gradient(135deg, #14b8a6, #0891b2); color: white; font-size: 1rem; font-weight: 800; line-height: 4rem; text-align: center; box-shadow: 0 7px 18px rgb(15 23 42 / 22%); }.podium-avatar-large { width: 5.6rem; height: 5.6rem; margin-top: -4.7rem; font-size: 1.25rem; line-height: 5rem; border-color: #fff7bf; }.podium-avatar img { position: absolute; inset: 0; z-index: 1; width: 100%; height: 100%; object-fit: cover; }.crown { position: absolute; top: -1.15rem; left: 50%; z-index: 2; color: #b45309; font-size: 1.5rem; transform: translateX(-50%); }.podium-medal { margin: 0.2rem 0 0; font-size: 0.75rem; font-weight: 900; letter-spacing: 0.12em; }.podium-name { overflow: hidden; margin-top: 0.2rem; text-overflow: ellipsis; white-space: nowrap; font-size: clamp(0.75rem, 2vw, 1rem); font-weight: 900; }.podium-score { margin-top: 0.25rem; font-size: clamp(1rem, 3vw, 1.45rem); font-weight: 900; }.podium-score span { font-size: 0.62em; font-weight: 700; opacity: 0.7; }.podium-block { display: flex; min-height: 5.2rem; align-items: center; justify-content: center; border-radius: 0 0 0.8rem 0.8rem; color: rgb(15 23 42 / 65%); font-size: clamp(0.5rem, 1.7vw, 0.72rem); font-weight: 900; letter-spacing: 0.12em; }.podium-block-gold { min-height: 8rem; background: linear-gradient(135deg, #f59e0b, #d97706); }.podium-block-silver { min-height: 6.3rem; background: linear-gradient(135deg, #cbd5e1, #94a3b8); }.podium-block-bronze { min-height: 4.7rem; background: linear-gradient(135deg, #c27845, #92400e); } @media (max-width: 420px) { .podium-avatar { width: 3.5rem; height: 3.5rem; margin-top: -2.8rem; line-height: 3.1rem; }.podium-avatar-large { width: 4.3rem; height: 4.3rem; margin-top: -3.5rem; line-height: 3.8rem; } }
</style>
