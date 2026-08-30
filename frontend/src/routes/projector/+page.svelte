<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount } from 'svelte';
	import { socket } from '$lib/socket';
	import SituationBoard from '$lib/play/SituationBoard.svelte';
	import { QuizQuestionType } from '$lib/quiz_types';
	import type { Inject, QuizData, SituationStatus } from '$lib/quiz_types';
	import { pageTitle } from '$lib/brand';

	let { data } = $props();

	let success = $state(false);
	let quiz_data = $state<QuizData | null>(null);
	let situation_status = $state<SituationStatus | null>(null);
	let latest_inject = $state<Inject | null>(null);
	let clock = $state('');
	let errorMessage = $state('');
	let live_question = $state<any>(null);
	let live_question_index = $state(-1);
	let timer_remaining = $state(0);
	let timer_interval: ReturnType<typeof setInterval> | null = null;

	const connect = () => {
		socket.emit('register_as_remote', {
			game_pin: data.game_pin,
			game_id: data.game_token,
			host_token: data.host_token
		});
	};

	const onRegisteredAsAdmin = (payload: { game: string }) => {
		quiz_data = typeof payload.game === 'string' ? JSON.parse(payload.game) : payload.game as any;
		success = true;
		const current = (quiz_data as (QuizData & { current_question?: number }) | null)?.current_question;
		if (typeof current === 'number' && quiz_data?.questions?.[current]) {
			live_question_index = current;
			live_question = quiz_data.questions[current];
		}
		socket.emit('get_situation', {});
	};
	const onSetQuestionNumber = (payload: { question_index: number; question: any }) => {
		live_question_index = Number(payload.question_index);
		live_question = payload.question;
	};
	const onQuestionTimerStarted = (payload: { duration: number; server_timestamp: string }) => {
		const start = new Date(payload.server_timestamp).getTime();
		if (timer_interval) clearInterval(timer_interval);
		const tick = () => {
			timer_remaining = Math.max(0, payload.duration - (Date.now() - start) / 1000);
			if (timer_remaining <= 0 && timer_interval) {
				clearInterval(timer_interval);
				timer_interval = null;
			}
		};
		tick();
		timer_interval = setInterval(tick, 250);
	};
	const onQuestionTimerStopped = () => {
		timer_remaining = 0;
		if (timer_interval) clearInterval(timer_interval);
		timer_interval = null;
	};
	const onAdminRegistrationDenied = () => {
		errorMessage = 'Could not connect to session. Check your host link.';
	};
	const onSituationUpdated = (status: SituationStatus) => {
		if (status) situation_status = status;
	};
	const onInjectReceived = (inject: Inject) => {
		if (inject) latest_inject = inject;
	};
	const onSituationRoomData = (payload: { status?: SituationStatus; injects_log?: Array<{ inject: Inject }> }) => {
		if (payload?.status) situation_status = payload.status;
		const last = payload?.injects_log?.at(-1);
		if (last?.inject) latest_inject = last.inject;
	};

	onMount(() => {
		const tick = setInterval(() => {
			clock = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
		}, 1000);
		clock = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

		socket.on('registered_as_admin', onRegisteredAsAdmin);
		socket.on('set_question_number', onSetQuestionNumber);
		socket.on('question_timer_started', onQuestionTimerStarted);
		socket.on('question_timer_stopped', onQuestionTimerStopped);
		socket.on('admin_registration_denied', onAdminRegistrationDenied);
		socket.on('situation_updated', onSituationUpdated);
		socket.on('inject_received', onInjectReceived);
		socket.on('situation_room_data', onSituationRoomData);

		if (data.auto_connect) connect();

		return () => {
			socket.off('registered_as_admin', onRegisteredAsAdmin);
			socket.off('set_question_number', onSetQuestionNumber);
			socket.off('question_timer_started', onQuestionTimerStarted);
			socket.off('question_timer_stopped', onQuestionTimerStopped);
			socket.off('admin_registration_denied', onAdminRegistrationDenied);
			socket.off('situation_updated', onSituationUpdated);
			socket.off('inject_received', onInjectReceived);
			socket.off('situation_room_data', onSituationRoomData);
			clearInterval(tick);
			if (timer_interval) clearInterval(timer_interval);
		};
	});
</script>

<svelte:head>
	<title>{pageTitle('Situation Board')}</title>
</svelte:head>

{#if !success}
	<div class="flex min-h-screen items-center justify-center bg-slate-950 text-slate-300">
		<div class="text-center">
			{#if errorMessage}
				<p class="text-red-400">{errorMessage}</p>
			{:else if !data.auto_connect}
				<p>Missing session credentials. Open this page from the host console.</p>
			{:else}
				<p>Connecting to live session…</p>
			{/if}
		</div>
	</div>
{:else}
	<div class="min-h-screen bg-slate-950 text-white p-8">
		<div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-8">
			<div><p class="text-xs uppercase tracking-[0.3em] text-cyan-400">Live exercise</p><h1 class="text-3xl font-semibold">{quiz_data?.title ?? 'Exercise'}</h1></div>
			{#if timer_remaining > 0}<div class="text-4xl font-mono text-cyan-300">{Math.ceil(timer_remaining)}s</div>{/if}
		</div>
		{#if live_question?.type === QuizQuestionType.SLIDE || live_question?.type === QuizQuestionType.INFORMATION || live_question?.type === QuizQuestionType.FILE}
			<div class="mx-auto max-w-6xl rounded-2xl bg-white text-slate-900 p-8 shadow-2xl">
				<h2 class="text-4xl font-semibold mb-6">{@html live_question?.question ?? ''}</h2>
				{#if live_question?.image}<img src="/api/v1/storage/download/{live_question.image}" alt="Presentation content" class="max-h-[62vh] mx-auto object-contain" />{/if}
			</div>
		{:else if live_question}
			<div class="mx-auto max-w-6xl rounded-2xl bg-slate-900 border border-slate-700 p-10">
				<p class="text-sm text-slate-400">Question {live_question_index + 1}</p>
				<h2 class="text-5xl font-semibold mt-4">{@html live_question.question ?? ''}</h2>
			</div>
		{:else}
			<SituationBoard title={quiz_data?.title ?? 'Tabletop Exercise'} {situation_status} {latest_inject} {clock} />
		{/if}
	</div>
{/if}
