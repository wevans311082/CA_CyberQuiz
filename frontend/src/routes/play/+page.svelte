<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<!--suppress ALL -->
<script lang="ts">
	import { socket } from '$lib/socket';
	import JoinGame from '$lib/play/join.svelte';
	import type { Answer, Question as QuestionType } from '$lib/quiz_types';
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
			/>
		{:else if gameMeta.started && gameData !== undefined && question_index !== '' && answer_results === undefined}
			{#key unique}
				<div class="text-black dark:text-black">
					{#if question?.type === QuizQuestionType.SLIDE}
						<Slide {question} />
					{:else}
						<Question bind:game_mode bind:question {question_index} {solution} />
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
</div>
