<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import PlayerOverview from './player_overview.svelte';
	import QuestionOverview from './question_overview.svelte';
	import GeneralOverview from './general_overview.svelte';
	import { fade } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';
	import Button from '$lib/ui/Button.svelte';
	import PageHeader from '$lib/ui/PageHeader.svelte';
	import Tabs from '$lib/ui/Tabs.svelte';
	import { pageTitle } from '$lib/brand';

	const { t } = getLocalization();

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();

	let selected_tab = $state('overview');

	const tabs = [
		{ id: 'overview', label: $t('words.overview') },
		{ id: 'players', label: $t('words.player', { count: 2 }) },
		{ id: 'questions', label: $t('words.question', { count: 2 }) }
	];
</script>

<svelte:head>
	<title>{pageTitle(data.results?.title ?? 'Result')}</title>
</svelte:head>

<div class="mx-auto max-w-6xl px-4 py-8">
	<PageHeader
		eyebrow="Session Report"
		title={data.results?.title ?? 'Result'}
		description="Review scores, player responses, and question breakdowns from this session."
	>
		{#snippet actions()}
			<Button href="/results/aar/{data.results.id}" variant="primary" size="sm">
				View After-Action Report
			</Button>
			<Button href="/api/v1/results/export-csv/{data.results.id}" download variant="secondary" size="sm">
				Download CSV
			</Button>
		{/snippet}
	</PageHeader>

	<div class="mt-8">
		<Tabs {tabs} bind:active={selected_tab} />
	</div>

	<div class="mt-6">
		{#if selected_tab === 'overview'}
			<div in:fade|global={{ duration: 150 }}>
				<GeneralOverview
					scores={data.results.player_scores}
					title={data.results.title}
					timestamp={data.results.timestamp}
				/>
			</div>
		{:else if selected_tab === 'questions'}
			<div in:fade|global={{ duration: 150 }}>
				<QuestionOverview questions={data.results.questions} answers={data.results.answers} />
			</div>
		{:else if selected_tab === 'players'}
			<div in:fade|global={{ duration: 150 }}>
				<PlayerOverview
					custom_field={data.results.custom_field_data}
					scores={data.results.player_scores}
					answers={data.results.answers}
				/>
			</div>
		{/if}
	</div>
</div>