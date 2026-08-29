<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData, Question } from '../quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { reach } from 'yup';
	import { ABCDQuestionSchema, dataSchema } from '../yupSchemas';
	import { createTippy } from 'svelte-tippy';
	import { getLocalization } from '$lib/i18n';
	import AddNewQuestionPopup from '$lib/editor/AddNewQuestionPopup.svelte';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { fade } from 'svelte/transition';
	import { confirmAction } from '$lib/notifications.svelte';

	const { t } = getLocalization();

	interface Props {
		data: EditorData;
		selected_question?: any;
	}

	let { data = $bindable(), selected_question = $bindable(-1) }: Props = $props();

	let reorder_mode = $state(false);

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'right'
	});
	let arr_of_cards = $state(Array(data.questions.length));
	let propertyCard = $state();
	let add_new_question_popup_open = $state(false);

	const empy_slide: Question = {
		type: QuizQuestionType.SLIDE,
		time: '120',
		question: 'Slide',
		image: undefined,
		answers: ''
	};

	const swapArrayElements = (arr, a: number, b: number) => {
		let _arr = [...arr];
		let temp = _arr[a];
		_arr[a] = _arr[b];
		_arr[b] = temp;
		return _arr;
	};

	const setSelectedQuestion = (index: number): void => {
		if (reorder_mode) {
			return;
		}
		selected_question = index;
		if (index === -1) {
			propertyCard.scrollIntoView({
				behavior: 'smooth'
			});
		} else {
			arr_of_cards[index].scrollIntoView({
				behavior: 'smooth'
			});
		}
	};

	const delete_question = async (index: number, e: MouseEvent) => {
		e.stopPropagation();
		if (!(await confirmAction('Do you really want to delete this question?', { title: 'Delete question', confirmLabel: 'Delete question' }))) {
			return;
		}

		const next_questions = data.questions.filter((_, i) => i !== index);
		data = {
			...data,
			questions: next_questions
		};

		if (selected_question === index) {
			selected_question = next_questions.length ? Math.max(0, index - 1) : -1;
		} else if (selected_question > index) {
			selected_question -= 1;
		}
	};
	/*	onMount(() => {
            propertyCard.scrollIntoView({
                behavior: 'smooth'
            });
        });*/
</script>

