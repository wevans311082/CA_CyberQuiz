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

	onMount(() => {
		const tick = setInterval(() => {
			clock = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
		}, 1000);
		clock = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

		socket.on('registered_as_admin', (payload) => {
			quiz_data = JSON.parse(payload.game);
			success = true;
			socket.emit('get_situation', {});
		});
		socket.on('admin_registration_denied', () => {
			errorMessage = 'Could not connect to session. Check your host link.';
		});
		socket.on('situation_updated', (status: SituationStatus) => {
			if (status) situation_status = status;
		});
		socket.on('inject_received', (inject: Inject) => {
			if (inject) latest_inject = inject;
		});
		socket.on('situation_room_data', (payload: { status?: SituationStatus; injects_log?: Array<{ inject: Inject }> }) => {
			if (payload?.status) situation_status = payload.status;
			const last = payload?.injects_log?.at(-1);
			if (last?.inject) latest_inject = last.inject;
		});

		if (data.auto_connect) connect();

		return () => clearInterval(tick);
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