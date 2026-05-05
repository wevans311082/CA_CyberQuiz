<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import { onMount } from 'svelte';
	import Pikaso from 'pikaso';

	interface Props {
		question: Question;
	}

	let { question }: Props = $props();

	let canvas_el: HTMLDivElement | undefined = $state();
	let canvas: Pikaso;
	let img_src = $state('');

	onMount(() => {
		if (question.type === QuizQuestionType.INFORMATION || question.type === QuizQuestionType.FILE) {
			return;
		}
		canvas = new Pikaso({
			container: canvas_el,
			snapToGrid: {},
			selection: {
				interactive: false
			}
		});
		if (typeof question.answers === 'string') {
			const data = JSON.parse(question.answers);
			canvas.import.json(data);
			img_src = canvas.export.toImage();
		}
	});
</script>

<div class="w-full h-full">
	{#if question.type === QuizQuestionType.INFORMATION || question.type === QuizQuestionType.FILE}
		<div class="mx-auto mt-10 max-w-5xl px-6 space-y-4">
			<h2 class="text-4xl text-center">{@html question.question}</h2>
			{#if question.information_body || typeof question.answers === 'string'}
				<div class="rounded-xl border border-gray-300 bg-white/90 p-6 text-gray-900 shadow">
					<p class="whitespace-pre-wrap">{question.information_body ?? question.answers}</p>
				</div>
			{/if}
			{#if question.type === QuizQuestionType.FILE && question.file_attachments?.length}
				<div class="space-y-2">
					{#each question.file_attachments as attachment}
						<div class="flex items-center justify-between rounded-lg border border-gray-300 bg-white px-4 py-3">
							<div>
								<p class="font-medium">{attachment.filename}</p>
								<p class="text-xs text-gray-500">{attachment.mime_type}</p>
							</div>
							<a
								href={attachment.url}
								target="_blank"
								rel="noopener noreferrer"
								class="rounded-md bg-[#B07156] px-3 py-1.5 text-sm font-semibold text-white"
							>
								Open
							</a>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{:else}
		<div class="hidden">
			<div bind:this={canvas_el} class="w-full h-full block"></div>
		</div>
		<div class="w-full h-full flex justify-center">
			<img src={img_src} alt="Slide image" />
		</div>
	{/if}
</div>
