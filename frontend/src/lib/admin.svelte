<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { QuizData, Inject, SituationStatus } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import { get_question_title } from '$lib/admin.ts';
	import type { PlayerAnswer } from '$lib/admin.ts';
	import { socket } from './socket';
	import { QuizQuestionType } from '$lib/quiz_types';
	import Spinner from '$lib/Spinner.svelte';
	import Controls from '$lib/play/admin/controls.svelte';
	import Question from '$lib/play/admin/question.svelte';
	import BranchMap from '$lib/play/admin/BranchMap.svelte';

	const { t } = getLocalization();
	const default_colors = ['#D6EDC9', '#B07156', '#7F7057', '#4E6E58'];

	let question_results = $state(null);
	let selected_question = $state(-1);
	let timer_res: string = $state();
	let shown_question_now: number = $state();
	let final_results_clicked = $state(false);
	let timer_interval: NodeJS.Timeout;
	let answer_count = $state(0);

	// Tabletop state
	let tie_pending = $state(false);
	let tie_votes = $state<Record<string, number>>({});
	let admin_player_roles = $state<Record<string, string>>({});
	let role_assign_username = $state('');
	let role_assign_role = $state('');

	// Facilitator notes & inject/situation state
	let facilitator_notes = $state<string | null>(null);
	let situation_status = $state<SituationStatus>({ severity: 'low', phase: 'Detection', affected_systems: [], summary: '' });

	interface Props {
		game_token: string;
		quiz_data: QuizData;
		bg_color: string;
		final_results?: Array<null> | Array<Array<PlayerAnswer>>;
		final_results_avatar_map?: Record<string, any>;
		control_visible: boolean;
		player_scores: any;
		socket_diagnostics_enabled: boolean;
		on_toggle_socket_diagnostics: () => void;
	}

	let {
		game_token,
		quiz_data = $bindable(),
		bg_color,
		final_results = $bindable([null]),
		final_results_avatar_map = $bindable({}),
		control_visible,
		player_scores = $bindable(),
		socket_diagnostics_enabled = $bindable(false),
		on_toggle_socket_diagnostics
	}: Props = $props();

	socket.on('get_question_results', () => {
		console.log('get_question_results');
	});
	socket.on('set_question_number', (data) => {
		timer_res = '0';
		clearInterval(timer_interval);
		question_results = null;
		shown_question_now = data.question_index;
		timer_res = quiz_data.questions[data.question_index].time;
		selected_question = selected_question + 1;
		answer_count = 0;
		timer(timer_res);
	});

	socket.on('solutions', (_) => {
		timer_res = '0';
		clearInterval(timer_interval);
	});

	socket.on('final_results', (data) => {
		// data = JSON.parse(data);
		final_results_clicked = true;
		timer_res = '0';
		if (data && typeof data === 'object' && 'results' in data) {
			final_results = data.results;
			final_results_avatar_map = data.avatar_map ?? {};
		} else {
			final_results = data;
			final_results_avatar_map = {};
		}
	});

	socket.on('everyone_answered', (_) => {
		timer_res = '0';
	});

	socket.on('question_results', (data) => {
		console.log('question_results:', data);
		question_results = data;
		timer_res = '0';
	});

	socket.on('player_answer', (_) => {
		answer_count += 1;
	});

	// Tabletop admin events
	socket.on('tie_detected', (data) => {
		tie_pending = true;
		tie_votes = data?.votes ?? {};
	});
	socket.on('branch_resolved', (_) => {
		tie_pending = false;
		tie_votes = {};
	});
	socket.on('roles_updated', (data) => {
		if (data?.player_roles) {
			admin_player_roles = data.player_roles;
		}
	});
	socket.on('facilitator_notes', (data) => {
		facilitator_notes = data?.notes ?? null;
	});
	socket.on('situation_updated', (data) => {
		if (data) {
			situation_status = { ...situation_status, ...data };
		}
	});

	const timer = (time: string) => {
		let seconds = Number(time);
		timer_interval = setInterval(() => {
			if (timer_res === '0') {
				clearInterval(timer_interval);
				return;
			} else {
				seconds--;
			}

			timer_res = seconds.toString();
		}, 1000);
	};
</script>

