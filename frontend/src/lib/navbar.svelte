<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { signedIn, pathname } from '$lib/stores';
	import { browser } from '$app/environment';
	import { beforeNavigate } from '$app/navigation';
	import { draw, slide } from 'svelte/transition';

	let menuIsClosed = $state(true);
	const toggleMenu = () => {
		menuIsClosed = !menuIsClosed;
	};

	beforeNavigate(() => {
		menuIsClosed = true;
	});

	let darkMode = $state(false);
	if (browser) {
		darkMode =
			localStorage.theme === 'dark' ||
			(!('theme' in localStorage) &&
				window.matchMedia('(prefers-color-scheme: dark)').matches);
	}

	const switchDarkMode = () => {
		!darkMode ? localStorage.setItem('theme', 'dark') : localStorage.setItem('theme', 'light');
		window.location.reload();
	};
</script>

<nav class="fixed top-0 z-30 w-screen border-b border-slate-200/70 bg-white/78 px-4 py-3 shadow-sm backdrop-blur-xl dark:border-slate-700/70 dark:bg-slate-950/70">
	<div class="hidden items-center justify-between lg:flex">
		<div class="flex items-center gap-2">
			<a
				href="/"
				class="px-3 text-lg font-semibold uppercase tracking-[0.28em] text-slate-900 transition hover:text-teal-700 dark:text-white dark:hover:text-cyan-300"
			>
				CyberAsk Quiz
			</a>
			<a class="btn-nav" href="/">Enter PIN</a>
			{#if $signedIn}
				<a class="btn-nav" href="/dashboard">Dashboard</a>
			{/if}
		</div>
		<div class="flex items-center gap-2">
			{#if $signedIn}
				<a class="btn-nav" href="/api/v1/users/logout">Logout</a>
			{:else}
				<a class="btn-nav" href="/account/login?returnTo={$pathname}">Admin Login</a>
			{/if}

			<div class="flex items-center justify-center rounded-full border border-slate-200/80 bg-white/70 p-2 dark:border-slate-700 dark:bg-slate-900/70">
				{#if darkMode}
					<button
						onclick={() => {
							switchDarkMode();
						}}
						aria-label="Activate light mode"
					>
						<svg
							class="h-5 w-5 text-slate-900 dark:text-white"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
							/>
						</svg>
					</button>
				{:else}
					<button
						onclick={() => {
							switchDarkMode();
						}}
						aria-label="Activate dark mode"
					>
						<svg
							class="h-5 w-5 text-slate-900"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
							/>
						</svg>
					</button>
				{/if}
			</div>
		</div>
	</div>

	<div class="lg:hidden">
		<div class="flex items-center justify-between">
			<a
				href="/"
				class="px-1 text-sm font-semibold uppercase tracking-[0.26em] text-slate-900 dark:text-white"
			>
				CyberAsk Quiz
			</a>
			<a class="btn-nav" href="/">PIN</a>

			<div class="flex items-center">
				{#if darkMode}
					<button
						class="px-3"
						onclick={() => {
							switchDarkMode();
						}}
						aria-label="Activate light mode"
					>
						<svg
							class="h-6 w-6 text-black"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
							/>
						</svg>
					</button>
				{:else}
					<button
						class="px-3"
						onclick={() => {
							switchDarkMode();
						}}
						aria-label="Activate dark mode"
					>
						<svg
							class="h-6 w-6"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
							/>
						</svg>
					</button>
				{/if}

				{#if menuIsClosed}
					<button
						class="px-3"
						id="open-menu"
						onclick={toggleMenu}
						aria-label="Open navbar"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="24"
							height="24"
							viewBox="0 0 24 24"
							fill="none"
							stroke="#000000"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path d="M3 6h18M3 12h18M3 18h18" />
						</svg>
					</button>
				{:else}
					<button
						class="px-3"
						id="close-menu"
						onclick={toggleMenu}
						aria-label="Close navbar"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="24"
							height="24"
							viewBox="0 0 24 24"
							fill="none"
							stroke="#000000"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<path in:draw|global={{ duration: 300 }} d="M18 6 6 18" />
							<path in:draw|global={{ duration: 300 }} d="m6 6 12 12" />
						</svg>
					</button>
				{/if}
			</div>
		</div>

		{#if !menuIsClosed}
			<div class="flex flex-col gap-1 border-t border-slate-200/70 pt-3 dark:border-slate-700/70" transition:slide|global={{ duration: 400 }}>
				<a class="btn-nav" href="/">Enter PIN</a>
				{#if $signedIn}
					<a class="btn-nav" href="/dashboard">Dashboard</a>
					<a class="btn-nav" href="/api/v1/users/logout">Logout</a>
				{:else}
					<a class="btn-nav" href="/account/login?returnTo={$pathname}">Admin Login</a>
				{/if}
			</div>
		{/if}
	</div>
</nav>
