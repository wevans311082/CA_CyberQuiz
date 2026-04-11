<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import JoinGame from '$lib/play/join.svelte';
	import { navbarVisible } from '$lib/stores.svelte.ts';

	navbarVisible.visible = false;

	let game_pin = $state('');
	let game_mode = $state();
	let username = $state('');
</script>

<svelte:head>
	<title>CyberAsk Quiz</title>
	<meta name="description" content="Join your CyberAsk live quiz with a game PIN." />
	<meta property="og:url" content="https://quiz.cyberask.co.uk/" />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="CyberAsk Quiz" />
	<meta property="og:description" content="Enter your game PIN to join the live session." />
	<meta name="twitter:card" content="summary_large_image" />
	<meta property="twitter:domain" content="quiz.cyberask.co.uk" />
	<meta property="twitter:url" content="https://quiz.cyberask.co.uk/" />
	<meta name="twitter:title" content="CyberAsk Quiz" />
	<meta name="twitter:description" content="Enter your game PIN to join the live session." />
</svelte:head>

<div class="relative min-h-screen overflow-hidden">
	<div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.18),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(13,148,136,0.22),transparent_30%)]"></div>
	<div class="relative z-10 mx-auto flex min-h-screen max-w-6xl flex-col justify-center px-4 py-8 lg:px-6">
		<div class="mb-6 flex items-start justify-between gap-4">
			<div class="max-w-2xl">
				<p class="mb-3 text-xs font-semibold uppercase tracking-[0.32em] text-teal-700 dark:text-cyan-300">
					CyberAsk Hosted Quiz
				</p>
				<h1 class="text-4xl font-semibold tracking-tight text-slate-950 dark:text-white sm:text-6xl">
					Join the live session.
				</h1>
				<p class="mt-4 max-w-xl text-base leading-7 text-slate-600 dark:text-slate-300 sm:text-lg">
					Enter the six-digit game PIN shown by your host to access the quiz.
				</p>
			</div>
			<a
				href="/account/login"
				class="rounded-full border border-slate-300/80 bg-white/80 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-700 shadow-sm transition hover:border-teal-600 hover:text-teal-700 dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-200 dark:hover:border-cyan-400 dark:hover:text-cyan-300"
			>
				Admin Login
			</a>
		</div>
		<div class="rounded-[2rem] border border-white/70 bg-white/45 shadow-[0_30px_100px_rgba(15,23,42,0.16)] backdrop-blur dark:border-slate-700/80 dark:bg-slate-900/35">
			<JoinGame bind:game_pin bind:game_mode bind:username />
		</div>
	</div>
</div>
