<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { run } from 'svelte/legacy';

	import type { EditorData } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import RangeEditor from '$lib/editor/RangeSelectorEditorPart.svelte';
	import { reach } from 'yup';
	import { dataSchema } from '$lib/yupSchemas';
	import Spinner from '../Spinner.svelte';
	import { createTippy } from 'svelte-tippy';
	import { getLocalization } from '$lib/i18n';
	import HoverRichTextEditor from '$lib/editor/HoverRichTextEditor.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import MasterThemeEditor from '$lib/editor/MasterThemeEditor.svelte';
	import { fade } from 'svelte/transition';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	// import MediaComponent from "$lib/editor/MediaComponent.svelte";

	const { t } = getLocalization();

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'top'
	});

	interface Props {
		data: EditorData;
		selected_question: number;
		edit_id: string;
	}

	let {
		data = $bindable(),
		selected_question = $bindable(),
		edit_id = $bindable()
	}: Props = $props();

	let advanced_options_open = $state(false);

	let uppyOpen = $state(false);

	/*eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }]*/
	const correctTimeInput = (_) => {
		let time = data.questions[selected_question].time;
		if (time === null || time === undefined) {
			data.questions[selected_question].time = '';
			time = '';
		}
		if (data.questions[selected_question].time > 3) {
			data.questions[selected_question].time = data.questions[selected_question].time
				.toString()
				.slice(0, 3);
		}
	};
	run(() => {
		correctTimeInput(data.questions[selected_question].time);
	});
	let image_url = $state('');

	const update_image_url = () => {
		image_url = data.questions[selected_question].image;
	};
	run(() => {
		update_image_url();
		selected_question;
		data.questions;
	});

	const type_to_name = {
		RANGE: $t('words.range'),
		ABCD: $t('words.multiple_choice'),
		VOTING: $t('words.voting'),
		INFORMATION: 'Information Screen',
		FILE: 'File Screen',
		TEXT: $t('words.text'),
		ORDER: $t('words.order'),
		CHECK: $t('words.check_choice'),
		SCOREBOARD: 'Scoreboard Slide'
	};

	/*
    if (typeof data.questions[selected_question].type !== QuizQuestionType) {
        console.log(data.questions[selected_question].type !== QuizQuestionType.ABCD || data.questions[selected_question].type !== QuizQuestionType.RANGE)
        data.questions[selected_question].type = QuizQuestionType.ABCD;
    }
     */
</script>

