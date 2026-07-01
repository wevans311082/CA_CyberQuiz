<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import Footer from '$lib/footer.svelte';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import { page } from '$app/state';
	import { DOC_LINKS } from '$lib/docs/nav';
	import { pageTitle } from '$lib/brand';

	interface Props {
		children?: import('svelte').Snippet;
	}

	let { children }: Props = $props();

	navbarVisible.visible = true;
</script>

<svelte:head>
	<title>{pageTitle('Documentation')}</title>
</svelte:head>

<div class="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.08),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(13,148,136,0.1),transparent_32%)]">
	<div class="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-8 lg:flex-row lg:py-10">
		<aside class="lg:w-64 lg:shrink-0">
			<div class="sticky top-24 rounded-2xl border border-slate-200/70 bg-white/85 p-4 shadow-sm backdrop-blur-xl dark:border-slate-700/80 dark:bg-slate-900/70">
				<p class="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700 dark:text-cyan-300">
					Documentation
				</p>
				<nav class="mt-4 flex flex-col gap-1">
					{#each DOC_LINKS as link}
						<a
							href={link.href}
							class="rounded-lg px-3 py-2 text-sm font-medium transition-colors {page.url.pathname === link.href ? 'bg-brand-accent/15 text-teal-800 dark:text-cyan-200' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800/60'}"
						>
							{link.label}
						</a>
					{/each}
				</nav>
			</div>
		</aside>

		<main class="min-w-0 flex-1">
			{@render children?.()}
		</main>
	</div>
</div>

<div class="pt-4">
	<Footer />
</div>