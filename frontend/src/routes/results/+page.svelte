<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import { getLocalization } from '$lib/i18n';
	import Card from '$lib/ui/Card.svelte';
	import PageHeader from '$lib/ui/PageHeader.svelte';
	import { pageTitle } from '$lib/brand';

	const { t } = getLocalization();

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();
</script>

<svelte:head>
	<title>{pageTitle('Results')}</title>
</svelte:head>

<div class="mx-auto max-w-6xl px-4 py-8">
	<PageHeader
		eyebrow="Session History"
		title={$t('words.results')}
		description="Review past game sessions, player counts, and open detailed reports."
	/>

	{#if data.results.length === 0}
		<Card variant="glass" padding="lg" class="mt-8 text-center">
			<p class="text-lg text-slate-500 dark:text-slate-400">{$t('results_page.no_results_so_far')}</p>
		</Card>
	{:else}
		<Card variant="glass" padding="none" class="mt-8 overflow-hidden">
			<div class="overflow-x-auto">
				<table class="w-full min-w-[640px] text-left text-sm">
					<thead class="border-b border-slate-200/70 bg-slate-50/80 dark:border-slate-700 dark:bg-slate-900/50">
						<tr>
							<th class="px-4 py-3 font-semibold text-slate-700 dark:text-slate-200">
								{$t('results_page.quiz_title')}
							</th>
							<th class="px-4 py-3 font-semibold text-slate-700 dark:text-slate-200">
								{$t('results_page.date_played')}
							</th>
							<th class="px-4 py-3 font-semibold text-slate-700 dark:text-slate-200">
								{$t('results_page.player_count')}
							</th>
							<th class="px-4 py-3 font-semibold text-slate-700 dark:text-slate-200">
								{$t('words.note')}
							</th>
						</tr>
					</thead>
					<tbody>
						{#each data.results as result}
							<tr class="border-b border-slate-200/50 transition-colors hover:bg-slate-50/60 dark:border-slate-700/50 dark:hover:bg-slate-800/40">
								<td class="px-4 py-3">
									<a
										href="/results/{result.id}"
										class="font-medium text-teal-700 underline decoration-teal-700/30 hover:text-teal-800 dark:text-cyan-300 dark:decoration-cyan-300/30"
									>
										{@html result.title}
									</a>
								</td>
								<td class="px-4 py-3 text-slate-600 dark:text-slate-400">
									{new Date(result.timestamp).toLocaleString()}
								</td>
								<td class="px-4 py-3 text-slate-600 dark:text-slate-400">
									{Object.keys(result.player_scores).length}
								</td>
								<td class="px-4 py-3 text-slate-500 dark:text-slate-400">
									{result.note ?? '—'}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</Card>
	{/if}
</div>