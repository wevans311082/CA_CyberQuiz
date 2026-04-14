<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';

	import { socket } from '$lib/socket';
	import { getLocalization } from '$lib/i18n';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import type { PlayerAnswer, Player } from '$lib/admin.ts';
	import SomeAdminScreen from '$lib/admin.svelte';
	import GameNotStarted from '$lib/play/admin/game_not_started.svelte';
	import { browser } from '$app/environment';
	import { onMount } from 'svelte';
	import FinalResults from '$lib/play/admin/final_results.svelte';
	import GrayButton from '$lib/components/buttons/gray.svelte';
	import SocketDiagnostics from '$lib/socket_diagnostics.svelte';
	import { FRONTEND_BUILD_NUMBER } from '$lib/build_info';
	import { page } from '$app/state';
	import CountdownOverlay from '$lib/play/countdown_overlay.svelte';

	navbarVisible.visible = false;

	const { t } = getLocalization();

	// let gameData = {
	// 	game_id: 'a7ddb6af-79ab-45e0-b996-6254c1ad9818',
	// 	game_pin: '66190765'

	interface Props {
		// };
		data: any;
	}

	let { data }: Props = $props();
	let game_mode = $state();
	let { auto_connect, game_token } = $state(data);
	const game_pin = data.game_pin;

	let players: Array<Player> = $state([]);
	let player_scores = $state({});
	let errorMessage = $state('');
	let game_started = $state(false);
	let quiz_data: QuizData = $state();
	let control_visible = $state(true);
	//let question_number = '0';
	// let question_results = null;
	let final_results: Array<null> | Array<Array<PlayerAnswer>> = $state([null]);
	let final_results_avatar_map = $state<Record<string, any>>({});
	let success = $state(false);
	let dataexport_download_a = $state();
	let warnToLeave = true;
	let export_token = $state(undefined);
	let chat_messages = $state<Array<{ sender: string; content: string; timestamp: string; sender_is_admin?: boolean }>>([]);
	let chat_block_reason = $state<string | null>(null);
	let countdown_active = $state(false);
	let countdown_remaining_seconds = $state(0);
	let countdown_total_seconds = $state(5);
	let countdown_timer: ReturnType<typeof setInterval> | null = null;
	let countdown_event_received = $state(false);
	let socket_diagnostics_enabled = $state(false);

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

	const connect = async () => {
		socket.emit('register_as_admin', {
			game_pin: game_pin,
			game_id: game_token
		});
		const res = await fetch(`/api/v1/quiz/play/check_captcha/${game_pin}`);
		const json = await res.json();
		game_mode = json.game_mode;
	};
	onMount(() => {
		if (auto_connect) {
			connect();
		}
	});
	socket.on('session_id', (d) => {
		const session_id = d.session_id;
	});

	socket.on('registered_as_admin', (data) => {
		quiz_data = JSON.parse(data['game']);
		console.log(quiz_data);
		success = true;
	});
	socket.on('player_joined', (int_data) => {
		players = [...players.filter((player) => player.username !== int_data.username), int_data];
	});
	socket.on('lobby_state', (data) => {
		if (!data || !Array.isArray(data.players)) {
			return;
		}
		players = data.players;
	});
	socket.on('chat_history', (data) => {
		chat_messages = Array.isArray(data?.messages) ? data.messages : [];
	});
	socket.on('chat_message_received', (data) => {
		chat_messages = [...chat_messages, data].slice(-40);
		chat_block_reason = null;
	});
	socket.on('chat_blocked', (data) => {
		chat_block_reason = data?.reason ?? 'blocked';
	});
	socket.on('socket_diagnostics_visibility', (data) => {
		socket_diagnostics_enabled = Boolean(data?.enabled);
	});
	socket.on('already_registered_as_admin', () => {
		// eslint-disable-next-line @typescript-eslint/ban-ts-comment
		// @ts-ignore
		errorMessage = $t('admin_page.already_registered_as_admin');
	});

	socket.on('start_game', (_) => {
		game_started = true;
		setTimeout(() => {
			if (!countdown_event_received && !countdown_active) {
				startCountdownFromServer({ server_timestamp: new Date().toISOString(), duration_seconds: 5 });
			}
		}, 350);
	});

	socket.on('countdown_start', (data) => {
		startCountdownFromServer(data);
	});

	const toggleSocketDiagnostics = () => {
		socket.emit('set_socket_diagnostics_visibility', {
			enabled: !socket_diagnostics_enabled
		});
	};

	socket.on('control_visibility', (data) => {
		control_visible = data.visible;
	});

	/*	socket.on('question_results', (int_data) => {
        try {
            int_data = JSON.parse(int_data);
        } catch (e) {
            console.error('Failed to parse question results');
            return;
        }
        question_results = int_data;
    });*/
	socket.on('export_token', (int_data) => {
		warnToLeave = false;
		export_token = int_data;

		setTimeout(() => {
			warnToLeave = true;
		}, 200);
	});

	socket.on('results_saved_successfully', (_) => {
		results_saved = true;
	});

	const confirmUnload = () => {
		if (warnToLeave) {
			event.preventDefault();
			// eslint-disable-next-line @typescript-eslint/ban-ts-comment
			// @ts-ignore
			event.returnValue = '';
		}
	};

	const request_answer_export = (e: Event) => {
		e.preventDefault();
		socket.emit('get_export_token');
	};
	const save_quiz = () => {
		socket.emit('save_quiz');
	};

	let darkMode = false;
	if (browser) {
		darkMode =
			localStorage.theme === 'dark' ||
			(!('theme' in localStorage) &&
				window.matchMedia('(prefers-color-scheme: dark)').matches);
	}

	let bg_color = $derived(quiz_data ? quiz_data.background_color : undefined);
	let bg_image = $derived(quiz_data ? quiz_data.background_image : undefined);
	let results_saved = $state(false);

	let show_final_results = $derived(JSON.stringify(final_results) !== JSON.stringify([null]));
