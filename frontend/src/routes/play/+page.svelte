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
		players?: string[];
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
			game_pin: data.game_pin
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
		Cookies.set('joined_game', JSON.stringify({ sid: socket.id, username, game_pin }), {
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
		solution = undefined;
		restart();
		question = data.question;
		question_index = data.question_index;
		answer_results = undefined;
	};

	const onStartGame = () => {
		gameMeta.started = true;
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

	const onFinalResults = (data: Array<Array<PlayerAnswer>>) => {
		final_results = data;
		Cookies.remove('joined_game');
	};

	const onSolutions = (data: QuestionType) => {
		solution = data;
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
		{#if !gameMeta.started && gameData === undefined}
			<JoinGame bind:game_pin bind:game_mode bind:username />
		{:else if JSON.stringify(final_results) !== JSON.stringify([null])}
			<ShowEndScreen bind:data={scores} show_final_results={true} {username} />
		{:else if gameData !== undefined && question_index === ''}
			<ShowTitle
				title={gameData.title}
				description={gameData.description}
				cover_image={gameData.cover_image}
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