<div class="h-screen relative">
	<div class="absolute right-3 top-3 z-20">
		<button type="button" class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[11px] font-semibold text-slate-600 shadow-sm hover:border-teal-300 hover:text-teal-700" onclick={() => (reorder_mode = !reorder_mode)}>
			<span>{reorder_mode ? 'Done' : 'Reorder'}</span>
		</button>
	</div>
	<div class="h-full overflow-scroll border-r border-slate-200 bg-[#f8fafc] px-3 pt-16 shadow-[4px_0_18px_rgba(15,23,42,0.03)] sm:px-4">
		<div
			bind:this={propertyCard}
			class="mb-6 h-40 cursor-pointer rounded-xl border border-slate-200 bg-slate-50 p-2 shadow-sm transition-all hover:border-teal-300 dark:border-slate-700 dark:bg-slate-900/80 {selected_question === -1 ? 'ring-2 ring-brand-accent border-brand-accent/50 bg-brand-accent/10' : ''}"
			onclick={() => setSelectedQuestion(-1)}
		>
			<div
				use:tippy={{ content: data.title === '' ? "It's empty!" : data.title }}
				class="m-1 border border-gray-500 rounded-lg p-0.5 transition"
				class:border-red-600={!((reach(dataSchema, 'title') as any).isValidSync(data.title))}
				class:border-solid={!((reach(dataSchema, 'title') as any).isValidSync(data.title))}
				class:border-2={!((reach(dataSchema, 'title') as any).isValidSync(data.title))}
			>
				<p
					type="text"
					class="whitespace-nowrap truncate text-center w-full bg-transparent rounded-sm dark:text-white"
					class:dark:text-black={selected_question === -1}
				>
					{#if data.title}
						{@html data.title}
					{:else}
						<i>{$t('editor.no_title')}</i>
					{/if}
				</p>
			</div>
			<div
				use:tippy={{ content: data.description === '' ? "It's empty!" : data.description }}
				class="m-1 border border-gray-500 rounded-lg p-0.5 transition"
				class:border-red-600={!((reach(dataSchema, 'description') as any).isValidSync(
					data.description
				))}
				class:border-solid={!((reach(dataSchema, 'description') as any).isValidSync(data.description))}
				class:border-2={!((reach(dataSchema, 'description') as any).isValidSync(data.description))}
			>
				<textarea
					bind:value={data.description}
					class="bg-transparent resize-none w-full rounded-sm text-sm dark:text-white"
					class:dark:text-black={selected_question === -1}
				></textarea>
			</div>
			<div
				class="w-full flex justify-center dark:text-white"
				class:dark:text-black={selected_question === -1}
			>
				<button
					type="button"
					onclick={() => {
						data.public = !data.public;
					}}
					class="text-center"
				>
					{#if data.public}
						<svg
							class="w-5 h-5 inline-block"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						<span>{$t('words.public')}</span>
					{:else}
						<svg
							class="w-5 h-5 inline-block"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
							/>
						</svg>
						<span>{$t('words.private')}</span>
					{/if}
				</button>
			</div>
		</div>
		{#each data.questions as question, index}
			<div
				class="relative mb-6 h-40 cursor-pointer rounded-xl border border-slate-200/70 bg-white/90 p-2 shadow-sm transition-all hover:border-brand-accent/30 dark:border-slate-700 dark:bg-slate-900/80 {index === selected_question ? 'ring-2 ring-brand-accent border-brand-accent/50 bg-brand-accent/10' : ''}"
				onclick={() => {
					setSelectedQuestion(index);
				}}
				bind:this={arr_of_cards[index]}
			>
				{#if reorder_mode}
					<div
						transition:fade|global={{ duration: 90 }}
						class="absolute z-10 grid grid-cols-2 bg-transparent w-full rounded-sm h-full"
					>
						<!-- Div is used, since it just put me on the dashboard when using button elements... Idk why and I hate it-->
						<div
							class="h-full"
							role="button"
							aria-label="Move card up"
							class:opacity-50={index === 0}
							class:pointer-events-none={index === 0}
							onclick={() =>
								(data.questions = swapArrayElements(
									data.questions,
									index,
									index - 1
								))}
						>
							<!-- heroicons/new/ChevronUp --><svg
								data-slot="icon"
								aria-hidden="true"
								fill="none"
								stroke-width="1.5"
								stroke="currentColor"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="m4.5 15.75 7.5-7.5 7.5 7.5"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</div>
						<div
							class="h-full"
							role="button"
							aria-label="Move card down"
							class:opacity-50={index + 1 === data.questions.length}
							class:pointer-events-none={index + 1 === data.questions.length}
							onclick={() =>
								(data.questions = swapArrayElements(
									data.questions,
									index,
									index + 1
								))}
						>
							<!-- heroicons/new/ChevronDown -->
							<svg
								data-slot="icon"
								aria-hidden="true"
								fill="none"
								stroke-width="1.5"
								stroke="currentColor"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="m19.5 8.25-7.5 7.5-7.5-7.5"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</div>
					</div>
				{/if}
				<button
					class="rounded-full absolute -top-3 -right-3 opacity-70 hover:opacity-100 transition"
					type="button"
					onclick={(e) => delete_question(index, e)}
				>
					<svg
						class="w-6 h-6 bg-red-500 rounded-full"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				</button>
				<div
					use:tippy={{
						content: question.question === '' ? 'No title' : question.question
					}}
					class="m-1 border border-gray-500 rounded-lg p-0.5"
				>
					<h1
						class="whitespace-nowrap truncate text-center rounded-lg dark:text-white transition"
						class:bg-yellow-500={!((reach(dataSchema, 'questions[].question') as any).isValidSync(
							question.question
						))}
						class:dark:text-black={index === selected_question}
					>
						{#if question.question === ''}
							<span class="italic text-gray-500">{$t('editor.no_title')}</span>
						{:else}
							{@html question.question}
						{/if}
					</h1>
				</div>
				{#if question.image}
					<div class="flex justify-center align-middle pb-0.5">
						<img
							src="/api/v1/storage/download/{question.image}"
							class="h-10 border rounded-lg"
							alt="Not available"
							use:tippy={{
								content: `<img src="/api/v1/storage/download/${question.image}" alt="Not available" class="rounded-sm">`,
								allowHTML: true
							}}
						/>
					</div>
				{/if}

				{#if question.type === QuizQuestionType.ABCD || question.type === QuizQuestionType.CHECK}
					<div class="grid grid-cols-2 gap-2">
						{#if Array.isArray(question.answers)}
							{#each question.answers as answer}
								{@const plain_answer = answer.answer.replace(/<[^>]*>/g, '').trim()}
								<span
									class="whitespace-nowrap truncate rounded-lg p-0.5 text-sm text-center border border-gray-700"
									class:bg-green-500={answer.right}
									class:bg-red-500={!answer.right}
									class:bg-yellow-500={!reach(
										ABCDQuestionSchema,
										'answer'
									).isValidSync(answer.answer)}
									use:tippy={{
										content:
											plain_answer === ''
												? $t('editor.empty')
												: plain_answer
									}}
									>{#if plain_answer === ''}
										<i>{$t('editor.empty')}</i>
									{:else}
										{plain_answer}
									{/if}</span
								>
							{/each}
						{/if}
					</div>
				{:else if question.type === QuizQuestionType.RANGE}
					<p class="text-center text-sm p-0.5">
						All numbers between {question.answers.min_correct}
						and {question.answers.max_correct} are correct, where numbers between {question
							.answers.min} and {question.answers.max} can be selected.
					</p>
				{:else if question.type === QuizQuestionType.VOTING || question.type === QuizQuestionType.TEXT}
					{#if Array.isArray(question.answers)}
						<div class="grid grid-cols-2 gap-2">
							{#each question.answers as answer}
								{@const plain_answer = answer.answer.replace(/<[^>]*>/g, '').trim()}
								<span
									class="whitespace-nowrap truncate rounded-lg p-0.5 text-sm text-center border border-gray-700"
									class:dark:bg-gray-500={answer.answer}
									class:bg-gray-300={answer.answer}
									class:bg-yellow-500={!reach(
										ABCDQuestionSchema,
										'answer'
									).isValidSync(answer.answer)}
									use:tippy={{
										content:
											plain_answer === ''
												? $t('editor.empty')
												: plain_answer
									}}
									>{#if plain_answer === ''}
										<i>{$t('editor.empty')}</i>
									{:else}
										{plain_answer}
									{/if}</span
								>
							{/each}
						</div>
					{/if}
				{:else if question.type === QuizQuestionType.SLIDE}
					<p>Some smart information on a slide</p>
				{:else if question.type === QuizQuestionType.ORDER}
					<p>Get thing's into the right order!</p>
				{:else}
					<p>Unknown Question Type (shouldn't happen)</p>
				{/if}
			</div>
		{/each}
		<div class="mt-3 grid grid-cols-2 gap-2 rounded-2xl border border-dashed border-slate-300 bg-white p-2 shadow-sm">
			<button
				type="button"
				class="flex min-h-20 items-center justify-center gap-1 rounded-xl border-r border-slate-200 text-xs font-semibold text-slate-600 hover:bg-teal-50 hover:text-teal-700"
				onclick={() => {
					add_new_question_popup_open = true;
				}}
			>
				<span class="w-full text-center">{$t('words.question')}</span>
				<svg
					class="h-5 w-5"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 6v6m0 0v6m0-6h6m-6 0H6"
					/>
				</svg>
			</button>
			<button
				type="button"
				class="flex min-h-20 items-center justify-center gap-1 rounded-xl text-xs font-semibold text-slate-600 hover:bg-teal-50 hover:text-teal-700"
				onclick={() => {
					data.questions = [...data.questions, { ...empy_slide, id: crypto.randomUUID() }];
				}}
			>
				<span class="w-full text-center">{$t('words.slide')}</span>
				<svg
					class="h-5 w-5"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 6v6m0 0v6m0-6h6m-6 0H6"
					/>
				</svg>
			</button>
		</div>
	</div>
</div>
{#if add_new_question_popup_open}
	<AddNewQuestionPopup
		bind:questions={data.questions}
		bind:open={add_new_question_popup_open}
		bind:selected_question
	/>
{/if}
