<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->
<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import SearchCard from '$lib/search-card.svelte';
	import Button from '$lib/ui/Button.svelte';
	import Card from '$lib/ui/Card.svelte';
	import Input from '$lib/ui/Input.svelte';
	import PageHeader from '$lib/ui/PageHeader.svelte';
	import { pageTitle } from '$lib/brand';
	import { onMount } from 'svelte';

	const { t } = getLocalization();
	let search_term = $state('');
	let resp_data = $state(null);

	const submit = async () => {
		const res = await fetch('/api/v1/search/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ q: search_term, attributesToHighlight: ['*'] })
		});
		if (res.status === 200) {
			let resp_data_temp: string = await res.text();
			resp_data_temp = resp_data_temp.replaceAll('<em>', '<mark>');
			resp_data_temp = resp_data_temp.replaceAll('</em>', '</mark>');
			resp_data = JSON.parse(resp_data_temp);
			const url = new URLSearchParams(window.location.search);
			url.set('q', search_term);
			history.pushState(null, null, '?' + url.toString());
		} else {
			console.error('Error!', res.status);
		}
	};

	onMount(() => {
		const url = new URLSearchParams(window.location.search);
		search_term = url.get('q') ?? '';
		if (search_term.length > 2) {
			submit();
		}
	});
</script>

<svelte:head>
	<title>{pageTitle('Search')}</title>
</svelte:head>

<div class="mx-auto max-w-6xl px-4 py-8">
	<PageHeader
		eyebrow="Explore"
		title={$t('words.search') ?? 'Search'}
		description="Find public quizzes across the platform."
	/>

	<Card variant="glass" padding="md" class="mt-8">
		<form
			class="flex flex-col gap-3 sm:flex-row sm:items-center"
			onsubmit={(e: Event) => {
				e.preventDefault();
				submit();
			}}
		>
			<div class="flex-1">
				<Input
					type="search"
					bind:value={search_term}
					placeholder={$t('search_page.at_least_3_characters')}
					ariaLabel="Search"
				/>
			</div>
			<Button type="submit" variant="primary" disabled={search_term.length <= 2}>
				<svg class="h-4 w-4" aria-hidden="true" fill="currentColor" viewBox="0 0 512 512">
					<path
						d="M505 442.7L405.3 343c-4.5-4.5-10.6-7-17-7H372c27.6-35.3 44-79.7 44-128C416 93.1 322.9 0 208 0S0 93.1 0 208s93.1 208 208 208c48.3 0 92.7-16.4 128-44v16.3c0 6.4 2.5 12.5 7 17l99.7 99.7c9.4 9.4 24.6 9.4 33.9 0l28.3-28.3c9.4-9.4 9.4-24.6.1-34zM208 336c-70.7 0-128-57.2-128-128 0-70.7 57.2-128 128-128 70.7 0 128 57.2 128 128 0 70.7-57.2 128-128 128z"
					/>
				</svg>
				{$t('words.search')}
			</Button>
		</form>
	</Card>

	{#if resp_data}
		{#if resp_data.hits.length !== 0}
			<div class="mt-8 grid grid-cols-1 gap-4 lg:grid-cols-3">
				{#each resp_data.hits as quiz}
					<SearchCard quiz={quiz._formatted} />
				{/each}
			</div>
		{:else}
			<Card variant="flat" padding="lg" class="mt-8 text-center">
				<h2 class="text-2xl font-semibold text-slate-900 dark:text-white">
					{$t('search_page.nothing_here')}
				</h2>
				<p class="mt-3 text-slate-600 dark:text-slate-400">
					Not finding what you are looking for? Search on
					<a
						class="font-medium text-teal-700 underline hover:text-teal-800 dark:text-cyan-300"
						href="https://create.kahoot.it/search?query={search_term}&tags=test&filter=filter%3D1"
						target="_blank"
						rel="noreferrer">Kahoot</a
					>
					and <a class="font-medium text-teal-700 underline hover:text-teal-800 dark:text-cyan-300" href="/import"
						>import</a
					> it.
				</p>
			</Card>
		{/if}
	{/if}
</div>