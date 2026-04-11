<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import MediaComponent from '$lib/editor/MediaComponent.svelte';

	interface Props {
		title: string;
		description: string;
		cover_image: string | undefined;
		players?: string[];
		player_count?: number;
		started?: boolean;
	}

	let {
		title,
		description,
		cover_image,
		players = [],
		player_count = 0,
		started = false
	}: Props = $props();

	const sceneElements = Array.from({ length: 14 }, (_, index) => ({
		id: index,
		size: 80 + ((index * 19) % 120),
		left: (index * 9) % 100,
		delay: `${(index % 5) * 0.7}s`,
		duration: `${12 + (index % 6) * 2}s`
	}));
</script>

<div class="relative flex min-h-screen w-screen items-center justify-center overflow-hidden px-6 py-10 text-slate-950 dark:text-white">
	<div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.14),transparent_30%),radial-gradient(circle_at_bottom_right,rgba(20,184,166,0.18),transparent_30%),linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.02))]"></div>
	{#each sceneElements as element}
		<div
			class="lobby-orb absolute rounded-full"
			style="width: {element.size}px; height: {element.size}px; left: {element.left}%; animation-delay: {element.delay}; animation-duration: {element.duration};"
		></div>
	{/each}

	<div class="relative z-10 grid w-full max-w-6xl gap-8 lg:grid-cols-[1.4fr,0.9fr]">
		<section class="rounded-[2rem] border border-white/60 bg-white/50 p-8 shadow-[0_24px_80px_rgba(15,23,42,0.16)] backdrop-blur dark:border-slate-700/80 dark:bg-slate-900/45">
			<p class="text-sm font-semibold uppercase tracking-[0.34em] text-teal-700 dark:text-cyan-300">
				{started ? 'Quiz starting' : 'Lobby'}
			</p>
			<h1 class="mt-4 text-4xl font-semibold tracking-tight sm:text-6xl">{@html title}</h1>
			<p class="mt-5 max-w-2xl text-lg leading-8 text-slate-700 dark:text-slate-300">
				{#if started}
					The host has started the session. Your first question will appear here in a moment.
				{:else}
					Waiting for the quiz to start. Stay on this screen while the host brings everyone in.
				{/if}
			</p>
			{#if description}
				<p class="mt-4 text-base leading-7 text-slate-600 dark:text-slate-400">{@html description}</p>
			{/if}
			<div class="mt-8 inline-flex items-center gap-3 rounded-full border border-teal-700/20 bg-teal-600/10 px-5 py-3 text-sm font-medium text-teal-900 dark:border-cyan-300/20 dark:bg-cyan-400/10 dark:text-cyan-100">
				<span class="h-2.5 w-2.5 rounded-full bg-teal-600 dark:bg-cyan-300"></span>
				{#if started}
					Waiting for the first question
				{:else}
					Waiting for the quiz to start
				{/if}
			</div>
			{#if cover_image}
				<div class="mt-8 overflow-hidden rounded-[1.5rem] border border-white/70 bg-white/70 p-3 dark:border-slate-700 dark:bg-slate-950/60">
					<MediaComponent src={cover_image} css_classes="max-h-[28vh] w-full object-contain" />
				</div>
			{/if}
		</section>

		<aside class="rounded-[2rem] border border-white/60 bg-white/50 p-6 shadow-[0_24px_80px_rgba(15,23,42,0.16)] backdrop-blur dark:border-slate-700/80 dark:bg-slate-900/45">
			<div class="flex items-center justify-between gap-4 border-b border-slate-200/70 pb-4 dark:border-slate-700/70">
				<div>
					<p class="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">Players</p>
					<h2 class="mt-2 text-3xl font-semibold">{player_count}</h2>
				</div>
				<div class="rounded-full bg-slate-950 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-white dark:bg-white dark:text-slate-950">
					Live Lobby
				</div>
			</div>
			{#if players.length > 0}
				<div class="mt-5 grid max-h-[45vh] gap-3 overflow-auto pr-2">
					{#each players as player}
						<div class="rounded-2xl border border-slate-200/70 bg-white/80 px-4 py-3 text-base font-medium text-slate-800 shadow-sm dark:border-slate-700 dark:bg-slate-950/70 dark:text-slate-100">
							{player}
						</div>
					{/each}
				</div>
			{:else}
				<p class="mt-5 text-sm leading-6 text-slate-600 dark:text-slate-400">No one else is in the lobby yet.</p>
			{/if}
		</aside>
	</div>
</div>

<style>
	.lobby-orb {
		top: -8%;
		background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.95), rgba(45, 212, 191, 0.18));
		filter: blur(1px);
		opacity: 0.7;
		animation-name: floatLobbyOrb;
		animation-iteration-count: infinite;
		animation-timing-function: ease-in-out;
	}

	@keyframes floatLobbyOrb {
		0% {
			transform: translate3d(0, 0, 0) scale(0.96);
			opacity: 0.28;
		}
		25% {
			transform: translate3d(18px, 22vh, 0) scale(1.04);
			opacity: 0.58;
		}
		50% {
			transform: translate3d(-12px, 48vh, 0) scale(1);
			opacity: 0.42;
		}
		75% {
			transform: translate3d(14px, 71vh, 0) scale(1.08);
			opacity: 0.5;
		}
		100% {
			transform: translate3d(-8px, 108vh, 0) scale(0.94);
			opacity: 0.14;
		}
	}
</style>
