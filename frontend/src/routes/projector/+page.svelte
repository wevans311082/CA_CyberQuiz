<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount } from 'svelte';
	import { socket } from '$lib/socket';
	import SituationBoard from '$lib/play/SituationBoard.svelte';
	import type { Inject, QuizData, SituationStatus } from '$lib/quiz_types';
	import { pageTitle } from '$lib/brand';

	let { data } = $props();

	let success = $state(false);
	let quiz_data = $state<QuizData | null>(null);
	let situation_status = $state<SituationStatus | null>(null);
	let latest_inject = $state<Inject | null>(null);
	let clock = $state('');
	let errorMessage = $state('');

	const connect = () => {
		socket.emit('register_as_admin', {
			game_pin: data.game_pin,
			game_id: data.game_token,
			host_token: data.host_token
		});
	};

	const onRegisteredAsAdmin = (payload: { game: string }) => {
		quiz_data = JSON.parse(payload.game);
		success = true;
		socket.emit('get_situation', {});
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
		socket.on('admin_registration_denied', onAdminRegistrationDenied);
		socket.on('situation_updated', onSituationUpdated);
		socket.on('inject_received', onInjectReceived);
		socket.on('situation_room_data', onSituationRoomData);

		if (data.auto_connect) connect();

		return () => {
			socket.off('registered_as_admin', onRegisteredAsAdmin);
			socket.off('admin_registration_denied', onAdminRegistrationDenied);
			socket.off('situation_updated', onSituationUpdated);
			socket.off('inject_received', onInjectReceived);
			socket.off('situation_room_data', onSituationRoomData);
			clearInterval(tick);
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
	<SituationBoard
		title={quiz_data?.title ?? 'Tabletop Exercise'}
		{situation_status}
		{latest_inject}
		{clock}
	/>
{/if}