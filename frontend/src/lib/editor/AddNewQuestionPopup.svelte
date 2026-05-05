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
	class="fixed top-0 left-0 w-screen h-screen flex items-center justify-center bg-black/70 z-50"
	onclick={on_parent_click}
	transition:fade={{ duration: 100 }}
>
	<div class="relative w-full max-w-3xl mx-4 rounded-[2rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_120px_rgba(15,23,42,0.7)] p-8 flex flex-col gap-6 text-white max-h-[90vh]">
		<div class="text-center">
			<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80 mb-2">Editor</p>
			<h1 class="text-2xl font-semibold">{$t('quiztivity.editor.select_page_type')}</h1>
		</div>

		<div class="overflow-y-auto flex flex-col gap-6 pr-1">
			{#each section_order as section}
				{@const items = question_types
					.map((qt, idx) => ({ qt, idx }))
					.filter((item) => item.qt.category === section)}
				{#if items.length}
					<div class="space-y-3">
						<h2 class="text-xs uppercase tracking-[0.3em] text-slate-400/70">{section_titles[section]}</h2>
						<div class="grid grid-cols-3 gap-3">
							{#each items as item}
								<button
									class="rounded-2xl border border-white/10 bg-white/5 hover:border-[#B07156]/60 hover:bg-[#B07156]/8 p-4 text-left transition-all group"
									onclick={() => { add_question(item.idx); }}
								>
									<h3 class="text-sm font-semibold text-white mb-1 group-hover:text-[#B07156] transition-colors">{item.qt.name}</h3>
									<p class="text-xs text-slate-400 leading-5">{item.qt.description}</p>
								</button>
							{/each}
						</div>
					</div>
				{/if}
			{/each}
		</div>

		<div class="flex items-center justify-between pt-2 border-t border-white/8">
			<p class="text-xs text-slate-500">
				{$t('editor.need_more_help')}
				<a
					href="/docs/quiz/question-types"
					target="_blank"
					class="text-[#B07156] underline hover:text-[#c07d62] transition-colors"
				>{$t('editor.visit_docs')}</a>
			</p>
			<button
				class="rounded-full border border-white/15 px-5 py-2 text-sm font-semibold text-white/90 hover:bg-white/6 transition-colors"
				onclick={() => { open = false; }}
			>
				Cancel
			</button>
		</div>
	</div>
</div>