</script>

<svelte:window onbeforeunload={confirmUnload} />
<svelte:head>
	<title>ClassQuiz - Host</title>
</svelte:head>
<div
	class="min-h-screen min-w-full"
	style="background-repeat: no-repeat;background-size: 100% 100%;background-image: {bg_image
		? `url('${bg_image}')`
		: `unset`}; background-color: {bg_color ? bg_color : 'transparent'}"
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
	{#if JSON.stringify(final_results) !== JSON.stringify([null])}
		{#if control_visible}
			<div class="w-screen flex justify-center mt-16">
				<div class="w-fit">
					{#if export_token === undefined}
						<GrayButton onclick={request_answer_export}
							>{$t('admin_page.request_export_results')}</GrayButton
						>
					{:else}
						<GrayButton
							target="_blank"
							href="/api/v1/quiz/export_data/{export_token}?ts={new Date().getTime()}&game_pin={game_pin}"
							>{$t('admin_page.download_export_results')}</GrayButton
						>
					{/if}
				</div>
			</div>
			<div class="w-screen flex justify-center mt-2">
				<div class="w-fit">
					<GrayButton onclick={save_quiz} flex={true} disabled={results_saved}>
						{#if results_saved}
							<svg
								class="w-4 h-4"
								aria-hidden="true"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="M5 13l4 4L19 7"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						{:else}{$t('admin_page.save_results')}{/if}
					</GrayButton>
				</div>
			</div>
		{/if}
		<FinalResults
			bind:data={player_scores}
			{show_final_results}
			raw_final_results={final_results}
			avatar_map={
				Object.keys(final_results_avatar_map).length > 0
					? final_results_avatar_map
					: Object.fromEntries(players.map((player) => [player.username, player.avatar_params]))
			}
		/>
	{/if}
	<CountdownOverlay
		active={countdown_active}
		remaining_seconds={countdown_remaining_seconds}
		total_seconds={countdown_total_seconds}
		label="Question goes live in"
	/>
	{#if !success}
		{#if errorMessage !== ''}
			<p class="text-red-700">{errorMessage}</p>
		{/if}
	{:else if !game_started}
		<GameNotStarted
			{game_pin}
			bind:players
			{socket}
			{chat_messages}
			chat_block_reason={chat_block_reason}
			cqc_code={page.url.searchParams.get('cqc_code')}
		/>
	{:else}
		<SomeAdminScreen
			bind:final_results
			bind:final_results_avatar_map
			bind:socket_diagnostics_enabled
			{game_token}
			bind:quiz_data
			{bg_color}
			bind:player_scores
			{control_visible}
			on_toggle_socket_diagnostics={toggleSocketDiagnostics}
		/>
	{/if}
	<SocketDiagnostics
		socket={socket}
		label="admin"
		enabled={socket_diagnostics_enabled}
		details={{
			gamePin: game_pin,
			autoConnect: auto_connect,
			success,
			buildNumber: FRONTEND_BUILD_NUMBER,
			gameStarted: game_started,
			playerCount: players.length,
			quizLoaded: quiz_data !== undefined
		}}
	/>
</div>
<a
	onclick={request_answer_export}
	href="#"
	target="_blank"
	bind:this={dataexport_download_a}
	download=""
	class="absolute -top-3/4 -left-3/4 opacity-0">Download</a
>
