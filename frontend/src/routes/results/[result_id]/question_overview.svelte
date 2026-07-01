<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { fly } from 'svelte/transition';
	import QuestionTab from './question_tab_dropdown.svelte';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import Card from '$lib/ui/Card.svelte';

	const { t } = getLocalization();

	interface Props {
		questions: Question[];
		answers: {
			username: string;
			answer: string;
			right: boolean;
			tike_taken: number;
			score: number;
		}[][];
	}

	let { questions, answers }: Props = $props();

	const get_average_score = (q_index: number): number => {
		const q_answers = answers[q_index];
		let summed_up_scores = 0;
		for (const answer of q_answers) {
			summed_up_scores = summed_up_scores + answer.score;
		}
		return summed_up_scores / q_answers.length;
	};

	const get_number_of_correct_answers = (q_index: number): number => {
		const q_answers = answers[q_index];
		let correct_answer = 0;
		for (const answer of q_answers) {
			if (answer.right) {
				correct_answer++;
			}
		}
		return correct_answer;
	};

	const toggle_dropdown = (q_index: number) => {
		if (question_open === q_index) {
			question_open = false;
		} else {
			question_open = q_index;
		}
	};
	let question_open: number | boolean = $state(false);
</script>

<div class="flex w-full flex-col gap-4">
	{#each questions as question, i}
		<div class="transition-all">
			<Card variant="glass" padding="sm" class="grid grid-cols-1 gap-2 sm:grid-cols-3">
				<button
					class="text-left text-base font-medium text-teal-700 underline decoration-teal-700/30 hover:text-teal-800 dark:text-cyan-300 dark:decoration-cyan-300/30 sm:text-center"
					onclick={() => {
						toggle_dropdown(i);
					}}
				>
					<span class="mr-2 text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">Q{i + 1}</span>
					{@html question.question}
				</button>
				{#if question.type !== QuizQuestionType.VOTING}
					{@const correct_answers = get_number_of_correct_answers(i)}
					<p class="my-auto text-center text-sm text-slate-600 dark:text-slate-400">
						{$t('result_page.average_score', {
							average_score: get_average_score(i)
						})}
					</p>
					<p class="my-auto text-center text-sm text-slate-600 dark:text-slate-400">
						{$t('result_page.correct_answer', { count: correct_answers })}
					</p>
				{/if}
			</Card>
			{#if question_open === i}
				<div class="mt-2" in:fly={{ y: -10 }}>
					<QuestionTab {question} answers={answers[i]} />
				</div>
			{/if}
		</div>
	{/each}
</div>