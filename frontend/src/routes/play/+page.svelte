<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<!--suppress ALL -->
<script lang="ts">
	import { socket } from '$lib/socket';
	import JoinGame from '$lib/play/join.svelte';
	import type { Answer, Question as QuestionType, Inject, SituationStatus } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import ShowTitle from '$lib/play/title.svelte';
	import Question from '$lib/play/question.svelte';
	import Slide from '$lib/play/admin/slide.svelte';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import ShowEndScreen from '$lib/play/admin/final_results.svelte';
	import KahootResults from '$lib/play/results_kahoot.svelte';
	import SocketDiagnostics from '$lib/socket_diagnostics.svelte';
	import { FRONTEND_BUILD_NUMBER } from '$lib/build_info';
	import CountdownOverlay from '$lib/play/countdown_overlay.svelte';
	import { getLocalization } from '$lib/i18n';
	import { onDestroy, onMount } from 'svelte';
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

	// Tabletop exercise state
	let scenario_type = $state<string | undefined>(undefined);
	let my_role = $state<string | undefined>(undefined);
	let player_roles = $state<Record<string, string>>({});
	let current_allowed_roles = $state<string[] | undefined>(undefined);
	let current_decision_mode = $state<string | undefined>(undefined);
	let branch_path = $state<string[]>([]);

	// Inject & situation state
	let active_injects = $state<Inject[]>([]);
	let situation_status = $state<SituationStatus | null>(null);
	let discussion_time = $state<number | null>(null);

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
		solution = undefined;
		restart();
		question = data.question;
		question_index = data.question_index;
		answer_results = undefined;
		// Capture tabletop metadata from question payload
		current_allowed_roles = data.question?.allowed_roles ?? undefined;
		current_decision_mode = data.question?.decision_mode ?? undefined;
	};

	const onStartGame = () => {
		gameMeta.started = true;
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
		} else {
			final_results = data;
			final_results_avatar_map = {};
		}
		Cookies.remove('joined_game');
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
				my_role = data.player_roles[username];
			}
		}
	};

	const onRoleNotAllowed = () => {
		// Answer rejected server-side — no action needed, button should already be disabled
	};

	const onBranchResolved = (data: { question_id?: string; branch_path?: string[] }) => {
		if (data?.branch_path) {
			branch_path = data.branch_path;
		}
	};

	const onScenarioComplete = () => {
		// Scenario finished, final results will follow
	};

	const onTieDetected = (_data: { votes?: Record<string, number> }) => {
		// Tie detected — players wait for facilitator to resolve
	};

	const onInjectReceived = (data: Inject) => {
		if (data) {
			active_injects = [...active_injects, data];
		}
	};

	const onSituationUpdated = (data: SituationStatus) => {
		if (data) {
			situation_status = data;
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
		socket.on('solutions', onSolutions);
		socket.on('countdown_start', onCountdownStart);
		socket.on('chat_history', onChatHistory);
		socket.on('chat_message_received', onChatMessageReceived);
		socket.on('chat_blocked', onChatBlocked);
		socket.on('socket_diagnostics_visibility', onSocketDiagnosticsVisibility);
		socket.on('lobby_state', onLobbyState);
		socket.on('roles_updated', onRolesUpdated);
		socket.on('role_not_allowed', onRoleNotAllowed);
		socket.on('branch_resolved', onBranchResolved);
		socket.on('scenario_complete', onScenarioComplete);
		socket.on('tie_detected', onTieDetected);
		socket.on('inject_received', onInjectReceived);
		socket.on('situation_updated', onSituationUpdated);
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
		socket.off('solutions', onSolutions);
		socket.off('countdown_start', onCountdownStart);
		socket.off('chat_history', onChatHistory);
		socket.off('chat_message_received', onChatMessageReceived);
		socket.off('chat_blocked', onChatBlocked);
		socket.off('socket_diagnostics_visibility', onSocketDiagnosticsVisibility);
		socket.off('lobby_state', onLobbyState);
		socket.off('roles_updated', onRolesUpdated);
		socket.off('role_not_allowed', onRoleNotAllowed);
		socket.off('branch_resolved', onBranchResolved);
		socket.off('scenario_complete', onScenarioComplete);
		socket.off('tie_detected', onTieDetected);
		socket.off('inject_received', onInjectReceived);
		socket.off('situation_updated', onSituationUpdated);
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
	<div class="fixed right-4 top-4 z-50 rounded-md border border-black/20 bg-white/90 px-3 py-1 text-xs font-semibold text-black shadow-sm">
		build #{FRONTEND_BUILD_NUMBER}
	</div>
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
			/>
		{:else if gameMeta.started && gameData !== undefined && question_index !== '' && answer_results === undefined}
			{#key unique}
				<div class="text-black dark:text-black">
					{#if question?.type === QuizQuestionType.SLIDE}
						<Slide {question} />
					{:else}
						<Question bind:game_mode bind:question {question_index} {solution} {my_role} {scenario_type} allowed_roles={current_allowed_roles} />
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
			{/if}
		{/if}
	</div>
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
