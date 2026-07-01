<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import Card from '$lib/ui/Card.svelte';
	import PageHeader from '$lib/ui/PageHeader.svelte';
	import { DOC_LINKS } from '$lib/docs/nav';
	import { pageTitle } from '$lib/brand';
</script>

<svelte:head>
	<title>{pageTitle('Documentation')}</title>
	<meta
		name="description"
		content="CyberAsk Quiz documentation — tabletop exercises, live quizzes, hosting, and imports."
	/>
</svelte:head>

<PageHeader
	eyebrow="Documentation"
	title="CyberAsk Quiz docs"
	description="Guides for running tabletop exercises, hosting live quizzes, importing content, and deploying the platform."
/>

<div class="mt-8 grid gap-4 sm:grid-cols-2">
	{#each DOC_LINKS.filter((l) => l.href !== '/docs') as link}
		<a href={link.href} class="block transition-transform hover:-translate-y-0.5">
			<Card variant="glass" padding="md" class="h-full">
				<p class="font-semibold text-slate-900 dark:text-white">{link.label}</p>
				<p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Open guide →</p>
			</Card>
		</a>
	{/each}
</div>

<Card variant="flat" padding="lg" class="mt-8">
	<h2 class="text-lg font-semibold text-slate-900 dark:text-white">Quick start</h2>
	<ol class="mt-4 list-decimal space-y-2 pl-5 text-sm text-slate-600 dark:text-slate-300">
		<li>Create or import a quiz from the dashboard.</li>
		<li>Choose tabletop mode for cyber exercises with roles, injects, and branching.</li>
		<li>Start a session and share the game PIN with participants.</li>
		<li>Use the facilitator console during play to manage the situation room and injects.</li>
	</ol>
</Card>