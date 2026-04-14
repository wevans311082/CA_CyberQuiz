<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { QuizQuestionType } from '$lib/quiz_types';
	import type { QuizData, Inject, SituationStatus } from '$lib/quiz_types';
	import type { Socket } from 'socket.io-client';
	import { getLocalization } from '$lib/i18n';

	interface Props {
		bg_color: string;
		selected_question: number;
		quiz_data: QuizData;
		timer_res: string;
		final_results: any;
		socket: Socket;
		game_token: string;
		question_results: any;
		shown_question_now: number;
		socket_diagnostics_enabled: boolean;
		on_toggle_socket_diagnostics: () => void;
		scenario_type?: string;
		tie_pending?: boolean;
		tie_votes?: Record<string, number>;
		facilitator_notes?: string | null;
		situation_status?: SituationStatus;
	}

	let {
		bg_color,
		selected_question,
		quiz_data,
		timer_res = $bindable(),
		final_results,
		socket,
		game_token,
		question_results,
		shown_question_now,
		socket_diagnostics_enabled,
		on_toggle_socket_diagnostics,
		scenario_type = undefined,
		tie_pending = false,
		tie_votes = {},
		facilitator_notes = null,
		situation_status = $bindable({ severity: 'low', phase: 'Detection', affected_systems: [], summary: '' })
	}: Props = $props();

	let is_tabletop = $derived(scenario_type === 'tabletop');
	let override_question_id = $state('');
	let inject_panel_open = $state(false);
	let situation_panel_open = $state(false);
	let adhoc_inject_title = $state('');
	let adhoc_inject_content = $state('');
	let adhoc_inject_severity = $state<'info' | 'warning' | 'critical'>('info');
	let new_affected_system = $state('');

	const { t } = getLocalization();
	const set_question_number = (q_number: number) => {
		if (is_tabletop && selected_question >= 0) {
			// In tabletop mode, use branching-aware advance instead of sequential
			advance_tabletop();
		} else {
			socket.emit('set_question_number', q_number.toString());
		}
	};

	const get_question_results = () => {
		socket.emit('get_question_results', {
			game_id: game_token,
			question_number: shown_question_now
		});
	};
	const show_solutions = () => {
		socket.emit('show_solutions', {});
		timer_res = '0';
	};

	const get_final_results = () => {
		socket.emit('get_final_results', {});
	};

	const advance_tabletop = () => {
		socket.emit('advance_tabletop', {});
	};

	const force_next_question = () => {
		if (override_question_id) {
			socket.emit('force_next_question', { question_id: override_question_id });
			override_question_id = '';
		}
	};

	const resolve_tie = (answer_text: string) => {
		socket.emit('resolve_tie', { answer_text });
	};

	const push_predefined_inject = (inject: Inject) => {
		socket.emit('push_inject', { inject_id: inject.id });
	};

	const push_adhoc_inject = () => {
		if (!adhoc_inject_title.trim()) return;
		socket.emit('push_inject', {
			title: adhoc_inject_title,
			content: adhoc_inject_content,
			severity: adhoc_inject_severity
		});
		adhoc_inject_title = '';
		adhoc_inject_content = '';
		adhoc_inject_severity = 'info';
	};

	const update_situation = () => {
		socket.emit('update_situation', { ...situation_status });
	};
</script>

<div
	class="fixed top-0 w-full h-10 z-20 grid grid-cols-2"
	style="background: {bg_color ? bg_color : 'transparent'}"
	class:text-black={bg_color}