<div class="w-full max-h-full pb-10 px-10 h-full">
	<div class="rounded-lg bg-white w-full h-full border-gray-500 dark:bg-gray-700 shadow-2xl">
		<div class="h-12 bg-gray-300 rounded-t-lg dark:bg-gray-500">
			<div class="flex align-middle p-4 gap-3">
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-red-400 transition"
				></span>
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-yellow-400 transition"
				></span>
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-green-400 transition"
				></span>
				<button
					class="ml-auto"
					type="button"
					use:tippy={{ content: $t('editor.advanced_settings') }}
					onclick={() => (advanced_options_open = true)}
				>
					<svg
						class="text-white w-5 h-5"
						aria-hidden="true"
						fill="none"
						stroke="white"
						stroke-width="2"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
						<path
							d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
					</svg>
				</button>
			</div>
		</div>
		{#if data.questions[selected_question].type === QuizQuestionType.SLIDE}
			{#await import('./slide.svelte')}
				<Spinner my_20={false} />
			{:then c}
				<c.default bind:data={data.questions[selected_question]} />
			{/await}
		{:else}
			{@const type = data.questions[selected_question].type}
			<div class="flex flex-col">
				<div class="flex justify-center pt-10 w-full">
					<div
						class="w-full max-w-4xl rounded-lg placeholder:italic placeholder:font-normal dark:bg-gray-500"
						class:bg-yellow-500={!reach(
							dataSchema,
							'questions[].question'
						).isValidSync(data.questions[selected_question].question)}
					>
						<HoverRichTextEditor
							bind:text={data.questions[selected_question].question}
							placeholder="Question title"
							minHeightClass="min-h-[4rem]"
							toolbarLabel="Question formatting tools"
						/>
					</div>
				</div>
				{#if data.questions[selected_question].image}
					<div class="flex justify-center pt-10 w-full h-72">
						<div class="h-72 relative">
							<button
								class="rounded-full absolute -top-2 -right-2 opacity-70 hover:opacity-100 transition"
								type="button"
								onclick={() => {
									data.questions[selected_question].image = null;
								}}
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
							<MediaComponent bind:src={image_url} />
						</div>
					</div>
				{:else}
					{#await import('$lib/editor/uploader.svelte')}
						<Spinner my_20={false} />
					{:then c}
						<c.default
							bind:modalOpen={uppyOpen}
							bind:edit_id
							bind:data
							bind:selected_question
							video_upload={true}
						/>
					{/await}
				{/if}
				<div class="flex justify-center pt-10 w-full">
					<div>
						<svg
							class="w-8 h-8 inline-block"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						<input
							type="number"
							max="999"
							min="1"
							class="w-20 bg-transparent rounded-lg text-lg border-2 border-gray-500 p-1 outline-hidden focus:shadow-2xl"
							bind:value={data.questions[selected_question].time}
						/>
						<p class="inline-block">s</p>
					</div>
				</div>
				<div class="flex justify-center py-5">
					<p>{type_to_name[String(data.questions[selected_question].type)]}</p>
				</div>
				<div class="flex justify-center w-full">
					{#if type === QuizQuestionType.ABCD || type === QuizQuestionType.CHECK}
						{#await import('$lib/editor/ABCDEditorPart.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<c.default
								bind:data
								bind:selected_question
								check_choice={type === QuizQuestionType.CHECK}
							/>
						{/await}
					{:else if type === QuizQuestionType.RANGE}
						<RangeEditor bind:selected_question bind:data />
					{:else if type === QuizQuestionType.VOTING}
						{#await import('$lib/editor/VotingEditorPart.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<c.default bind:data bind:selected_question />
						{/await}
					{:else if type === QuizQuestionType.TEXT}
						{#await import('$lib/editor/TextEditorPart.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<c.default bind:data bind:selected_question />
						{/await}
					{:else if type === QuizQuestionType.ORDER}
						{#await import('$lib/editor/OrderEditorPart.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<c.default bind:data bind:selected_question />
						{/await}
					{:else if type === QuizQuestionType.INFORMATION}
						{#await import('$lib/editor/InformationEditorPart.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<c.default bind:data bind:selected_question />
						{/await}
					{:else if type === QuizQuestionType.FILE}
						{#await import('$lib/editor/FileEditorPart.svelte')}
							<Spinner my_20={false} />
						{:then c}
							<c.default bind:data bind:selected_question />
						{/await}
					{:else if type === QuizQuestionType.SCOREBOARD}
						<div class="flex flex-col items-center justify-center gap-3 py-10 text-center text-gray-500 dark:text-gray-400">
							<svg class="h-12 w-12 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
							<p class="font-medium">Scoreboard Slide</p>
							<p class="text-sm">Displays current player rankings and company score during gameplay. No answers are collected.</p>
						</div>
					{/if}
				</div>
			</div>
		{/if}
	</div>
</div>

{#if advanced_options_open}
	<div
		class="fixed top-0 left-0 w-full h-full bg-black/60 flex"
		transition:fade|global={{ duration: 150 }}
	>
		<div
			class="w-1/3 max-h-[70vh] overflow-auto m-auto bg-white dark:bg-gray-700 rounded-lg flex flex-col p-4 gap-3"
		>
			<h1 class="text-3xl mx-auto">{$t('editor.advanced_settings')}</h1>
			<div class="flex flex-col gap-2 rounded-lg border border-gray-300 p-3 dark:border-gray-600">
				<h2 class="text-xl font-semibold">Master Slide Theme</h2>
				<MasterThemeEditor bind:master_theme={data.master_theme} />
			</div>
			<label class="flex justify-around text-lg">
				<span class="my-auto">{$t('editor.hide_question_results')}</span>
				<input
					type="checkbox"
					bind:checked={data.questions[selected_question]['hide_results']}
				/>
			</label>
			{#if data.scenario_type === 'tabletop'}
				<hr class="border-gray-300 dark:border-gray-600" />
				<h2 class="text-xl font-semibold text-center">Tabletop Settings</h2>
				<!-- Per-Slide Answer Timer -->
				<div class="flex flex-col gap-1">
					<span class="text-sm font-medium">Per-Slide Answer Timer</span>
					<label class="inline-flex items-center gap-2 text-sm">
						<input
							type="checkbox"
							checked={data.questions[selected_question].timer?.enabled ?? false}
							onchange={(e) => {
								const enabled = e.currentTarget.checked;
								data.questions[selected_question].timer = {
									enabled,
									duration_seconds: data.questions[selected_question].timer?.duration_seconds ?? undefined
								};
								data = data;
							}}
						/>
						Enable countdown for this slide
					</label>
					<p class="text-xs text-gray-500">Default is off for tabletop slides. Admin can still manually control discussion timer during play.</p>
					<input
						type="number"
						min="1"
						max="3600"
						placeholder="Optional override duration in seconds"
						class="w-full rounded-lg border border-gray-400 p-1.5 text-sm dark:bg-gray-600 outline-hidden"
						disabled={!(data.questions[selected_question].timer?.enabled ?? false)}
						value={data.questions[selected_question].timer?.duration_seconds ?? ''}
						oninput={(e) => {
							const val = parseInt(e.currentTarget.value);
							data.questions[selected_question].timer = {
								enabled: data.questions[selected_question].timer?.enabled ?? false,
								duration_seconds: isNaN(val) ? undefined : val
							};
							data = data;
						}}
					/>
				</div>
				<!-- Allowed Roles -->
				<div class="flex flex-col gap-1">
					<span class="text-sm font-medium">Allowed Roles (who can answer)</span>
					<div class="flex flex-wrap gap-1">
						{#each data.roles ?? [] as role}
							<label class="inline-flex items-center gap-1 text-sm">
								<input
									type="checkbox"
									checked={(data.questions[selected_question].allowed_roles ?? []).includes(role)}
									onchange={() => {
										const q = data.questions[selected_question];
										const current = q.allowed_roles ?? [];
										if (current.includes(role)) {
											q.allowed_roles = current.filter(r => r !== role);
										} else {
											q.allowed_roles = [...current, role];
										}
										if (q.allowed_roles.length === 0) q.allowed_roles = undefined;
										data = data;
									}}
								/>
								{role}
							</label>
						{/each}
					</div>
					{#if !data.roles?.length}
						<p class="text-xs text-gray-500">Add roles in quiz settings first.</p>
					{/if}
				</div>
				<!-- Decision Mode -->
				<div class="flex flex-col gap-1">
					<span class="text-sm font-medium">Decision Mode</span>
					<select
						class="rounded-lg border border-gray-400 p-1.5 text-sm dark:bg-gray-600 outline-hidden"
						value={data.questions[selected_question].decision_mode ?? 'majority_vote'}
						onchange={(e) => {
							data.questions[selected_question].decision_mode = e.currentTarget.value === 'majority_vote' ? undefined : e.currentTarget.value;
							data = data;
						}}
					>
						<option value="majority_vote">Majority Vote</option>
						<option value="facilitator_only">Facilitator Only</option>
					</select>
				</div>
				<!-- Default Next Question -->
				<div class="flex flex-col gap-1">
					<span class="text-sm font-medium">Default Next Question</span>
					<select
						class="rounded-lg border border-gray-400 p-1.5 text-sm dark:bg-gray-600 outline-hidden"
						value={data.questions[selected_question].default_next_question_id ?? ''}
						onchange={(e) => {
							data.questions[selected_question].default_next_question_id = e.currentTarget.value || undefined;
							data = data;
						}}
					>
						<option value="">Sequential (next in list)</option>
						{#each data.questions as q, qi}
							{#if qi !== selected_question}
								<option value={q.id ?? ''}>{qi + 1}. {q.question?.replace(/<[^>]*>/g, '').slice(0, 40) || 'Untitled'}</option>
							{/if}
						{/each}
					</select>
				</div>
				<!-- Facilitator Notes -->
				<div class="flex flex-col gap-1">
					<span class="text-sm font-medium">Facilitator Notes (private, admin only)</span>
					<textarea
						placeholder="Private notes for the facilitator (markdown supported)..."
						class="w-full rounded-lg border border-gray-400 p-2 text-sm dark:bg-gray-600 outline-hidden resize-y min-h-[80px]"
						value={data.questions[selected_question].facilitator_notes ?? ''}
						oninput={(e) => {
							data.questions[selected_question].facilitator_notes = e.currentTarget.value || undefined;
							data = data;
						}}
					></textarea>
				</div>
				<!-- Discussion Timer -->
				<div class="flex flex-col gap-1">
					<span class="text-sm font-medium">Discussion Timer (seconds)</span>
					<p class="text-xs text-gray-500">Separate from answer timer. Used for group discussion phase.</p>
					<input
						type="number"
						min="0"
						max="3600"
						placeholder="e.g. 300 for 5 minutes"
						class="w-full rounded-lg border border-gray-400 p-1.5 text-sm dark:bg-gray-600 outline-hidden"
						value={data.questions[selected_question].discussion_time ?? ''}
						oninput={(e) => {
							const val = parseInt(e.currentTarget.value);
							data.questions[selected_question].discussion_time = isNaN(val) ? undefined : val;
							data = data;
						}}
					/>
				</div>
				<!-- Objective Category -->
				<div class="flex flex-col gap-1">
					<span class="text-sm font-medium">Scoring Objective</span>
					<p class="text-xs text-gray-500">Applies a score multiplier based on the exercise objective this question targets.</p>
					<select
						class="rounded-lg border border-gray-400 p-1.5 text-sm dark:bg-gray-600 outline-hidden"
						value={data.questions[selected_question].objective ?? ''}
						onchange={(e) => {
							data.questions[selected_question].objective = e.currentTarget.value || undefined;
							data = data;
						}}
					>
						<option value="">None (1.0×)</option>
						<option value="Detection">Detection (1.0×)</option>
						<option value="Containment">Containment (1.2×)</option>
						<option value="Recovery">Recovery (1.1×)</option>
						<option value="Communication">Communication (0.9×)</option>
					</select>
				</div>
				<!-- SLA Checkpoints -->
				<div class="flex flex-col gap-2">
					<div class="flex items-center justify-between">
						<span class="text-sm font-medium">SLA Checkpoints</span>
						<button
							type="button"
							class="rounded border border-gray-400 px-2 py-0.5 text-xs hover:bg-gray-100 dark:hover:bg-gray-600"
							onclick={() => {
								const current = data.questions[selected_question].sla_checkpoints ?? [];
								data.questions[selected_question].sla_checkpoints = [
									...current,
									{ deadline_seconds: 120, bonus_points: 50, penalty_points: 25, description: 'Response deadline' }
								];
								data = data;
							}}
						>+ Add</button>
					</div>
					<p class="text-xs text-gray-500">Bonus awarded if question advances before deadline; penalty if still active after deadline.</p>
					{#each (data.questions[selected_question].sla_checkpoints ?? []) as cp, ci}
						<div class="rounded-lg border border-gray-300 dark:border-gray-600 p-2 flex flex-col gap-1.5">
							<input
								type="text"
								placeholder="Description"
								class="w-full rounded border border-gray-300 dark:border-gray-600 p-1 text-xs dark:bg-gray-700"
								value={cp.description}
								oninput={(e) => {
									data.questions[selected_question].sla_checkpoints![ci].description = e.currentTarget.value;
									data = data;
								}}
							/>
							<div class="grid grid-cols-3 gap-1">
								<label class="flex flex-col gap-0.5">
									<span class="text-[10px] text-gray-500">Deadline (s)</span>
									<input type="number" min="1" class="rounded border border-gray-300 dark:border-gray-600 p-1 text-xs dark:bg-gray-700"
										value={cp.deadline_seconds}
										oninput={(e) => { data.questions[selected_question].sla_checkpoints![ci].deadline_seconds = parseInt(e.currentTarget.value) || 60; data = data; }}
									/>
								</label>
								<label class="flex flex-col gap-0.5">
									<span class="text-[10px] text-gray-500">Bonus pts</span>
									<input type="number" min="0" class="rounded border border-gray-300 dark:border-gray-600 p-1 text-xs dark:bg-gray-700"
										value={cp.bonus_points}
										oninput={(e) => { data.questions[selected_question].sla_checkpoints![ci].bonus_points = parseInt(e.currentTarget.value) || 0; data = data; }}
									/>
								</label>
								<label class="flex flex-col gap-0.5">
									<span class="text-[10px] text-gray-500">Penalty pts</span>
									<input type="number" min="0" class="rounded border border-gray-300 dark:border-gray-600 p-1 text-xs dark:bg-gray-700"
										value={cp.penalty_points}
										oninput={(e) => { data.questions[selected_question].sla_checkpoints![ci].penalty_points = parseInt(e.currentTarget.value) || 0; data = data; }}
									/>
								</label>
							</div>
							<button
								type="button"
								class="self-end text-[10px] text-red-500 hover:text-red-700"
								onclick={() => {
									const cps = data.questions[selected_question].sla_checkpoints ?? [];
									data.questions[selected_question].sla_checkpoints = cps.filter((_, j) => j !== ci);
									data = data;
								}}
							>Remove</button>
						</div>
					{/each}
				</div>
			{/if}
			<div class="mt-auto w-full">
				<BrownButton onclick={() => (advanced_options_open = false)}
					>{$t('words.close')}</BrownButton
				>
			</div>
		</div>
	</div>
{/if}
