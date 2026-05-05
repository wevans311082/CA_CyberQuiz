<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Answers, Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';


	interface Props {
		questions: Question[];
		open: boolean;
		selected_question: number;
	}

	let { questions = $bindable(), open = $bindable(), selected_question = $bindable() }: Props = $props();

	const { t } = getLocalization();
	onMount(() => {
		document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
	});
	const close_start_game_if_esc_is_pressed = (key: KeyboardEvent) => {
		if (key.code === 'Escape') {
			open = false;
		}
	};
	const on_parent_click = (e: Event) => {
		if (e.target === e.currentTarget) {
			open = false;
		}
	};

	const question_types: {
		name: string;
		description: string;
		answers: Answers;
		type: QuizQuestionType;
		category: 'INTERACTIVE' | 'CONTENT' | 'EVIDENCE';
	}[] = [
		{
			name: $t('words.multiple_choice'),
			description: $t('editor.abcd_description'),
			answers: [],
			type: QuizQuestionType.ABCD,
			category: 'INTERACTIVE'
		},
		{
			name: $t('words.voting'),
			description: $t('editor.voting_description'),
			answers: [],
			type: QuizQuestionType.VOTING,
			category: 'INTERACTIVE'
		},
		{
			name: $t('words.check_choice'),
			description: $t('editor.check_choice_description'),
			answers: [],
			type: QuizQuestionType.CHECK,
			category: 'INTERACTIVE'
		},
		{
			name: $t('words.order'),
			description: $t('editor.order_description'),
			answers: [],
			type: QuizQuestionType.ORDER,
			category: 'INTERACTIVE'
		},
		{
			name: $t('words.text'),
			description: $t('editor.text_description'),
			answers: [],
			type: QuizQuestionType.TEXT,
			category: 'INTERACTIVE'
		},
		{
			name: $t('words.range'),
			description: $t('editor.range_description'),
			answers: {
				max: 10,
				min: 0,
				max_correct: 7,
				min_correct: 3
			},
			type: QuizQuestionType.RANGE,
			category: 'INTERACTIVE'
		},
		{
			name: 'Information Screen',
			description: 'Present context, briefing notes, and instructions without collecting answers.',
			answers: '',
			type: QuizQuestionType.INFORMATION,
			category: 'CONTENT'
		},
		{
			name: 'File Screen',
			description: 'Present downloadable evidence files such as PDF, image, and logs.',
			answers: '',
			type: QuizQuestionType.FILE,
			category: 'EVIDENCE'
		}
	];

	const section_order: Array<'INTERACTIVE' | 'CONTENT' | 'EVIDENCE'> = ['INTERACTIVE', 'CONTENT', 'EVIDENCE'];
	const section_titles: Record<'INTERACTIVE' | 'CONTENT' | 'EVIDENCE', string> = {
		INTERACTIVE: 'Interactive Questions',
		CONTENT: 'Content Screens',
		EVIDENCE: 'Evidence Screens'
	};

	const add_question = (index: number) => {
		const empty_question: Question = {
			id: crypto.randomUUID(),
			type: question_types[index].type,
			time: '20',
			question: '',
			image: undefined,
			answers: question_types[index].answers,
			category: question_types[index].category,
			timer: { enabled: false }
		};
		questions = [...questions, { ...empty_question }];
		selected_question = questions.length - 1;
		open = false;
	};
</script>

<div
	class="fixed top-0 left-0 w-screen h-screen flex bg-black/50 z-50"
	onclick={on_parent_click}
	transition:fade={{ duration: 100 }}
>
	<div
		class="m-auto w-2/3 h-5/6 rounded-sm shadow-2xl bg-white dark:bg-gray-600 p-6 flex flex-col"
	>
		<h1 class="text-center text-3xl mb-6">{$t('quiztivity.editor.select_page_type')}</h1>
		<div class="overflow-y-scroll flex flex-col gap-4">
			{#each section_order as section}
				{@const items = question_types
					.map((qt, idx) => ({ qt, idx }))
					.filter((item) => item.qt.category === section)}
				{#if items.length}
					<div class="space-y-2">
						<h2 class="text-lg font-semibold text-black dark:text-white">{section_titles[section]}</h2>
						<div class="grid grid-cols-3 gap-3">
							{#each items as item}
								<div class="rounded-sm p-4 border-[#B07156] border">
									<button
										class="text-lg text-black dark:text-white text-left"
										onclick={() => {
											add_question(item.idx);
										}}>{item.qt.name}</button
									>
									<p class="text-sm">{item.qt.description}</p>
								</div>
							{/each}
						</div>
					</div>
				{/if}
			{/each}
		</div>

		<div class="mt-auto flex justify-center">
			<p>
				{$t('editor.need_more_help')}
				<a
					href="/docs/quiz/question-types"
					target="_blank"
					class="text-sm font-bold underline text-blue-500 dark:text-blue-400"
					>{$t('editor.visit_docs')}</a
				>
			</p>
		</div>
	</div>
</div>