>
	<p class="mr-auto ml-0 col-start-1 col-end-1">
		{selected_question === -1 ? '0' : selected_question + 1}
		/{quiz_data.questions.length}
	</p>
	<div class="justify-self-center col-start-2 col-end-2">
		<button onclick={on_toggle_socket_diagnostics} class="admin-button">
			Diagnostics: {socket_diagnostics_enabled ? 'On' : 'Off'}
		</button>
	</div>
	<div class="justify-self-end ml-auto mr-0 col-start-3 col-end-3">
		{#if selected_question + 1 === quiz_data.questions.length && ((timer_res === '0' && question_results !== null) || quiz_data?.questions?.[selected_question]?.type === QuizQuestionType.SLIDE)}
			{#if JSON.stringify(final_results) === JSON.stringify([null])}
				<button onclick={get_final_results} class="admin-button"
					>{$t('admin_page.get_final_results')}
				</button>
			{/if}
		{:else if timer_res === '0' || selected_question === -1}
			{#if (selected_question + 1 !== quiz_data.questions.length && question_results !== null) || selected_question === -1}
				<button
					onclick={() => {
						set_question_number(selected_question + 1);
					}}
					class="admin-button"
					>{$t('admin_page.next_question', { question: selected_question + 2 })}
				</button>
			{/if}
			{#if question_results === null && selected_question !== -1}
				{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
					<button
						onclick={() => {
							set_question_number(selected_question + 1);
						}}
						class="admin-button"
						>{$t('admin_page.next_question', { question: selected_question + 2 })}
					</button>
				{:else if quiz_data.questions[selected_question]?.hide_results === true}
					<button
						onclick={() => {
							get_question_results();
							setTimeout(() => {
								set_question_number(selected_question + 1);
							}, 200);
						}}
						class="admin-button"
						>{$t('admin_page.next_question', { question: selected_question + 2 })}
					</button>
				{:else}
					<button onclick={get_question_results} class="admin-button"
						>{$t('admin_page.show_results')}
					</button>
				{/if}
			{/if}
		{:else if selected_question !== -1}
			{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
				<button
					onclick={() => {
						set_question_number(selected_question + 1);
					}}
					class="admin-button"
					>{$t('admin_page.next_question', { question: selected_question + 2 })}
				</button>
			{:else}
				<button onclick={show_solutions} class="admin-button"
					>{$t('admin_page.stop_time_and_solutions')}
				</button>
			{/if}
		{/if}
	</div>
</div>
{#if is_tabletop && selected_question >= 0}
	<div
		class="fixed top-10 w-full h-8 z-20 flex items-center gap-3 px-4"
		style="background: {bg_color ? bg_color : 'rgba(0,0,0,0.05)'}"
	>
		<button onclick={advance_tabletop} class="admin-button text-xs">Advance (Branch)</button>
		<select
			class="rounded border border-gray-400 px-2 py-0.5 text-xs dark:bg-gray-700 outline-hidden"
			bind:value={override_question_id}
		>
			<option value="">Override → ...</option>
			{#each quiz_data.questions as q, qi}
				{#if qi !== selected_question}
					<option value={q.id ?? ''}>{qi + 1}. {q.question?.replace(/<[^>]*>/g, '').slice(0, 30) || 'Q' + (qi + 1)}</option>
				{/if}
			{/each}
		</select>
		{#if override_question_id}
			<button onclick={force_next_question} class="admin-button text-xs bg-amber-600">Override</button>
		{/if}
		{#if tie_pending}
			<span class="ml-2 text-xs font-semibold text-red-600">TIE — pick a winner:</span>
			{#each Object.entries(tie_votes) as [answer, count]}
				<button onclick={() => resolve_tie(answer)} class="admin-button text-xs bg-red-500" title="{count} votes">{answer}</button>
			{/each}
		{/if}
		<div class="ml-auto flex gap-2">
			<button onclick={() => inject_panel_open = !inject_panel_open} class="admin-button text-xs"
				class:bg-orange-600={inject_panel_open}>Injects</button>
			<button onclick={() => situation_panel_open = !situation_panel_open} class="admin-button text-xs"
				class:bg-purple-600={situation_panel_open}>Situation Room</button>
		</div>
	</div>
	<!-- Facilitator Notes -->
	{#if facilitator_notes}
		<div class="fixed top-[4.5rem] left-4 z-30 max-w-sm rounded-lg border border-blue-400 bg-blue-50/95 p-3 shadow-lg dark:bg-blue-900/90 dark:border-blue-700">
			<h4 class="text-xs font-bold uppercase text-blue-700 dark:text-blue-300 mb-1">Facilitator Notes</h4>
			<p class="text-sm whitespace-pre-wrap text-blue-900 dark:text-blue-100">{facilitator_notes}</p>
		</div>
	{/if}
	<!-- Inject Panel -->
	{#if inject_panel_open}
		<div class="fixed top-[4.5rem] right-4 z-30 w-80 max-h-[60vh] overflow-auto rounded-lg border border-orange-400 bg-white/95 p-4 shadow-xl dark:bg-gray-800/95 dark:border-orange-600">
			<h3 class="text-sm font-bold mb-3 text-orange-700 dark:text-orange-300">Push Inject</h3>
			<!-- Pre-defined injects -->
			{#if quiz_data.injects?.length}
				<div class="mb-3">
					<span class="text-xs font-semibold text-gray-600 dark:text-gray-400">Pre-defined:</span>
					{#each quiz_data.injects as inject}
						<button
							class="mt-1 w-full text-left rounded border p-2 text-xs hover:bg-orange-50 dark:hover:bg-orange-900/30 transition"
							class:border-blue-300={inject.severity === 'info'}
							class:border-yellow-400={inject.severity === 'warning'}
							class:border-red-400={inject.severity === 'critical'}
							onclick={() => push_predefined_inject(inject)}
						>
							<span class="font-semibold">{inject.title}</span>
							<span class="ml-1 text-[10px] uppercase rounded px-1"
								class:bg-blue-100={inject.severity === 'info'}
								class:bg-yellow-100={inject.severity === 'warning'}
								class:bg-red-100={inject.severity === 'critical'}
								class:text-blue-700={inject.severity === 'info'}
								class:text-yellow-700={inject.severity === 'warning'}
								class:text-red-700={inject.severity === 'critical'}
							>{inject.severity}</span>
						</button>
					{/each}
				</div>
			{/if}
			<!-- Ad-hoc inject form -->
			<div class="border-t border-gray-300 dark:border-gray-600 pt-3">
				<span class="text-xs font-semibold text-gray-600 dark:text-gray-400">Ad-hoc inject:</span>
				<input
					type="text"
					bind:value={adhoc_inject_title}
					placeholder="Title"
					class="mt-1 w-full rounded border border-gray-400 p-1.5 text-xs dark:bg-gray-700 outline-hidden"
				/>
				<textarea
					bind:value={adhoc_inject_content}
					placeholder="Content (markdown)"
					class="mt-1 w-full rounded border border-gray-400 p-1.5 text-xs dark:bg-gray-700 outline-hidden resize-y min-h-[40px]"
				></textarea>
				<div class="mt-1 flex gap-2 items-center">
					<select bind:value={adhoc_inject_severity} class="rounded border border-gray-400 p-1 text-xs dark:bg-gray-700 outline-hidden">
						<option value="info">Info</option>
						<option value="warning">Warning</option>
						<option value="critical">Critical</option>
					</select>
					<button
						class="ml-auto rounded bg-orange-600 px-3 py-1 text-xs text-white hover:bg-orange-700 disabled:opacity-50"
						disabled={!adhoc_inject_title.trim()}
						onclick={push_adhoc_inject}
					>Push</button>
				</div>
			</div>
		</div>
	{/if}
	<!-- Situation Room Panel -->
	{#if situation_panel_open}
		<div class="fixed top-[4.5rem] right-[22rem] z-30 w-80 max-h-[60vh] overflow-auto rounded-lg border border-purple-400 bg-white/95 p-4 shadow-xl dark:bg-gray-800/95 dark:border-purple-600">
			<h3 class="text-sm font-bold mb-3 text-purple-700 dark:text-purple-300">Situation Room</h3>
			<div class="flex flex-col gap-2">
				<div>
					<span class="text-xs font-semibold">Severity</span>
					<select
						bind:value={situation_status.severity}
						class="w-full rounded border border-gray-400 p-1.5 text-xs dark:bg-gray-700 outline-hidden"
					>
						<option value="low">Low</option>
						<option value="medium">Medium</option>
						<option value="high">High</option>
						<option value="critical">Critical</option>
					</select>
				</div>
				<div>
					<span class="text-xs font-semibold">Incident Phase</span>
					<select
						bind:value={situation_status.phase}
						class="w-full rounded border border-gray-400 p-1.5 text-xs dark:bg-gray-700 outline-hidden"
					>
						<option value="Detection">Detection</option>
						<option value="Containment">Containment</option>
						<option value="Eradication">Eradication</option>
						<option value="Recovery">Recovery</option>
						<option value="Lessons Learned">Lessons Learned</option>
					</select>
				</div>
				<div>
					<span class="text-xs font-semibold">Affected Systems</span>
					<div class="flex flex-wrap gap-1 mt-1">
						{#each situation_status.affected_systems as sys, i}
							<span class="inline-flex items-center gap-1 rounded-full bg-purple-600 px-2 py-0.5 text-[10px] text-white">
								{sys}
								<button type="button" class="hover:text-red-200" onclick={() => {
									situation_status.affected_systems = situation_status.affected_systems.filter((_, idx) => idx !== i);
								}}>&times;</button>
							</span>
						{/each}
					</div>
					<div class="flex gap-1 mt-1">
						<input
							type="text"
							bind:value={new_affected_system}
							placeholder="Add system"
							class="flex-1 rounded border border-gray-400 p-1 text-xs dark:bg-gray-700 outline-hidden"
							onkeydown={(e) => {
								if (e.key === 'Enter') {
									e.preventDefault();
									const v = new_affected_system.trim();
									if (v) {
										situation_status.affected_systems = [...situation_status.affected_systems, v];
										new_affected_system = '';
									}
								}
							}}
						/>
						<button
							type="button"
							class="rounded bg-purple-600 px-2 py-0.5 text-[10px] text-white hover:bg-purple-700"
							onclick={() => {
								const v = new_affected_system.trim();
								if (v) {
									situation_status.affected_systems = [...situation_status.affected_systems, v];
									new_affected_system = '';
								}
							}}
						>+</button>
					</div>
				</div>
				<div>
					<span class="text-xs font-semibold">Summary</span>
					<textarea
						bind:value={situation_status.summary}
						placeholder="Current situation summary..."
						class="w-full rounded border border-gray-400 p-1.5 text-xs dark:bg-gray-700 outline-hidden resize-y min-h-[40px]"
					></textarea>
				</div>
				<button
					class="mt-1 w-full rounded bg-purple-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-purple-700"
					onclick={update_situation}
				>Broadcast Update</button>
			</div>
		</div>
	{/if}
{/if}
