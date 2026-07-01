<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import Card from '$lib/ui/Card.svelte';

	const { t } = getLocalization();
	interface Props {
		scores: {
			[key: string]: string;
		};
		custom_field: {
			[key: string]: string;
		};
		answers: { [key: string]: any }[];
	}

	let { scores, custom_field, answers }: Props = $props();

	let usernames = $derived(
		Object.keys(scores).sort((a, b) => {
			const scoreA = parseFloat(scores[a]) || 0;
			const scoreB = parseFloat(scores[b]) || 0;
			return scoreB - scoreA;
		})
	);

	const correctCounts = {};
	answers.forEach((questionAnswers) => {
		questionAnswers.forEach((answer) => {
			const user = answer.username;
			if (!correctCounts[user]) {
				correctCounts[user] = 0;
			}
			if (answer.right) {
				correctCounts[user] += 1;
			}
		});
	});
</script>

<Card variant="glass" padding="none" class="overflow-hidden">
	<div class="overflow-x-auto">
		<table class="w-full min-w-[480px] text-left text-sm">
			<thead class="border-b border-slate-200/70 bg-slate-50/80 dark:border-slate-700 dark:bg-slate-900/50">
				<tr>
					<th class="px-4 py-3 font-semibold text-slate-700 dark:text-slate-200">
						{$t('result_page.player_name')}
					</th>
					<th class="px-4 py-3 font-semibold text-slate-700 dark:text-slate-200">
						{$t('result_page.player_correct_questions')}
					</th>
					<th class="px-4 py-3 font-semibold text-slate-700 dark:text-slate-200">
						{$t('result_page.player_score')}
					</th>
					{#if Object.keys(custom_field).length !== 0}
						<th class="px-4 py-3 font-semibold text-slate-700 dark:text-slate-200">
							{$t('result_page.custom_field')}
						</th>
					{/if}
				</tr>
			</thead>
			<tbody>
				{#each usernames as uname, i}
					<tr
						class="border-b border-slate-200/50 transition-colors hover:bg-slate-50/60 dark:border-slate-700/50 dark:hover:bg-slate-800/40"
					>
						<td class="px-4 py-3 font-medium text-slate-900 dark:text-slate-100">
							<span class="mr-2 text-xs text-slate-400">#{i + 1}</span>
							{uname}
						</td>
						<td class="px-4 py-3 text-slate-600 dark:text-slate-400">{correctCounts[uname]}</td>
						<td class="px-4 py-3 font-semibold text-teal-700 dark:text-cyan-300">{scores[uname]}</td>
						{#if custom_field[uname]}
							<td class="px-4 py-3 text-slate-600 dark:text-slate-400">{custom_field[uname]}</td>
						{/if}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</Card>