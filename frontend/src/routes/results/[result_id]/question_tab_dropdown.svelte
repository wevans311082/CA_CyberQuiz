<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { QuizQuestionType } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import type { Question } from '$lib/quiz_types';
	import Card from '$lib/ui/Card.svelte';

	const { t } = getLocalization();

	interface Answer {
		username: string;
		answer: string;
		right: boolean;
		time_taken: number;
		score: number;
	}

	interface Props {
		question: Question;
		answers: Answer[];
	}

	let { question, answers }: Props = $props();

	const get_answer_count_for_answer = (answer: string): number => {
		let count = 0;
		let answer_id = 0;
		if (question.type === QuizQuestionType.CHECK) {
			for (let i = 0; i < question.answers.length; i++) {
				if (answer === question.answers[i].answer) {
					answer_id = i;
					break;
				}
			}
		}
		for (let i = 0; i < answers.length; i++) {
			const a = answers[i];
			if (question.type === QuizQuestionType.CHECK) {
				if (a.answer.includes(String(answer_id))) {
					count++;
				}
			} else if (a.answer === answer) {
				count++;
			}
		}
		return count;
	};
</script>

<Card variant="flat" padding="md" class="w-full">
	{#if question.type !== QuizQuestionType.ORDER && question.type !== QuizQuestionType.RANGE}
		<div class="mb-4 flex flex-col gap-2">
			{#each question.answers as answer}
				<div class="grid grid-cols-4 gap-2 text-sm">
					<p class="text-slate-700 dark:text-slate-200">{answer.answer}</p>
					<div class="col-span-3 flex w-full items-center gap-2 border-l border-slate-200 pl-2 dark:border-slate-700">
						<div class="my-auto w-full">
							<span
								class="block h-1.5 rounded-full bg-teal-600 dark:bg-cyan-500"
								style="width: {(get_answer_count_for_answer(answer.answer) / answers.length) * 100}%"
							></span>
						</div>
						<p class="shrink-0 text-slate-600 dark:text-slate-400">{get_answer_count_for_answer(answer.answer)}</p>
						{#if question.type !== QuizQuestionType.VOTING && question.type !== QuizQuestionType.TEXT}
							<p class="ml-1">
								{#if answer.right}✅{:else}❌{/if}
							</p>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/if}
	<div class="overflow-x-auto">
		<table class="w-full min-w-[480px] text-left text-sm">
			<thead class="border-b border-slate-200/70 dark:border-slate-700">
				<tr>
					<th class="px-3 py-2 font-semibold text-slate-700 dark:text-slate-200">
						{$t('result_page.player_name')}
					</th>
					{#if question.type !== QuizQuestionType.VOTING}
						<th class="px-3 py-2 font-semibold text-slate-700 dark:text-slate-200">
							{$t('words.score')}
						</th>
					{/if}
					<th class="px-3 py-2 font-semibold text-slate-700 dark:text-slate-200">
						{$t('result_page.time_taken')}
					</th>
					<th class="px-3 py-2 font-semibold text-slate-700 dark:text-slate-200">
						{$t('words.answer')}
					</th>
					{#if question.type !== QuizQuestionType.VOTING}
						<th class="px-3 py-2 font-semibold text-slate-700 dark:text-slate-200">
							{$t('words.correct')}?
						</th>
					{/if}
				</tr>
			</thead>
			<tbody>
				{#each answers as answer}
					<tr class="border-b border-slate-200/50 dark:border-slate-700/50">
						<td class="px-3 py-2 text-slate-900 dark:text-slate-100">{answer.username}</td>
						{#if question.type !== QuizQuestionType.VOTING}
							<td class="px-3 py-2 text-slate-600 dark:text-slate-400">{answer.score}</td>
						{/if}
						<td class="px-3 py-2 text-slate-600 dark:text-slate-400">
							{(answer.time_taken / 1000).toFixed(3)}s
						</td>
						<td class="px-3 py-2 text-slate-600 dark:text-slate-400">{answer.answer}</td>
						{#if question.type !== QuizQuestionType.VOTING}
							<td class="px-3 py-2">
								{#if answer.right}✅{:else}❌{/if}
							</td>
						{/if}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</Card>