{#if control_visible}
	<Controls
		{bg_color}
		{selected_question}
		{quiz_data}
		bind:timer_res
		{final_results}
		{socket}
		{question_results}
		{game_token}
		{shown_question_now}
		{socket_diagnostics_enabled}
		{on_toggle_socket_diagnostics}
		scenario_type={quiz_data.scenario_type}
		{tie_pending}
		{tie_votes}
		{facilitator_notes}
		bind:situation_status
	/>
{/if}
{#if quiz_data.scenario_type === 'tabletop' && quiz_data.questions?.length}
	<BranchMap questions={quiz_data.questions} {selected_question} />
{/if}
{#if timer_res !== '0' && selected_question >= 0}
	<span
		class="fixed top-0 bg-red-500 h-8 transition-all"
		class:mt-10={control_visible}
		style="width: {(100 / parseInt(quiz_data.questions[selected_question].time)) *
			parseInt(timer_res)}vw"
	></span>
{/if}

<div class="w-full h-full" class:pt-28={control_visible} class:pt-12={!control_visible}>
	{#if timer_res !== undefined && !final_results_clicked && !question_results}
		<!-- Question is shown -->
		{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
			{#await import('$lib/play/admin/slide.svelte')}
				<Spinner my_20={false} />
			{:then c}
				<c.default question={quiz_data.questions[selected_question]} />
			{/await}
		{:else}
			<Question {quiz_data} {selected_question} {timer_res} {answer_count} {default_colors} />
		{/if}
	{/if}
	<br />
	{#if timer_res === '0' && JSON.stringify(final_results) === JSON.stringify( [null] ) && quiz_data.questions[selected_question].type !== QuizQuestionType.SLIDE && question_results !== null && quiz_data.questions[selected_question]?.hide_results !== true}
		{#if question_results === undefined}
			{#if !final_results_clicked}
				<div class="w-full flex justify-center">
					<h1 class="text-3xl">{$t('admin_page.no_answers')}</h1>
				</div>
			{/if}
		{:else if quiz_data.questions[selected_question].type === QuizQuestionType.VOTING}
			{#await import('$lib/play/admin/voting_results.svelte')}
				<Spinner />
			{:then c}
				<c.default
					data={question_results}
					question={quiz_data.questions[selected_question]}
				/>
			{/await}
		{:else}
			{#await import('$lib/play/admin/results.svelte')}
				<Spinner />
			{:then c}
				<c.default
					bind:data={player_scores}
					question={quiz_data.questions[selected_question]}
					new_data={question_results}
				/>
			{/await}
		{/if}
	{/if}
	<br />
	{#if selected_question === -1}
		<div class="flex flex-col justify-center w-screen h-full">
			<h1 class="text-7xl text-center">{@html quiz_data.title}</h1>
			<p class="text-3xl pt-8 text-center">{@html quiz_data.description}</p>
			{#if quiz_data.cover_image}
				<div class="flex justify-center align-middle items-center">
					<div class="h-[30vh] m-auto w-auto mt-12">
						<img
							class="max-h-full max-w-full block"
							src="/api/v1/storage/download/{quiz_data.cover_image}"
							alt="Not provided"
						/>
					</div>
				</div>
			{/if}
			{#if quiz_data.scenario_type === 'tabletop' && quiz_data.roles?.length}
				<div class="mx-auto mt-8 w-full max-w-lg rounded-xl border border-gray-300 bg-white/80 p-6 dark:border-gray-600 dark:bg-gray-800/80">
					<h2 class="mb-4 text-xl font-semibold text-center">Assign Player Roles</h2>
					<div class="flex flex-col gap-3">
						{#each Object.entries(admin_player_roles) as [player, role]}
							<div class="flex items-center justify-between gap-2 rounded-lg bg-gray-100 p-2 text-sm dark:bg-gray-700">
								<span class="font-medium">{player}</span>
								<span class="rounded-full bg-teal-600 px-2 py-0.5 text-xs text-white">{role}</span>
							</div>
						{/each}
					</div>
					<div class="mt-4 flex items-center gap-2">
						<input
							type="text"
							placeholder="Username"
							bind:value={role_assign_username}
							class="flex-1 rounded-lg border border-gray-400 p-2 text-sm dark:bg-gray-700 outline-hidden"
						/>
						<select
							bind:value={role_assign_role}
							class="rounded-lg border border-gray-400 p-2 text-sm dark:bg-gray-700 outline-hidden"
						>
							<option value="">Select Role</option>
							{#each quiz_data.roles as r}
								<option value={r}>{r}</option>
							{/each}
						</select>
						<button
							type="button"
							class="rounded-lg bg-teal-600 px-3 py-2 text-sm font-semibold text-white hover:bg-teal-700 disabled:opacity-50"
							disabled={!role_assign_username || !role_assign_role}
							onclick={() => {
								socket.emit('assign_role', { username: role_assign_username, role: role_assign_role });
								role_assign_username = '';
								role_assign_role = '';
							}}
						>Assign</button>
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
