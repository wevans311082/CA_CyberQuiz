<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<!--suppress ALL -->
<script lang="ts">
	import { socket } from '$lib/socket';
	import JoinGame from '$lib/play/join.svelte';
	import type { Answer, Question as QuestionType, Inject, SituationStatus, TimelineEvent } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import ShowTitle from '$lib/play/title.svelte';
	import Question from '$lib/play/question.svelte';
	import Slide from '$lib/play/admin/slide.svelte';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import ShowEndScreen from '$lib/play/admin/final_results.svelte';
	import KahootResults from '$lib/play/results_kahoot.svelte';
	import SocketDiagnostics from '$lib/socket_diagnostics.svelte';
	import { FRONTEND_BUILD_NUMBER } from '$lib/build_info';
	import SituationRoom from '$lib/play/SituationRoom.svelte';
	import AnswerSummary from '$lib/play/AnswerSummary.svelte';
	import CountdownOverlay from '$lib/play/countdown_overlay.svelte';
	import { getLocalization } from '$lib/i18n';
	import { onDestroy, onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import Cookies from 'js-cookie';
	const { t } = getLocalization();

	interface Props {
		// Exports
		data: any;
	}

	let { data }: Props = $props();
	let { game_pin } = $state(data);

	// Types
	interface GameMeta {
		started: boolean;
	}

	interface PlayerGameData {
		title: string;
		description: string;
		cover_image?: string;
		background_color?: string;
		started?: boolean;
		players?: Array<{username: string; avatar_params?: any}>;
		player_count?: number;
		question_count?: number;
		current_question?: number;
		question_show?: boolean;
		game_id?: string;
		scenario_type?: string;
		roles?: string[];
		role_descriptions?: Record<string, string>;
		master_theme?: import('$lib/quiz_types').MasterTheme;
	}

	let game_mode = $state();
	let final_results: Array<null> | Array<Array<PlayerAnswer>> = $state([null]);

	interface PlayerAnswer {
		username: string;
		answer: string;
		right: string;
	}

	// Variables init
	let question_index = $state('');
	let unique = $state({});
	navbarVisible.visible = false;
	let answer_results: Array<Answer> = $state();
	let gameData: PlayerGameData | undefined = $state();
	let solution: QuestionType = $state();
	let username = $state('');
	let scores = $state({});
	let gameMeta: GameMeta = $state({
		started: false
	});

	let question: Question = $state();
	let chat_messages = $state<Array<{ sender: string; content: string; timestamp: string; sender_is_admin?: boolean }>>([]);
	let chat_block_reason = $state<string | null>(null);
	let final_results_avatar_map = $state<Record<string, any>>({});
	let countdown_active = $state(false);
	let countdown_remaining_seconds = $state(0);
	let countdown_total_seconds = $state(5);
	let countdown_timer: ReturnType<typeof setInterval> | null = null;
	let countdown_event_received = $state(false);
	let socket_diagnostics_enabled = $state(false);
	let score_validation_pending = $state(false);
	let provisional_my_score = $state<number | null>(null);
	let provisional_company_score = $state<number | null>(null);
	let provisional_company_benchmark = $state<number | null>(null);

	// Tabletop exercise state
	let scenario_type = $state<string | undefined>(undefined);
	let my_role = $state<string | undefined>(undefined);
	let player_roles = $state<Record<string, string>>({});
	let current_allowed_roles = $state<string[] | undefined>(undefined);
	let current_decision_mode = $state<string | undefined>(undefined);
	let branch_path = $state<string[]>([]);
	let hand_raised = $state(false);

	// Inject & situation state
	let active_injects = $state<Inject[]>([]);
	let situation_status = $state<SituationStatus | null>(null);
	let discussion_time = $state<number | null>(null);
	let disc_running = $state(false);
	let disc_remaining = $state(0);
	let disc_total = $state(0);
	let disc_interval: ReturnType<typeof setInterval> | null = null;

	// Question answer timer (server-synced)
	let qtimer_running = $state(false);
	let qtimer_remaining = $state(0);
	let qtimer_total = $state(0);
	let qtimer_interval: ReturnType<typeof setInterval> | null = null;

	const qtimer_fmt = (s: number) => {
		const m = Math.floor(s / 60);
		const sec = Math.floor(s % 60);
		return m > 0 ? `${m}:${sec.toString().padStart(2, '0')}` : `${Math.floor(s)}s`;
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

	const onQuestionTimerStarted = (data: { duration: number; server_timestamp: string }) => {
		qtimer_running = true;
		qtimer_total = data.duration;
		const serverStart = new Date(data.server_timestamp).getTime();
		if (qtimer_interval) clearInterval(qtimer_interval);
		qtimer_interval = setInterval(() => {
			const elapsed = (Date.now() - serverStart) / 1000;
			const rem = Math.max(0, data.duration - elapsed);
			qtimer_remaining = rem;
			if (rem <= 0) {
				qtimer_running = false;
				if (qtimer_interval) { clearInterval(qtimer_interval); qtimer_interval = null; }
			}
		}, 250);
	};

	const onQuestionTimerPaused = (data: { remaining: number }) => {
		qtimer_running = false;
		qtimer_remaining = data.remaining;
		if (qtimer_interval) { clearInterval(qtimer_interval); qtimer_interval = null; }
	};

	const onQuestionTimerStopped = () => {
		qtimer_running = false;
		qtimer_remaining = 0;
		qtimer_total = 0;
		if (qtimer_interval) { clearInterval(qtimer_interval); qtimer_interval = null; }
	};
	let injects_log = $state<Array<{ inject: Inject; triggered_by: string; timestamp: string }>>([]);
	let situation_room_open = $state(false);
	let answer_summary = $state<{ total: number; answers: Record<string, number> } | null>(null);
	let event_log = $state<TimelineEvent[]>([]);

	let _evt_counter = 0;
	const add_event = (ev: Omit<TimelineEvent, 'id' | 'timestamp'>) => {
		event_log = [...event_log, { ...ev, id: String(++_evt_counter), timestamp: new Date().toISOString() }];
	};

	let preventReload = true;

	// Functions
	function restart() {
		unique = {};
	}

	const confirmUnload = (event: Event) => {
		if (preventReload) {
			event.preventDefault();
			// eslint-disable-next-line @typescript-eslint/ban-ts-comment
			// @ts-ignore
			event.returnValue = '';
		}
	};

	const onTimeSync = (data: string) => {
		socket.emit('echo_time_sync', data);
	};

	const onConnect = async () => {
		console.log('Connected!');
		const cookie_data = Cookies.get('joined_game');
		if (!cookie_data) {
			return;
		}
		const data = JSON.parse(cookie_data);
		socket.emit('rejoin_game', {
			old_sid: data.sid,
			username: data.username,
			game_pin: data.game_pin,
			avatar_params: data.avatar_params
		});
		try {
			const res = await fetch(`/api/v1/quiz/play/check_captcha/${game_pin}`);
			const json = await res.json();
			game_mode = json.game_mode;
		} catch (error) {
			console.error('Failed to refresh game mode on reconnect', error);
		}
	};

	const onJoinedGame = (data: PlayerGameData) => {
		console.log('[JOINED_GAME] Handler fired with data:', data);
		gameData = data;
		console.log('[JOINED_GAME] gameData set to:', gameData);
		gameMeta.started = gameData.started === true;
		console.log('[JOINED_GAME] gameMeta.started set to:', gameMeta.started);
		// Capture tabletop scenario type
		if (gameData.scenario_type) {
			scenario_type = gameData.scenario_type;
		}
		if (typeof window !== 'undefined' && 'plausible' in window && typeof window.plausible === 'function') {
			window.plausible('Joined Game', { props: { game_id: gameData.game_id } });
		}
		const avatar_params = (() => {
			const cookie_data = Cookies.get('joined_game');
			if (!cookie_data) {
				return undefined;
			}
			try {
				return JSON.parse(cookie_data).avatar_params;
			} catch {
				return undefined;
			}
		})();
		Cookies.set('joined_game', JSON.stringify({ sid: socket.id, username, game_pin, avatar_params }), {
			expires: 3600
		});
	};

	const onRejoinedGame = (data: PlayerGameData) => {
		gameData = data;
		if (data.started) {
			gameMeta.started = true;
		}
		if (data.scenario_type) {
			scenario_type = data.scenario_type;
		}
	};

	const onGameNotFound = () => {
		const cookie_data = Cookies.get('joined_game');
		if (cookie_data) {
			Cookies.remove('joined_game');
			window.location.reload();
			return;
		}
	};

	const onSetQuestionNumber = (data: { question: QuestionType; question_index: string }) => {
		countdown_active = false;
		countdown_event_received = false;
		if (countdown_timer) {
			clearInterval(countdown_timer);
			countdown_timer = null;
		}
		// Reset discussion timer when a new question loads
		disc_running = false;
		disc_remaining = 0;
		disc_total = 0;
		if (disc_interval) { clearInterval(disc_interval); disc_interval = null; }
		solution = undefined;
		restart();
		question = data.question;
		question_index = data.question_index;
		answer_results = undefined;
		answer_summary = null;
		// Capture tabletop metadata from question payload
		current_allowed_roles = data.question?.allowed_roles ?? undefined;
		current_decision_mode = data.question?.decision_mode ?? undefined;
		const q_text = data.question?.question?.replace(/<[^>]*>/g, '').trim() ?? `Question ${data.question_index}`;
		add_event({ type: 'question_asked', title: `Q${Number(data.question_index) + 1}: ${q_text.slice(0, 60)}${q_text.length > 60 ? '…' : ''}` });
	};

	const onStartGame = () => {
		gameMeta.started = true;
		add_event({ type: 'game_started', title: 'Game started' });
		setTimeout(() => {
			if (!countdown_event_received && !countdown_active && question_index === '') {
				startCountdownFromServer({ server_timestamp: new Date().toISOString(), duration_seconds: 5 });
			}
		}, 350);
	};

	const startCountdownFromServer = (data: { server_timestamp: string; duration_seconds: number; remaining_seconds?: number }) => {
		countdown_event_received = true;
		if (countdown_timer) {
			clearInterval(countdown_timer);
			countdown_timer = null;
		}
		const duration = Number(data.duration_seconds || 5);
		const serverStart = new Date(data.server_timestamp).getTime();
		const elapsed = Math.max(0, (Date.now() - serverStart) / 1000);
		countdown_total_seconds = duration;
		countdown_remaining_seconds = Math.max(0, data.remaining_seconds ?? duration - elapsed);
		countdown_active = countdown_remaining_seconds > 0;

		countdown_timer = setInterval(() => {
			const elapsedNow = Math.max(0, (Date.now() - serverStart) / 1000);
			countdown_remaining_seconds = Math.max(0, duration - elapsedNow);
			if (countdown_remaining_seconds <= 0) {
				countdown_active = false;
				countdown_event_received = false;
				if (countdown_timer) {
					clearInterval(countdown_timer);
					countdown_timer = null;
				}
			}
		}, 100);
	};

	const onGameAlreadyStarted = () => {
		window.alert('This quiz has already started. Reloading to rejoin the live session.');
		window.location.reload();
	};

	const onQuestionResults = (data: Array<Answer>) => {
		restart();
		answer_results = data;
		if (data) {
			const correct = Array.isArray(data) ? data.filter((a: any) => a?.is_right).length : 0;
			add_event({ type: 'answer_results', title: 'Results revealed', detail: `${correct} player${correct !== 1 ? 's' : ''} answered correctly` });
		}
	};

	const onUsernameAlreadyExists = () => {
		window.alert('Username already exists!');
	};

	const onKick = () => {
		window.alert('You got kicked');
		preventReload = false;
		game_pin = '';
		username = '';
		Cookies.set('kicked', 'value', { expires: 1 });
		window.location.reload();
	};

	const onFinalResults = (data: any) => {
		if (data && typeof data === 'object' && 'results' in data) {
			final_results = data.results;
			final_results_avatar_map = data.avatar_map ?? {};
			if (data.player_scores) {
				scores = data.player_scores;
			}
		} else {
			final_results = data;
			final_results_avatar_map = {};
		}
		score_validation_pending = false;
		Cookies.remove('joined_game');
	};

	const onScoreValidationStarted = (data: { company_score?: number; company_benchmark?: number }) => {
		score_validation_pending = true;
		provisional_company_score = data?.company_score ?? null;
		provisional_company_benchmark = data?.company_benchmark ?? null;
	};

	const onProvisionalScoreUpdate = (data: { username?: string; score?: number }) => {
		if (!data || data.username !== username) {
			return;
		}
		provisional_my_score = data.score ?? null;
	};

	const onProvisionalCompanyScore = (data: { company_score?: number; company_benchmark?: number }) => {
		provisional_company_score = data?.company_score ?? null;
		provisional_company_benchmark = data?.company_benchmark ?? null;
	};

	const onScoreValidationCompleted = (_data: { company_score?: number; company_benchmark?: number }) => {
		score_validation_pending = false;
	};

	const onSolutions = (data: QuestionType) => {
		solution = data;
	};

	const onCountdownStart = (data: { server_timestamp: string; duration_seconds: number; remaining_seconds?: number }) => {
		startCountdownFromServer(data);
	};

	const onChatHistory = (data: { messages: Array<{ sender: string; content: string; timestamp: string; sender_is_admin?: boolean }> }) => {
		chat_messages = Array.isArray(data?.messages) ? data.messages : [];
	};

	const onChatMessageReceived = (data: { sender: string; content: string; timestamp: string; sender_is_admin?: boolean }) => {
		chat_messages = [...chat_messages, data].slice(-40);
		chat_block_reason = null;
	};

	const onChatBlocked = (data: { reason?: string }) => {
		chat_block_reason = data?.reason ?? 'blocked';
	};

	const onSocketDiagnosticsVisibility = (data: { enabled?: boolean }) => {
		socket_diagnostics_enabled = Boolean(data?.enabled);
	};

	const onLobbyState = (data: { players?: Array<{ username: string; avatar_params?: any }>; player_count?: number }) => {
		if (!data?.players) {
			return;
		}
		if (gameData) {
			gameData = { ...gameData, players: data.players, player_count: data.player_count ?? data.players.length };
		}
	};

	// Tabletop socket event handlers
	const onRolesUpdated = (data: { player_roles?: Record<string, string>; roles?: string[] }) => {
		if (data?.player_roles) {
			player_roles = data.player_roles;
			if (username && data.player_roles[username]) {
				const new_role = data.player_roles[username];
				if (new_role !== my_role) {
					my_role = new_role;
					add_event({ type: 'role_assigned', title: `Role assigned: ${new_role}`, detail: `You are now the ${new_role}` });
				}
			}
		}
	};

	const onRoleNotAllowed = () => {
		// Answer rejected server-side — no action needed, button should already be disabled
	};

	// Role proposal (admin proposes, player accepts/declines)
	let pending_role_proposal = $state<{ role: string } | null>(null);

	const onRoleProposed = (data: { username: string; role: string }) => {
		// Only show the modal if this proposal is for me
		if (data?.username === username) {
			pending_role_proposal = { role: data.role };
		}
	};

	const accept_role = () => {
		if (pending_role_proposal) {
			socket.emit('respond_to_role', { role: pending_role_proposal.role, accepted: true });
			pending_role_proposal = null;
		}
	};
	const decline_role = () => {
		if (pending_role_proposal) {
			socket.emit('respond_to_role', { role: pending_role_proposal.role, accepted: false });
			pending_role_proposal = null;
		}
	};

	const onBranchResolved = (data: { question_id?: string; branch_path?: string[] }) => {
		if (data?.branch_path) {
			branch_path = data.branch_path;
		}
		add_event({ type: 'branch_resolved', title: 'Decision made', detail: 'Team voted and a path was chosen' });
	};

	const onScenarioComplete = () => {
		add_event({ type: 'scenario_complete', title: 'Scenario complete', detail: 'The tabletop exercise has concluded' });
	};

	const onTieDetected = (_data: { votes?: Record<string, number> }) => {
		// Tie detected — players wait for facilitator to resolve
	};

	const onInjectReceived = (data: Inject) => {
		if (data) {
			active_injects = [...active_injects, data];
			// Also record in inject history for situation room
			injects_log = [...injects_log, { inject: data, triggered_by: 'facilitator', timestamp: new Date().toISOString() }];
			add_event({ type: 'inject', title: data.title ?? 'Inject received', detail: data.content?.slice(0, 80), data: { severity: data.severity } as Record<string, unknown> });
		}
	};

	const onSituationUpdated = (data: SituationStatus) => {
		if (data) {
			situation_status = data;
			add_event({ type: 'situation_update', title: `Situation update: ${data.severity ?? ''} / ${data.phase ?? ''}`, detail: data.summary?.slice(0, 80) });
		}
	};

	const onSituationRoomData = (data: { status: SituationStatus; injects_log: Array<{ inject: Inject; triggered_by: string; timestamp: string }> }) => {
		if (data?.status) {
			situation_status = data.status;
		}
		if (data?.injects_log) {
			injects_log = data.injects_log;
		}
	};

	const onAnswerSummary = (data: { total: number; answers: Record<string, number> }) => {
		if (data) {
			answer_summary = data;
		}
	};

	const dismissInject = (id: string) => {
		active_injects = active_injects.filter(inj => inj.id !== id);
		socket.emit('dismiss_inject', { inject_id: id });
	};

	onMount(() => {
		socket.on('time_sync', onTimeSync);
		socket.on('connect', onConnect);
		socket.on('joined_game', onJoinedGame);
		socket.on('rejoined_game', onRejoinedGame);
		socket.on('game_not_found', onGameNotFound);
		socket.on('set_question_number', onSetQuestionNumber);
		socket.on('start_game', onStartGame);
		socket.on('game_already_started', onGameAlreadyStarted);
		socket.on('question_results', onQuestionResults);
		socket.on('username_already_exists', onUsernameAlreadyExists);
		socket.on('kick', onKick);
		socket.on('final_results', onFinalResults);
		socket.on('score_validation_started', onScoreValidationStarted);
		socket.on('provisional_score_update', onProvisionalScoreUpdate);
		socket.on('provisional_company_score', onProvisionalCompanyScore);
		socket.on('score_validation_completed', onScoreValidationCompleted);
		socket.on('solutions', onSolutions);
		socket.on('countdown_start', onCountdownStart);
		socket.on('chat_history', onChatHistory);
		socket.on('chat_message_received', onChatMessageReceived);
		socket.on('chat_blocked', onChatBlocked);
		socket.on('socket_diagnostics_visibility', onSocketDiagnosticsVisibility);
		socket.on('lobby_state', onLobbyState);
		socket.on('roles_updated', onRolesUpdated);
		socket.on('role_not_allowed', onRoleNotAllowed);
		socket.on('role_proposed', onRoleProposed);
		socket.on('branch_resolved', onBranchResolved);
		socket.on('scenario_complete', onScenarioComplete);
		socket.on('tie_detected', onTieDetected);
		socket.on('inject_received', onInjectReceived);
		socket.on('situation_updated', onSituationUpdated);
		socket.on('situation_room_data', onSituationRoomData);
		socket.on('answer_summary', onAnswerSummary);
		socket.on('discussion_timer_started', onDiscussionTimerStarted);
		socket.on('discussion_timer_paused', onDiscussionTimerPaused);
		socket.on('discussion_timer_stopped', onDiscussionTimerStopped);
		socket.on('question_timer_started', onQuestionTimerStarted);
		socket.on('question_timer_paused', onQuestionTimerPaused);
		socket.on('question_timer_stopped', onQuestionTimerStopped);
	});

	onDestroy(() => {
		socket.off('time_sync', onTimeSync);
		socket.off('connect', onConnect);
		socket.off('joined_game', onJoinedGame);
		socket.off('rejoined_game', onRejoinedGame);
		socket.off('game_not_found', onGameNotFound);
		socket.off('set_question_number', onSetQuestionNumber);
		socket.off('start_game', onStartGame);
		socket.off('game_already_started', onGameAlreadyStarted);
		socket.off('question_results', onQuestionResults);
		socket.off('username_already_exists', onUsernameAlreadyExists);
		socket.off('kick', onKick);
		socket.off('final_results', onFinalResults);
		socket.off('score_validation_started', onScoreValidationStarted);
		socket.off('provisional_score_update', onProvisionalScoreUpdate);
		socket.off('provisional_company_score', onProvisionalCompanyScore);
		socket.off('score_validation_completed', onScoreValidationCompleted);
		socket.off('solutions', onSolutions);
		socket.off('countdown_start', onCountdownStart);
		socket.off('chat_history', onChatHistory);
		socket.off('chat_message_received', onChatMessageReceived);
		socket.off('chat_blocked', onChatBlocked);
		socket.off('socket_diagnostics_visibility', onSocketDiagnosticsVisibility);
		socket.off('lobby_state', onLobbyState);
		socket.off('roles_updated', onRolesUpdated);
		socket.off('role_not_allowed', onRoleNotAllowed);
		socket.off('role_proposed', onRoleProposed);
		socket.off('branch_resolved', onBranchResolved);
		socket.off('scenario_complete', onScenarioComplete);
		socket.off('tie_detected', onTieDetected);
		socket.off('inject_received', onInjectReceived);
		socket.off('situation_updated', onSituationUpdated);
		socket.off('situation_room_data', onSituationRoomData);
		socket.off('answer_summary', onAnswerSummary);
		socket.off('discussion_timer_started', onDiscussionTimerStarted);
		socket.off('discussion_timer_paused', onDiscussionTimerPaused);
		socket.off('discussion_timer_stopped', onDiscussionTimerStopped);
		socket.off('question_timer_started', onQuestionTimerStarted);
		socket.off('question_timer_paused', onQuestionTimerPaused);
		socket.off('question_timer_stopped', onQuestionTimerStopped);
		if (disc_interval) { clearInterval(disc_interval); disc_interval = null; }
		if (qtimer_interval) { clearInterval(qtimer_interval); qtimer_interval = null; }
		if (countdown_timer) {
			clearInterval(countdown_timer);
			countdown_timer = null;
		}
	});

	let bg_color = $derived(gameData ? gameData.background_color : undefined);

	// The rest
</script>

<svelte:window onbeforeunload={confirmUnload} />
<svelte:head>
	<title>CyberAsk Quiz - Join</title>
</svelte:head>
<div
	class="min-h-screen min-w-full"
	style="background: {bg_color ? bg_color : 'transparent'}"
	class:text-black={bg_color}
>
	{#if socket_diagnostics_enabled}
	<div class="fixed right-4 top-4 z-50 rounded-md border border-black/20 bg-white/90 px-3 py-1 text-xs font-semibold text-black shadow-sm">
		build #{FRONTEND_BUILD_NUMBER}
	</div>
	{/if}
	<!-- Always-available diagnostics toggle -->
	<button
		class="fixed left-4 top-4 z-50 rounded-full p-1.5 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition opacity-30 hover:opacity-100"
		onclick={() => { socket_diagnostics_enabled = !socket_diagnostics_enabled; }}
		title="Toggle diagnostics"
	>
		<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
			<path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
		</svg>
	</button>
	<div>
		<CountdownOverlay
			active={countdown_active}
			remaining_seconds={countdown_remaining_seconds}
			total_seconds={countdown_total_seconds}
			label="Quiz starts in"
		/>
		{#if !gameMeta.started && gameData === undefined}
			<JoinGame bind:game_pin bind:game_mode bind:username />
		{:else if JSON.stringify(final_results) !== JSON.stringify([null])}
			<ShowEndScreen
				bind:data={scores}
				show_final_results={true}
				{username}
				raw_final_results={final_results}
				avatar_map={
					Object.keys(final_results_avatar_map).length > 0
						? final_results_avatar_map
						: Object.fromEntries((gameData?.players ?? []).map((player) => [player.username, player.avatar_params]))
				}
			/>
		{:else if score_validation_pending}
			<div class="flex min-h-[55vh] items-center justify-center px-4">
				<div class="w-full max-w-xl rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 p-7 text-center text-white shadow-[0_30px_80px_rgba(15,23,42,0.6)] backdrop-blur-2xl">
					<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80">Score Validation</p>
					<h2 class="mt-2 text-2xl font-semibold">Scores Are Being Validated By Admin</h2>
					<p class="mt-2 text-sm text-slate-400">Please wait while the facilitator reviews each question/slide score before release.</p>
					<div class="mt-5 grid gap-3 sm:grid-cols-2">
						<div class="rounded-xl border border-white/10 bg-white/5 p-4">
							<p class="text-xs uppercase tracking-[0.25em] text-slate-400/70">Your Current Score</p>
							<p class="mt-1 text-2xl font-semibold">{provisional_my_score ?? 'Pending'}</p>
						</div>
						<div class="rounded-xl border border-white/10 bg-white/5 p-4">
							<p class="text-xs uppercase tracking-[0.25em] text-slate-400/70">Company Score</p>
							<p class="mt-1 text-2xl font-semibold">{provisional_company_score ?? 'Pending'}</p>
							{#if provisional_company_benchmark !== null}
								<p class="text-xs text-slate-400 mt-1">Benchmark: {provisional_company_benchmark}</p>
							{/if}
						</div>
					</div>
				</div>
			</div>
		{:else if gameData !== undefined && question_index === ''}
			<ShowTitle
				title={gameData.title}
				description={gameData.description}
				cover_image={gameData.cover_image}
				players={gameData.players}
				player_count={gameData.player_count}
				started={gameMeta.started}
				socket={socket}
				{chat_messages}
				chat_block_reason={chat_block_reason}
				{my_role}
				{player_roles}
				{scenario_type}
				role_descriptions={gameData.role_descriptions ?? {}}
				roles={gameData.roles ?? []}
				bind:hand_raised
			/>
		{:else if gameMeta.started && gameData !== undefined && question_index !== '' && answer_results === undefined}
			{#key unique}
				<div class="text-black dark:text-black">
					{#if question?.type === QuizQuestionType.SLIDE}
						<Slide {question} master_theme={gameData?.master_theme} />
					{:else}
						<Question bind:game_mode bind:question {question_index} {solution} {my_role} {scenario_type} allowed_roles={current_allowed_roles} master_theme={gameData?.master_theme} />
					{/if}
				</div>
			{/key}
		{:else}
			{#if answer_results === null}
				<div class="w-full flex justify-center">
					<h1 class="text-3xl">{$t('admin_page.no_answers')}</h1>
				</div>
			{:else}
				<div>
					<h2 class="text-center text-3xl mb-8">{$t('words.result', { count: 2 })}</h2>
				</div>
				{#key unique}
					<KahootResults {username} question_results={answer_results} bind:scores />
				{/key}
				{#if answer_summary}
					<AnswerSummary total={answer_summary.total} answers={answer_summary.answers} />
				{/if}
			{/if}
		{/if}
	</div>
	<!-- Question timer overlay (server-synced) -->
	{#if qtimer_running}
		<div class="fixed top-3 right-3 z-50 flex items-center gap-1.5 rounded-lg bg-black/80 px-3 py-1.5 text-white shadow-xl">
			<svg class="h-4 w-4 text-red-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/></svg>
			<span class="font-mono text-sm font-bold">{qtimer_fmt(qtimer_remaining)}</span>
		</div>
	{/if}
	<SocketDiagnostics
		socket={socket}
		label="player"
		enabled={socket_diagnostics_enabled}
		details={{
			gamePin: game_pin,
			username,
			started: gameMeta.started,
			questionIndex: question_index,
			hasGameData: gameData !== undefined,
			buildNumber: FRONTEND_BUILD_NUMBER,
			hasQuestion: question !== undefined,
				playerCount: gameData?.players?.length ?? 0
		}}
	/>
	<!-- Situation Room Pop-out -->
	{#if scenario_type === 'tabletop' && gameData !== undefined}
		<SituationRoom
			bind:open={situation_room_open}
			{situation_status}
			{injects_log}
			{event_log}
			{socket}
		/>
	{/if}
	<!-- Situation Status Bar -->
	{#if scenario_type === 'tabletop' && situation_status}
		<div class="fixed bottom-0 left-0 w-full z-40 flex items-center gap-4 px-4 py-2 text-xs text-white"
			class:bg-green-700={situation_status.severity === 'low'}
			class:bg-yellow-600={situation_status.severity === 'medium'}
			class:bg-orange-600={situation_status.severity === 'high'}
			class:bg-red-700={situation_status.severity === 'critical'}
		>
			<span class="font-bold uppercase">Severity: {situation_status.severity}</span>
			<span>|</span>
			<span>Phase: {situation_status.phase}</span>
			{#if situation_status.affected_systems?.length}
				<span>|</span>
				<span>Systems: {situation_status.affected_systems.join(', ')}</span>
			{/if}
			{#if situation_status.summary}
				<span>|</span>
				<span class="truncate max-w-xs">{situation_status.summary}</span>
			{/if}
		</div>
	{/if}
	<!-- Discussion Timer (visible to all players when running) -->
	{#if scenario_type === 'tabletop' && disc_total > 0}
		<div class="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 rounded-full px-5 py-2 shadow-xl"
			class:bg-green-700={disc_running && disc_remaining > 60}
			class:bg-yellow-600={disc_running && disc_remaining <= 60 && disc_remaining > 15}
			class:bg-red-700={disc_running && disc_remaining <= 15}
			class:bg-gray-600={!disc_running}
		>
			<span class="text-white text-xs font-semibold uppercase tracking-wide">Discussion</span>
			<span class="text-white font-mono text-xl font-bold tabular-nums">{disc_fmt(disc_remaining)}</span>
			{#if !disc_running}
				<span class="text-white/70 text-xs">Paused</span>
			{/if}
		</div>
	{/if}
	<!-- Inject Notifications -->
	{#if active_injects.length > 0}
		<div class="fixed top-16 right-4 z-50 flex flex-col gap-2 max-w-sm">
			{#each active_injects as inject (inject.id)}
				<div class="rounded-lg border-2 p-3 shadow-xl animate-pulse-once"
					class:border-blue-400={inject.severity === 'info'}
					class:bg-blue-50={inject.severity === 'info'}
					class:border-yellow-400={inject.severity === 'warning'}
					class:bg-yellow-50={inject.severity === 'warning'}
					class:border-red-400={inject.severity === 'critical'}
					class:bg-red-50={inject.severity === 'critical'}
				>
					<div class="flex items-center justify-between mb-1">
						<span class="text-xs font-bold uppercase"
							class:text-blue-700={inject.severity === 'info'}
							class:text-yellow-700={inject.severity === 'warning'}
							class:text-red-700={inject.severity === 'critical'}
						>INJECT — {inject.severity}</span>
						<button
							class="text-gray-500 hover:text-gray-800 text-lg leading-none"
							onclick={() => dismissInject(inject.id)}
						>&times;</button>
					</div>
					<h4 class="font-semibold text-sm text-gray-900">{inject.title}</h4>
					{#if inject.content}
						<p class="text-xs text-gray-700 mt-1 whitespace-pre-wrap">{inject.content}</p>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Role proposal modal -->
{#if pending_role_proposal}
	<div class="fixed inset-0 z-[70] flex items-center justify-center bg-black/50" transition:fade={{ duration: 150 }}>
		<div class="rounded-2xl bg-white dark:bg-gray-800 shadow-2xl p-6 max-w-sm w-full mx-4">
			<div class="flex items-center gap-3 mb-4">
				<span class="text-3xl">👤</span>
				<div>
					<h2 class="text-lg font-bold text-gray-900 dark:text-white">Role Assignment</h2>
					<p class="text-sm text-gray-500 dark:text-gray-400">The facilitator has proposed a role for you</p>
				</div>
			</div>
			<div class="rounded-xl bg-teal-50 dark:bg-teal-900/40 border border-teal-300 dark:border-teal-700 px-4 py-3 mb-5 text-center">
				<span class="text-xl font-bold text-teal-700 dark:text-teal-300">{pending_role_proposal.role}</span>
			</div>
			<div class="flex gap-3">
				<button
					class="flex-1 rounded-xl bg-teal-600 px-4 py-2.5 font-semibold text-white hover:bg-teal-700 transition"
					onclick={accept_role}
				>Accept</button>
				<button
					class="flex-1 rounded-xl bg-gray-200 dark:bg-gray-700 px-4 py-2.5 font-semibold text-gray-700 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600 transition"
					onclick={decline_role}
				>Decline</button>
			</div>
		</div>
	</div>
{/if}
