<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/state';
	import { QuizQuestionType } from '$lib/quiz_types';
	import type { QuizData, Inject, SituationStatus, TimelineEvent, ReferenceDocument } from '$lib/quiz_types';
	import type { Player } from '$lib/admin';
	import type { Socket } from 'socket.io-client';
	import { getLocalization } from '$lib/i18n';
	import RolesPanel from '$lib/play/RolesPanel.svelte';
	import FacilitatorDock from './FacilitatorDock.svelte';
	import FacilitatorTimeline from './FacilitatorTimeline.svelte';
	import InjectPreviewModal, { type InjectPreviewPayload } from './InjectPreviewModal.svelte';
	import { QUICK_INJECT_PRESETS } from '$lib/facilitator/inject_presets';
	import {
		buildFacilitatorTimeline,
		normalizeInjectsLog,
		type InjectLogEntry,
		type SituationLogEntry
	} from '$lib/facilitator/timeline';

	import EmojiPanel from './EmojiPanel.svelte';
	import RehearsalPlayerSimulator from './RehearsalPlayerSimulator.svelte';

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
		raised_hands?: string[];
		player_roles?: Record<string, string>;
		players?: Player[];
		scoreboard_data?: { ranked: [string, number][]; scores: Record<string, number> } | null;
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
		situation_status = $bindable({ severity: 'low', phase: 'Detection', affected_systems: [], summary: '' }),
		raised_hands = [],
		player_roles = {},
		players = [],
		scoreboard_data = null
	}: Props = $props();

	let is_tabletop = $derived(scenario_type === 'tabletop');
	let override_question_id = $state('');
	let facilitator_dock_open = $state(false);
	let facilitator_dock_tab = $state<'situation' | 'injects' | 'references' | 'rehearsal' | 'hands' | 'roles' | 'timeline' | 'rewards'>('situation');
	let bonus_target = $state('');
	let bonus_amount = $state(25);
	let bonus_reason = $state('Great participation');
	let injects_log = $state<InjectLogEntry[]>([]);
	let situation_log = $state<SituationLogEntry[]>([]);
	let inject_preview_open = $state(false);
	let inject_preview_payload = $state<InjectPreviewPayload | null>(null);
	let rehearsal_active = $state(false);
	let rehearsal_question = $state(0);
	let rehearsal_clock_speed = $state(1);
	let rehearsal_snapshot = $state<{ question: number; speed: number } | null>(null);
	let rehearsal_snapshots = $state<Array<{ question: number; speed: number; created_at: string }>>([]);
	let rehearsal_answers = $state<Record<string, string>>({});

	const timeline_events = $derived(buildFacilitatorTimeline(injects_log, situation_log));

	const open_facilitator_tab = (tab: 'situation' | 'injects' | 'references' | 'rehearsal' | 'hands' | 'roles' | 'timeline' | 'rewards') => {
		facilitator_dock_tab = tab;
		facilitator_dock_open = true;
		refresh_situation_data();
	};

	const refresh_situation_data = () => {
		socket.emit('get_situation', {});
	};

	const open_projector_display = () => {
		const token = page.url.searchParams.get('token');
		const game_id = page.url.searchParams.get('game_id') ?? game_token;
		const pin = quiz_data?.game_pin ?? page.url.searchParams.get('pin');
		if (!token || !game_id || !pin) return;
		window.open(`/projector?token=${encodeURIComponent(token)}&game_id=${encodeURIComponent(game_id)}&pin=${encodeURIComponent(pin)}&connect=1`, '_blank', 'noopener,noreferrer');
	};
	const spotlight_policy = (document: ReferenceDocument) => socket.emit('spotlight_policy', { document_id: document.id });
	const start_rehearsal = () => { rehearsal_active = true; facilitator_dock_tab = 'rehearsal'; socket.emit('create_rehearsal', {}); };
	const reset_rehearsal = () => socket.emit('reset_rehearsal', {});
	const exit_rehearsal = () => { socket.emit('exit_rehearsal', {}); rehearsal_active = false; rehearsal_snapshot = null; rehearsal_snapshots = []; };
	const rehearsal_next = () => { const next = Math.min(quiz_data.questions.length - 1, rehearsal_question + 1); rehearsal_question = next; socket.emit('update_rehearsal', { question: next, speed: rehearsal_clock_speed }); };
	const rehearsal_previous = () => { const previous = Math.max(0, rehearsal_question - 1); rehearsal_question = previous; socket.emit('update_rehearsal', { question: previous, speed: rehearsal_clock_speed }); };
	const save_rehearsal_snapshot = () => socket.emit('snapshot_rehearsal', {});
	const restore_rehearsal_snapshot = (index: number) => socket.emit('restore_rehearsal', { index });
	const submit_rehearsal_answer = (answer: string) => socket.emit('submit_rehearsal_answer', { question: rehearsal_question, answer });
	const update_rehearsal_speed = () => socket.emit('update_rehearsal', { question: rehearsal_question, speed: rehearsal_clock_speed });
	const onRehearsalState = (state: { active?: boolean; question?: number; speed?: number; answers?: Record<string, { answer?: string }>; snapshots?: Array<{ question: number; speed: number; created_at: string }> }) => { rehearsal_active = Boolean(state?.active); if (typeof state?.question === 'number') rehearsal_question = state.question; if (typeof state?.speed === 'number') rehearsal_clock_speed = state.speed; rehearsal_answers = Object.fromEntries(Object.entries(state?.answers ?? {}).map(([key, value]) => [key, value.answer ?? ''])); rehearsal_snapshots = state?.snapshots ?? []; };
	$effect(() => { if (!rehearsal_active && selected_question >= 0) rehearsal_question = selected_question; });
	const on_local_console_request = (event: Event) => {
		const tab = (event as CustomEvent<{ tab?: 'situation' | 'injects' | 'hands' | 'roles' | 'timeline' }>).detail?.tab;
		open_facilitator_tab(tab ?? 'situation');
	};
	onMount(() => window.addEventListener('cyberask:facilitator-console', on_local_console_request));
	onDestroy(() => window.removeEventListener('cyberask:facilitator-console', on_local_console_request));
	let score_review_open = $state(false);
	let score_review_sheet = $state<any | null>(null);
	let adhoc_inject_title = $state('');

	// Discussion timer admin state
	let disc_running = $state(false);
	let disc_remaining = $state(0);
	let disc_total = $state(0);
	let disc_custom_seconds = $state<number | null>(null); // override duration input
	let disc_interval: ReturnType<typeof setInterval> | null = null;

	const disc_effective_duration = $derived(
		disc_custom_seconds != null && disc_custom_seconds > 0
			? disc_custom_seconds
			: (selected_question >= 0 && quiz_data?.questions?.[selected_question]?.discussion_time) || 300
	);

	const disc_start = () => {
		const duration = disc_effective_duration;
		socket.emit('start_discussion_timer', { duration });
	};

	const disc_pause = () => {
		socket.emit('pause_discussion_timer', {});
	};

	const disc_resume = () => {
		socket.emit('resume_discussion_timer', {});
	};

	const disc_stop = () => {
		socket.emit('stop_discussion_timer', {});
	};

	const disc_fmt = (s: number) => {
		const m = Math.floor(s / 60);
		const sec = Math.floor(s % 60);
		return `${m}:${sec.toString().padStart(2, '0')}`;
	};

	const onDiscussionTimerStarted = (data: { duration: number; server_timestamp: string }) => {
		disc_running = true;
		disc_total = data.duration;
		const serverStart = new Date(data.server_timestamp).getTime();
		if (disc_interval) clearInterval(disc_interval);
		disc_interval = setInterval(() => {
			const elapsed = (Date.now() - serverStart) / 1000;
			const rem = Math.max(0, data.duration - elapsed);
			disc_remaining = rem;
			if (rem <= 0) {
				disc_running = false;
				if (disc_interval) { clearInterval(disc_interval); disc_interval = null; }
			}
		}, 250);
	};
	const award_bonus = () => {
		if (!bonus_target || bonus_amount < 1) return;
		socket.emit('award_bonus', { target: bonus_target, amount: bonus_amount, reason: bonus_reason });
		bonus_target = '';
	};
	const onDiscussionTimerPaused = (data: { remaining: number }) => {
		disc_running = false;
		disc_remaining = data.remaining;
		if (disc_interval) { clearInterval(disc_interval); disc_interval = null; }
	};
	const onDiscussionTimerStopped = () => {
		disc_running = false;
		disc_remaining = 0;
		disc_total = 0;
		if (disc_interval) { clearInterval(disc_interval); disc_interval = null; }
	};

	// Question answer timer (server-synced admin controls)
	let qtimer_running = $state(false);
	let qtimer_remaining = $state(0);
	let qtimer_total = $state(0);
	let qtimer_custom_seconds = $state<number | null>(null);
	let qtimer_interval: ReturnType<typeof setInterval> | null = null;

	const qtimer_effective_duration = $derived.by(() => {
		if (qtimer_custom_seconds != null && qtimer_custom_seconds > 0) {
			return qtimer_custom_seconds;
		}
		
		const question = quiz_data?.questions?.[selected_question];
		if (!question) return 60;
		
		// Try timer.duration_seconds first (Phase 4 field)
		const dur_secs = question.timer?.duration_seconds;
		if (dur_secs != null && dur_secs > 0) return dur_secs;
		
		// Fall back to legacy time field, but validate it's a reasonable number
		const time_str = question.time;
		if (time_str) {
			const parsed = parseInt(time_str, 10);
			if (!isNaN(parsed) && parsed > 0 && parsed <= 7200) return parsed;
		}
		
		// Safe default: 60 seconds
		return 60;
	});

	const qtimer_start = () => {
		socket.emit('start_question_timer', { duration: qtimer_effective_duration });
	};
	const qtimer_pause = () => { socket.emit('pause_question_timer', {}); };
	const qtimer_resume = () => { socket.emit('resume_question_timer', {}); };
	const qtimer_stop = () => { socket.emit('stop_question_timer', {}); };

	const qtimer_fmt = (s: number) => {
		const m = Math.floor(s / 60);
		const sec = Math.floor(s % 60);
		return m > 0 ? `${m}:${sec.toString().padStart(2, '0')}` : `${Math.floor(s)}s`;
	};

	const onQuestionTimerStarted = (data: { duration: number; server_timestamp: string }) => {
		qtimer_running = true;
		qtimer_total = data.duration;
		const serverStart = new Date(data.server_timestamp).getTime();
		if (qtimer_interval) clearInterval(qtimer_interval);
		qtimer_interval = setInterval(() => {
			const elapsed = (Date.now() - serverStart) / 1000;
			const rem = Math.max(0, data.duration - elapsed);
			qtimer_remaining = rem;
			timer_res = Math.ceil(rem).toString();
			if (rem <= 0) {
				qtimer_running = false;
				if (qtimer_interval) { clearInterval(qtimer_interval); qtimer_interval = null; }
			}
		}, 250);
	};
	const onQuestionTimerPaused = (data: { remaining: number }) => {
		qtimer_running = false;
		qtimer_remaining = data.remaining;
		timer_res = Math.ceil(data.remaining).toString();
		if (qtimer_interval) { clearInterval(qtimer_interval); qtimer_interval = null; }
	};
	const onQuestionTimerStopped = () => {
		qtimer_running = false;
		qtimer_remaining = 0;
		qtimer_total = 0;
		timer_res = '0';
		if (qtimer_interval) { clearInterval(qtimer_interval); qtimer_interval = null; }
	};

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

	const release_final_scores = () => {
		socket.emit('release_final_scores', {});
	};

	const set_score_visibility = (policy: 'hidden' | 'self_only' | 'top_n' | 'full') => {
		socket.emit('set_score_visibility', { policy });
	};

	const update_review_score = (question_index: number, username: string, score: string) => {
		const parsed = parseFloat(score);
		if (isNaN(parsed)) {
			return;
		}
		socket.emit('update_review_score', { question_index, username, score: parsed });
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

	const emit_push_inject = (payload: InjectPreviewPayload) => {
		if (payload.inject_id) {
			socket.emit('push_inject', { inject_id: payload.inject_id });
		} else {
			socket.emit('push_inject', {
				title: payload.title,
				content: payload.content,
				severity: payload.severity
			});
		}
		refresh_situation_data();
	};

	const queue_inject_preview = (payload: InjectPreviewPayload) => {
		inject_preview_payload = payload;
		inject_preview_open = true;
	};

	const push_predefined_inject = (inject: Inject) => {
		queue_inject_preview({
			title: inject.title,
			content: inject.content,
			severity: inject.severity,
			inject_id: inject.id
		});
	};

	const push_quick_preset = (preset: (typeof QUICK_INJECT_PRESETS)[number]) => {
		queue_inject_preview({
			title: preset.title,
			content: preset.content,
			severity: preset.severity
		});
	};

	const push_adhoc_inject = () => {
		if (!adhoc_inject_title.trim()) return;
		queue_inject_preview({
			title: adhoc_inject_title,
			content: adhoc_inject_content,
			severity: adhoc_inject_severity
		});
	};

	const confirm_inject_preview = () => {
		if (!inject_preview_payload) return;
		emit_push_inject(inject_preview_payload);
		if (!inject_preview_payload.inject_id) {
			adhoc_inject_title = '';
			adhoc_inject_content = '';
			adhoc_inject_severity = 'info';
		}
		inject_preview_payload = null;
	};

	const update_situation = () => {
		socket.emit('update_situation', { ...situation_status });
		refresh_situation_data();
	};

	const onSituationRoomData = (data: {
		status?: SituationStatus | null;
		injects_log?: InjectLogEntry[];
		situation_log?: SituationLogEntry[];
	}) => {
		if (data?.status && Object.keys(data.status).length > 0) {
			situation_status = data.status;
		}
		if (data?.injects_log) injects_log = normalizeInjectsLog(data.injects_log);
		if (data?.situation_log) situation_log = data.situation_log;
	};

	const onInjectReceived = (inject: Inject) => {
		injects_log = [
			...injects_log,
			{ inject, triggered_by: 'facilitator', timestamp: new Date().toISOString() }
		];
	};

	const onSituationUpdated = (status: SituationStatus) => {
		if (status) {
			situation_log = [
				...situation_log,
				{ ...status, timestamp: new Date().toISOString() }
			];
		}
	};

	const handle_facilitator_hotkey = (e: KeyboardEvent) => {
		if (!is_tabletop) return;
		const target = e.target as HTMLElement | null;
		if (target?.matches('input, textarea, select, [contenteditable="true"]')) return;

		const key = e.key.toLowerCase();
		if (key === 'escape') {
			facilitator_dock_open = false;
			inject_preview_open = false;
			return;
		}
		if (key === 'i') {
			e.preventDefault();
			open_facilitator_tab('injects');
		} else if (key === 's') {
			e.preventDefault();
			open_facilitator_tab('situation');
		} else if (key === 'h') {
			e.preventDefault();
			open_facilitator_tab('hands');
		} else if (key === 't') {
			e.preventDefault();
			open_facilitator_tab('timeline');
		}
	};

	const onScoreReviewSheet = (sheet: unknown) => {
		score_review_sheet = sheet;
		score_review_open = true;
	};

	onMount(() => {
		socket.on('situation_room_data', onSituationRoomData);
		socket.on('inject_received', onInjectReceived);
		socket.on('rehearsal_state', onRehearsalState);
		socket.on('situation_updated', onSituationUpdated);
		socket.on('discussion_timer_started', onDiscussionTimerStarted);
		socket.on('discussion_timer_paused', onDiscussionTimerPaused);
		socket.on('discussion_timer_stopped', onDiscussionTimerStopped);
		socket.on('question_timer_started', onQuestionTimerStarted);
		socket.on('question_timer_paused', onQuestionTimerPaused);
		socket.on('question_timer_stopped', onQuestionTimerStopped);
		socket.on('score_review_sheet', onScoreReviewSheet);
		refresh_situation_data();
		window.addEventListener('keydown', handle_facilitator_hotkey);
	});

	onDestroy(() => {
		socket.off('situation_room_data', onSituationRoomData);
		socket.off('inject_received', onInjectReceived);
		socket.off('rehearsal_state', onRehearsalState);
		socket.off('situation_updated', onSituationUpdated);
		socket.off('discussion_timer_started', onDiscussionTimerStarted);
		socket.off('discussion_timer_paused', onDiscussionTimerPaused);
		socket.off('discussion_timer_stopped', onDiscussionTimerStopped);
		socket.off('question_timer_started', onQuestionTimerStarted);
		socket.off('question_timer_paused', onQuestionTimerPaused);
		socket.off('question_timer_stopped', onQuestionTimerStopped);
		socket.off('score_review_sheet', onScoreReviewSheet);
		if (disc_interval) { clearInterval(disc_interval); disc_interval = null; }
		if (qtimer_interval) { clearInterval(qtimer_interval); qtimer_interval = null; }
		window.removeEventListener('keydown', handle_facilitator_hotkey);
	});

	const to_plain_text = (html?: string) => {
		if (!html) return 'Untitled';
		return html.replace(/<[^>]*>/g, '').trim() || 'Untitled';
	};

	const find_question_by_id = (question_id?: string) => {
		if (!question_id) return null;
		const idx = quiz_data.questions.findIndex((q) => q.id === question_id);
		if (idx < 0) return null;
		return { index: idx, question: quiz_data.questions[idx] };
	};

	const branch_previews = $derived.by(() => {
		if (!is_tabletop || selected_question < 0 || !quiz_data.questions?.length) {
			return [];
		}
		const current = quiz_data.questions[selected_question];
		const previews: Array<{ source: string; target_index: number; target_label: string; fallback?: boolean }> = [];

		if (Array.isArray(current.answers)) {
			for (const answer of current.answers) {
				if (!answer || !('next_question_id' in answer) || !answer.next_question_id) continue;
				const target = find_question_by_id(answer.next_question_id);
				if (!target) continue;
				previews.push({
					source: answer.answer ?? 'Branch',
					target_index: target.index,
					target_label: to_plain_text(target.question.question)
				});
			}
		}

		if (current.default_next_question_id) {
			const target = find_question_by_id(current.default_next_question_id);
			if (target) {
				previews.push({
					source: 'Default',
					target_index: target.index,
					target_label: to_plain_text(target.question.question),
					fallback: true
				});
			}
		}

		if (previews.length === 0 && selected_question + 1 < quiz_data.questions.length) {
			const next = quiz_data.questions[selected_question + 1];
			previews.push({
				source: 'Sequential',
				target_index: selected_question + 1,
				target_label: to_plain_text(next.question),
				fallback: true
			});
		}

		return previews;
	});

</script>

<header class="host-toolbar fixed top-0 z-30 w-full">
	<div class="flex flex-wrap items-center gap-2 px-3 py-2">
		<span class="host-badge">
			Q {selected_question === -1 ? '0' : selected_question + 1} / {quiz_data.questions.length}
		</span>
		<button onclick={on_toggle_socket_diagnostics} class="host-btn">
			Diagnostics: {socket_diagnostics_enabled ? 'On' : 'Off'}
		</button>
		<div class="ml-auto flex flex-wrap items-center justify-end gap-2">
		{#if selected_question + 1 === quiz_data.questions.length && ((timer_res === '0' && question_results !== null) || quiz_data?.questions?.[selected_question]?.type === QuizQuestionType.SLIDE)}
			{#if JSON.stringify(final_results) === JSON.stringify([null])}
				<button onclick={get_final_results} class="host-btn"
					>Prepare Score Sheet
				</button>
			{/if}
		{:else if timer_res === '0' || selected_question === -1}
			{#if (selected_question + 1 !== quiz_data.questions.length && question_results !== null) || selected_question === -1}
				<button
					onclick={() => {
						set_question_number(selected_question + 1);
					}}
					class="host-btn"
					>{$t('admin_page.next_question', { question: selected_question + 2 })}
				</button>
			{/if}
			{#if question_results === null && selected_question !== -1}
				{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
					<button
						onclick={() => {
							set_question_number(selected_question + 1);
						}}
						class="host-btn"
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
						class="host-btn"
						>{$t('admin_page.next_question', { question: selected_question + 2 })}
					</button>
				{:else}
					<button onclick={get_question_results} class="host-btn"
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
					class="host-btn"
					>{$t('admin_page.next_question', { question: selected_question + 2 })}
				</button>
			{:else}
				<button onclick={show_solutions} class="host-btn"
					>{$t('admin_page.stop_time_and_solutions')}
				</button>
			{/if}
		{/if}
		</div>
	</div>
	{#if is_tabletop && selected_question >= 0}
	<div class="flex flex-wrap items-center gap-2 overflow-x-auto border-t border-slate-700/50 px-3 py-2">
		<button onclick={advance_tabletop} class="host-btn">Advance (Branch)</button>
		<select class="host-field w-auto py-1" bind:value={override_question_id}>
			<option value="">Override → ...</option>
			{#each quiz_data.questions as q, qi}
				{#if qi !== selected_question}
					<option value={q.id ?? ''}>{qi + 1}. {q.question?.replace(/<[^>]*>/g, '').slice(0, 30) || 'Q' + (qi + 1)}</option>
				{/if}
			{/each}
		</select>
		{#if override_question_id}
			<button onclick={force_next_question} class="host-btn-warn">Override</button>
		{/if}
		{#if tie_pending}
			<span class="ml-2 text-xs font-semibold text-red-600">TIE — pick a winner:</span>
			{#each Object.entries(tie_votes) as [answer, count]}
				<button onclick={() => resolve_tie(answer)} class="host-btn-danger" title="{count} votes">{answer}</button>
			{/each}
		{/if}
		<div class="ml-auto flex gap-2">
			<!-- Question Answer Timer (shown when timer.enabled for current question) -->
			{#if is_tabletop && selected_question >= 0 && quiz_data?.questions?.[selected_question]?.timer?.enabled}
				<div class="flex items-center gap-1 border-r border-white/30 pr-2 mr-1">
					{#if qtimer_total > 0 && (qtimer_running || qtimer_remaining > 0)}
						<span class="font-mono text-xs font-bold tabular-nums"
							class:text-green-300={qtimer_running && qtimer_remaining > 30}
							class:text-yellow-300={qtimer_running && qtimer_remaining <= 30}
							class:text-red-400={qtimer_running && qtimer_remaining <= 10}
							class:text-gray-300={!qtimer_running}
						>{qtimer_fmt(qtimer_remaining)}</span>
						{#if qtimer_running}
							<button onclick={qtimer_pause} class="host-btn-warn" title="Pause answer timer">⏸</button>
						{:else}
							<button onclick={qtimer_resume} class="host-btn-accent" title="Resume answer timer">▶</button>
						{/if}
						<button onclick={qtimer_stop} class="host-btn-danger" title="Stop answer timer">■</button>
					{:else}
						<span class="text-xs text-white/60">Answer:</span>
						<input
							type="number"
							min="5"
							max="7200"
							step="10"
							placeholder={String(qtimer_effective_duration)}
							class="w-16 rounded border border-white/30 bg-white/10 px-1 py-0.5 text-xs text-white placeholder:text-white/40 outline-hidden"
							onchange={(e) => { qtimer_custom_seconds = parseInt(e.currentTarget.value) || null; }}
							title="Override answer timer duration in seconds"
						/>
						<span class="text-xs text-white/60">s</span>
						<button onclick={qtimer_start} class="host-btn-accent" title="Start answer timer">▶ Start</button>
					{/if}
				</div>
			{/if}
			<!-- Discussion Timer -->
			<div class="flex items-center gap-1 border-r border-white/30 pr-2 mr-1">
				{#if disc_total > 0 && (disc_running || disc_remaining > 0)}
					<span class="font-mono text-xs font-bold tabular-nums"
						class:text-green-300={disc_running && disc_remaining > 60}
						class:text-yellow-300={disc_running && disc_remaining <= 60}
						class:text-red-400={disc_running && disc_remaining <= 15}
						class:text-gray-300={!disc_running}
					>{disc_fmt(disc_remaining)}</span>
					{#if disc_running}
						<button onclick={disc_pause} class="host-btn-warn" title="Pause timer">⏸</button>
					{:else}
						<button onclick={disc_resume} class="host-btn-accent" title="Resume timer">▶</button>
					{/if}
					<button onclick={disc_stop} class="host-btn-danger" title="Stop timer">■</button>
				{:else}
					<span class="text-xs text-white/60">Discussion:</span>
					<input
						type="number"
						min="10"
						max="7200"
						step="30"
						placeholder={String(disc_effective_duration)}
						class="w-16 rounded border border-white/30 bg-white/10 px-1 py-0.5 text-xs text-white placeholder:text-white/40 outline-hidden"
						onchange={(e) => { disc_custom_seconds = parseInt(e.currentTarget.value) || null; }}
						title="Override duration in seconds (blank = use question default)"
					/>
					<span class="text-xs text-white/60">s</span>
					<button onclick={disc_start} class="host-btn-accent" title="Start discussion timer">▶ Start</button>
				{/if}
			</div>
			<button
				type="button"
				class="host-btn"
				onclick={() => open_facilitator_tab('situation')}
				title="Open situation room"
			>
				<span
					class="mr-1 inline-block h-2 w-2 rounded-full"
					class:bg-emerald-400={situation_status.severity === 'low'}
					class:bg-amber-400={situation_status.severity === 'medium'}
					class:bg-orange-500={situation_status.severity === 'high'}
					class:bg-red-500={situation_status.severity === 'critical'}
				></span>
				{situation_status.phase}
			</button>
			{#if raised_hands.length > 0}
				<button type="button" class="host-btn-warn relative" onclick={() => open_facilitator_tab('hands')}>
					✋ {raised_hands.length}
				</button>
			{/if}
			<button
				type="button"
				class="host-btn-accent"
				onclick={() => {
					facilitator_dock_open = !facilitator_dock_open;
					if (facilitator_dock_open) refresh_situation_data();
				}}
				title="Shortcuts: S situation, I injects, H hands, T timeline, Esc close"
			>
				Facilitator Console
			</button>
		</div>
	</div>
	{/if}
</header>
	{#if quiz_data?.questions?.[selected_question]?.type === QuizQuestionType.SCOREBOARD && scoreboard_data}
		<div class="fixed inset-0 z-35 flex items-center justify-center bg-black/50 backdrop-blur-sm">
			<div class="w-full max-w-lg rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 p-8 text-white shadow-[0_30px_80px_rgba(15,23,42,0.6)] backdrop-blur-2xl">
				<p class="text-center text-xs uppercase tracking-[0.35em] text-slate-400/80">Live Scoreboard</p>
				<h2 class="mt-1 text-center text-2xl font-bold">Current Rankings</h2>
				<div class="mt-6 space-y-2">
					{#each scoreboard_data.ranked.slice(0, 10) as [player, score], i}
						<div class="flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5">
							<span class="w-6 text-center text-sm font-bold {i === 0 ? 'text-yellow-400' : i === 1 ? 'text-slate-300' : i === 2 ? 'text-amber-600' : 'text-slate-500'}">{i + 1}</span>
							<span class="flex-1 text-sm text-slate-200">{player}</span>
							<span class="text-sm font-semibold text-[#B07156]">{score}</span>
						</div>
					{/each}
				</div>
			</div>
		</div>
	{/if}
	{#if score_review_open && score_review_sheet}
		<div class="fixed inset-0 z-40 bg-black/70 p-4 overflow-auto">
			<div class="mx-auto w-full max-w-6xl rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 p-6 text-white shadow-[0_30px_80px_rgba(15,23,42,0.6)] backdrop-blur-2xl">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80">Score Validation</p>
						<h3 class="text-2xl font-semibold">Review Before Releasing Final Scores</h3>
					</div>
					<button class="rounded-full border border-white/15 px-4 py-2 text-xs font-semibold hover:bg-white/6" onclick={() => (score_review_open = false)}>Close</button>
				</div>
				<div class="mt-4 grid gap-3 sm:grid-cols-3">
					<div class="rounded-xl border border-white/10 bg-white/5 px-4 py-3">
						<p class="text-xs uppercase tracking-[0.25em] text-slate-400/70">Company Score</p>
						<p class="text-2xl font-semibold">{score_review_sheet.company_score}</p>
					</div>
					<div class="rounded-xl border border-white/10 bg-white/5 px-4 py-3">
						<p class="text-xs uppercase tracking-[0.25em] text-slate-400/70">Benchmark</p>
						<p class="text-2xl font-semibold">{score_review_sheet.company_benchmark}</p>
					</div>
					<div class="rounded-xl border border-white/10 bg-white/5 px-4 py-3">
						<p class="text-xs uppercase tracking-[0.25em] text-slate-400/70">Players</p>
						<p class="text-2xl font-semibold">{Object.keys(score_review_sheet.player_totals ?? {}).length}</p>
					</div>
				</div>

				<div class="mt-5 space-y-4">
					{#each score_review_sheet.rows ?? [] as row}
						<div class="rounded-2xl border border-white/10 bg-white/4 p-4">
							<div class="mb-3 flex items-center justify-between">
								<p class="text-sm font-semibold text-white">Q{row.question_index + 1}: {row.question_title || 'Untitled'}</p>
								<span class="rounded-full border border-white/15 px-3 py-1 text-xs text-slate-300">{row.question_type}</span>
							</div>
							<div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
								{#each Object.entries(row.scores ?? {}) as [uname, rawScore]}
									{@const quality = row.decision_quality?.[uname]}
									<div class="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-3 py-2">
										<span class="text-sm text-slate-300">{uname}</span>
										<input
											type="number"
											min="0"
											step="1"
											value={rawScore}
											class="w-20 rounded-lg border border-white/10 bg-[#0f172a]/80 px-2 py-1 text-right text-sm text-white outline-none focus:border-[#B07156]/60"
											onchange={(e) => update_review_score(row.question_index, uname, e.currentTarget.value)}
										/>
									</div>
									{#if quality}<div class="col-span-full -mt-1 rounded-xl border border-teal-500/20 bg-teal-500/5 px-3 py-2 text-[11px] text-slate-400"><span class="font-semibold text-teal-300">Decision quality:</span> {quality.rubric_score != null ? `${quality.rubric_score}% rubric` : 'No rubric'} · {quality.confidence_score}% confidence · {quality.time_score}% timing{#if quality.criteria?.length}<span class="ml-2">· {quality.criteria.filter((criterion: { matched: boolean }) => criterion.matched).length}/{quality.criteria.length} criteria matched</span>{/if}</div>{/if}
								{/each}
							</div>
						</div>
					{/each}
				</div>

				<div class="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-white/8 pt-4">
					<div class="text-sm text-slate-400">Players are on hold while these scores are validated.</div>
					<div class="flex flex-wrap items-center gap-2">
						<span class="text-xs text-slate-400">Score visibility:</span>
						{#each (['hidden', 'self_only', 'top_n', 'full'] as const) as policy}
							<button onclick={() => set_score_visibility(policy)} class="rounded-full border border-white/15 px-3 py-1 text-xs text-slate-300 hover:bg-white/10 transition-colors capitalize">
								{policy.replace('_', ' ')}
							</button>
						{/each}
					</div>
					<button onclick={release_final_scores} class="host-btn-accent px-6 py-2.5 text-sm">
						Release Final Scores
					</button>
				</div>
			</div>
		</div>
	{/if}
	{#if is_tabletop}
		<FacilitatorDock
			bind:open={facilitator_dock_open}
			bind:activeTab={facilitator_dock_tab}
			handsCount={raised_hands.length}
			timelineCount={timeline_events.length}
			severity={situation_status.severity}
			phase={situation_status.phase}
			showRoles={is_tabletop}
			onopenprojector={open_projector_display}
		>
			{#snippet rehearsal()}
				<div class="space-y-4"><div class="rounded-xl border border-violet-500/30 bg-violet-500/10 p-3"><p class="text-sm font-bold text-violet-200">Safe rehearsal mode</p><p class="mt-1 text-xs leading-5 text-violet-100/70">This simulation is private to you. It does not broadcast, score players, or change the live exercise.</p></div>
					{#if !rehearsal_active}<button type="button" class="host-btn-accent w-full" onclick={start_rehearsal}>Start private rehearsal</button>{:else}<div class="space-y-3"><div class="flex items-center justify-between"><span class="host-label mb-0">Simulated node</span><span class="text-xs font-bold text-violet-300">{rehearsal_question + 1} / {quiz_data.questions.length}</span></div><select bind:value={rehearsal_question} class="host-field w-full">{#each quiz_data.questions as rehearsal_q, index}<option value={index}>Q{index + 1} · {rehearsal_q.question?.replace(/<[^>]*>/g, '').slice(0, 55) || 'Untitled'}</option>{/each}</select><div class="rounded-xl border border-slate-700 bg-slate-900/60 p-3"><p class="text-xs font-bold uppercase tracking-wider text-slate-500">Player-view content</p><p class="mt-2 text-sm font-semibold text-slate-100">{quiz_data.questions[rehearsal_question]?.question?.replace(/<[^>]*>/g, '') || 'No question content'}</p><p class="mt-2 text-xs text-slate-400">Type: {quiz_data.questions[rehearsal_question]?.type ?? 'ABCD'} · Objective: {quiz_data.questions[rehearsal_question]?.objective ?? 'Not set'}</p></div><div class="flex gap-2"><button type="button" class="host-btn flex-1" onclick={rehearsal_previous} disabled={rehearsal_question <= 0}>Previous</button><button type="button" class="host-btn flex-1" onclick={rehearsal_next} disabled={rehearsal_question >= quiz_data.questions.length - 1}>Next</button></div><label class="block"><span class="host-label">Clock speed</span><select bind:value={rehearsal_clock_speed} class="host-field mt-1 w-full"><option value={0.5}>0.5× slower</option><option value={1}>1× normal</option><option value={2}>2× faster</option><option value={4}>4× faster</option></select></label><div class="flex gap-2"><button type="button" class="host-btn-warn flex-1" onclick={reset_rehearsal}>Reset rehearsal</button><button type="button" class="host-btn flex-1" onclick={exit_rehearsal}>Exit mode</button></div></div>{/if}
					</div>
					{#if rehearsal_active}<div class="mt-3 border-t border-slate-700 pt-3"><button type="button" class="host-btn-accent w-full" onclick={save_rehearsal_snapshot}>Save server snapshot</button>{#if rehearsal_snapshots.length}<div class="mt-2 space-y-1"><p class="host-label">Saved snapshots</p>{#each rehearsal_snapshots as snapshot, index}<button type="button" class="flex w-full items-center justify-between rounded-lg border border-slate-700 px-3 py-2 text-left text-xs text-slate-300 hover:bg-slate-800" onclick={() => restore_rehearsal_snapshot(index)}><span>Snapshot {index + 1} · Q{snapshot.question + 1}</span><span class="text-violet-300">Restore</span></button>{/each}</div>{/if}</div>{/if}
				{/snippet}
			{#snippet situation()}
				{#if facilitator_notes}
					<div class="mb-4 rounded-xl border border-cyan-500/30 bg-cyan-500/10 p-3">
						<h4 class="mb-1 text-xs font-bold uppercase tracking-[0.2em] text-cyan-300">Facilitator Notes</h4>
						<p class="text-sm whitespace-pre-wrap text-slate-200">{facilitator_notes}</p>
					</div>
				{/if}
				<div class="flex flex-col gap-3">
					<div>
						<span class="host-label">Severity</span>
						<select bind:value={situation_status.severity} class="host-field mt-1">
							<option value="low">Low</option>
							<option value="medium">Medium</option>
							<option value="high">High</option>
							<option value="critical">Critical</option>
						</select>
					</div>
					<div>
						<span class="host-label">Incident Phase</span>
						<select bind:value={situation_status.phase} class="host-field mt-1">
							<option value="Detection">Detection</option>
							<option value="Containment">Containment</option>
							<option value="Eradication">Eradication</option>
							<option value="Recovery">Recovery</option>
							<option value="Lessons Learned">Lessons Learned</option>
						</select>
					</div>
					<div>
						<span class="host-label">Affected Systems</span>
						<div class="mt-1 flex flex-wrap gap-1">
							{#each situation_status.affected_systems as sys, i}
								<span class="inline-flex items-center gap-1 rounded-full border border-purple-500/40 bg-purple-500/20 px-2 py-0.5 text-[10px] text-purple-200">
									{sys}
									<button type="button" class="hover:text-red-300" onclick={() => {
										situation_status.affected_systems = situation_status.affected_systems.filter((_, idx) => idx !== i);
									}}>&times;</button>
								</span>
							{/each}
						</div>
						<div class="mt-1 flex gap-1">
							<input
								type="text"
								bind:value={new_affected_system}
								placeholder="Add system"
								class="host-field flex-1"
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
								class="host-btn"
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
						<span class="host-label">Summary</span>
						<textarea
							bind:value={situation_status.summary}
							placeholder="Current situation summary..."
							class="host-field mt-1 min-h-[40px] resize-y"
						></textarea>
					</div>
					<div>
						<span class="host-label">Context / Background</span>
						<textarea
							bind:value={(situation_status as any).context_notes}
							placeholder="Scenario background, asset details, threat actor info..."
							class="host-field mt-1 min-h-[48px] resize-y"
						></textarea>
					</div>
					<button class="host-btn-accent mt-1 w-full" onclick={update_situation}>Broadcast Update</button>
				</div>
			{/snippet}

			{#snippet references()}
				<div class="mb-4"><p class="text-sm font-bold text-teal-300">Player reference shelf</p><p class="mt-1 text-xs leading-5 text-slate-400">Open a policy for everyone and send a clear notification to player screens.</p></div>
				{#if quiz_data.reference_documents?.length}
					<div class="space-y-2">{#each quiz_data.reference_documents as document}<div class="flex items-center justify-between gap-3 rounded-xl border border-slate-700 bg-slate-900/60 p-3"><div class="min-w-0"><p class="truncate text-sm font-semibold text-slate-100">{document.title}</p><p class="mt-1 truncate text-[10px] uppercase tracking-wider text-slate-500">{document.filename ?? document.category ?? 'Company reference'}</p></div><button type="button" class="host-btn-accent shrink-0 px-3 py-1.5 text-xs" onclick={() => spotlight_policy(document)}>Open for players</button></div>{/each}</div>
				{:else}<p class="rounded-xl border border-dashed border-slate-700 p-4 text-xs text-slate-500">No policies are attached to this scenario. Add them from Scenario management before starting.</p>{/if}
			{/snippet}

			{#snippet injects()}
				<div class="mb-4">
					<span class="host-label">Quick presets</span>
					<div class="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
						{#each QUICK_INJECT_PRESETS as preset}
							<button
								type="button"
								class="rounded-xl border p-3 text-left transition-colors hover:bg-slate-800/80 {preset.severity === 'critical' ? 'border-red-500/50 bg-red-500/10' : preset.severity === 'warning' ? 'border-amber-500/50 bg-amber-500/10' : 'border-cyan-500/40 bg-cyan-500/10'}"
								onclick={() => push_quick_preset(preset)}
							>
								<p class="text-sm font-semibold text-slate-100">{preset.title}</p>
								<p class="mt-0.5 text-[10px] uppercase tracking-wide text-slate-400">{preset.hint}</p>
							</button>
						{/each}
					</div>
				</div>
				{#if quiz_data.injects?.length}
					<div class="mb-4 border-t border-slate-700/60 pt-3">
						<span class="host-label">Quiz injects</span>
						{#each quiz_data.injects as inject}
							<button
								class="mt-1.5 w-full rounded-lg border p-2.5 text-left text-xs transition-colors hover:bg-slate-800/80 {inject.severity === 'info' ? 'border-cyan-500/40' : inject.severity === 'warning' ? 'border-amber-500/40' : 'border-red-500/40'}"
								onclick={() => push_predefined_inject(inject)}
							>
								<span class="font-semibold text-slate-100">{inject.title}</span>
								<span
									class="ml-1 rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase {inject.severity === 'info' ? 'bg-cyan-500/20 text-cyan-300' : inject.severity === 'warning' ? 'bg-amber-500/20 text-amber-300' : 'bg-red-500/20 text-red-300'}"
								>{inject.severity}</span>
							</button>
						{/each}
					</div>
				{/if}
				<div class="border-t border-slate-700/60 pt-3">
					<span class="host-label">Ad-hoc inject</span>
					<input type="text" bind:value={adhoc_inject_title} placeholder="Title" class="host-field mt-2" />
					<textarea
						bind:value={adhoc_inject_content}
						placeholder="Content (markdown)"
						class="host-field mt-2 min-h-[40px] resize-y"
					></textarea>
					<div class="mt-2 flex items-center gap-2">
						<select bind:value={adhoc_inject_severity} class="host-field w-auto">
							<option value="info">Info</option>
							<option value="warning">Warning</option>
							<option value="critical">Critical</option>
						</select>
						<button class="host-btn-warn ml-auto" disabled={!adhoc_inject_title.trim()} onclick={push_adhoc_inject}>
							Preview & push
						</button>
					</div>
				</div>
			{/snippet}

			{#snippet hands()}
				<div class="mb-3 flex items-center justify-between">
					<h3 class="text-sm font-bold text-amber-300">✋ Raised Hands ({raised_hands.length})</h3>
					{#if raised_hands.length > 0}
						<button class="text-xs text-amber-400 hover:text-amber-200" onclick={() => socket.emit('dismiss_all_hands', {})}>
							Dismiss All
						</button>
					{/if}
				</div>
				{#if raised_hands.length === 0}
					<p class="text-xs italic text-slate-500">No hands raised.</p>
				{:else}
					<div class="flex flex-col gap-2">
						{#each raised_hands as username}
							<div class="flex items-center justify-between rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2">
								<span class="text-sm font-medium text-amber-100">✋ {username}</span>
								<button class="host-btn-warn px-2 py-0.5" onclick={() => socket.emit('dismiss_hand', { username })}>
									Dismiss
								</button>
							</div>
						{/each}
					</div>
				{/if}
			{/snippet}

			{#snippet roles()}
				<RolesPanel
					embedded
					roles={quiz_data.roles ?? []}
					role_descriptions={quiz_data.role_descriptions ?? {}}
					{player_roles}
				/>
			{/snippet}

			{#snippet rewards()}
				<div class="space-y-4">
					<div>
						<p class="text-sm font-bold text-amber-300">Participation bonus</p>
						<p class="mt-1 text-xs leading-5 text-slate-400">Recognise a strong decision, helpful contribution, or excellent teamwork. The recipient sees the award immediately.</p>
					</div>
					<div>
						<label class="host-label" for="bonus-target">Player</label>
						<select id="bonus-target" bind:value={bonus_target} class="host-field mt-1 w-full">
							<option value="">Choose a player</option>
							{#each players as player}<option value={player.username}>{player.username}</option>{/each}
						</select>
					</div>
					<div class="grid grid-cols-[1fr,2fr] gap-2">
						<div><label class="host-label" for="bonus-amount">Points</label><input id="bonus-amount" type="number" min="1" max="10000" bind:value={bonus_amount} class="host-field mt-1 w-full" /></div>
						<div><label class="host-label" for="bonus-reason">Reason</label><input id="bonus-reason" bind:value={bonus_reason} maxlength="200" class="host-field mt-1 w-full" /></div>
					</div>
					<button type="button" class="host-btn-accent w-full" disabled={!bonus_target || bonus_amount < 1} onclick={award_bonus}>Award +{bonus_amount || 0} points</button>
				</div>
			{/snippet}

			{#snippet timeline()}
				<div class="mb-3 flex items-center justify-between">
					<p class="host-label mb-0">Session timeline</p>
					<button type="button" class="host-btn" onclick={refresh_situation_data}>Refresh</button>
				</div>
				<FacilitatorTimeline events={timeline_events} />
			{/snippet}
		</FacilitatorDock>
		<RehearsalPlayerSimulator active={rehearsal_active} {quiz_data} question={rehearsal_question} answers={rehearsal_answers} {socket} />

		<InjectPreviewModal
			bind:open={inject_preview_open}
			payload={inject_preview_payload}
			onconfirm={confirm_inject_preview}
		/>
	{/if}

<EmojiPanel
	{socket}
	players={Object.keys(player_roles).map(username => ({ username }))}
/>

{#if is_tabletop && selected_question >= 0}
	<div class="fixed bottom-0 left-0 right-0 z-20 border-t border-slate-700/80 bg-slate-950/95 px-3 py-2 shadow-[0_-8px_24px_rgba(0,0,0,0.35)] backdrop-blur-xl">
		<div class="flex items-center gap-3">
			<span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Next Branch Preview</span>
			<div class="flex-1 overflow-x-auto">
				<div class="flex gap-2 min-w-max">
					{#if branch_previews.length === 0}
						<div class="rounded-md border border-dashed border-slate-600 px-3 py-1.5 text-xs text-slate-500">No branch targets configured</div>
					{/if}
					{#each branch_previews as preview}
						<div class="rounded-xl border border-slate-600/60 bg-slate-800/80 px-3 py-1.5 text-xs">
							<p class="font-semibold text-slate-100">{preview.source}{preview.fallback ? ' (fallback)' : ''}</p>
							<p class="text-slate-400">→ Q{preview.target_index + 1}: {preview.target_label.slice(0, 72)}</p>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</div>
{/if}

