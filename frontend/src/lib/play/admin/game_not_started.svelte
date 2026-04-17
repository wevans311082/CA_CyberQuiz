<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	// import AudioPlayer from '$lib/play/audio_player.svelte';
	import ControllerCodeDisplay from '$lib/components/controller/code.svelte';
	import { getLocalization } from '$lib/i18n';
	import GrayButton from '$lib/components/buttons/gray.svelte';
	import PlayerAvatarChip from '$lib/play/player_avatar_chip.svelte';
	import { fade } from 'svelte/transition';
	import type { QuizData } from '$lib/quiz_types';

	interface Props {
		game_pin: string;
		players: any;
		socket: any;
		cqc_code: string;
		quiz_data?: QuizData | null;
		chat_messages?: Array<{
			sender: string;
			content: string;
			timestamp: string;
			sender_is_admin?: boolean;
		}>;
		chat_block_reason?: string | null;
	}

	let {
		game_pin,
		players = $bindable(),
		socket,
		cqc_code = $bindable(),
		quiz_data = null,
		chat_messages = [],
		chat_block_reason = null
	}: Props = $props();

	let fullscreen_open = $state(false);
	const { t } = getLocalization();
	let play_music = $state(false);
	let chat_input = $state('');

	// Tabletop role assignment state
	let drag_player = $state<string | null>(null);
	let drag_over_role = $state<string | null>(null);
	let pending_proposals = $state<Record<string, string>>({});  // username -> proposed role
	let accepted_roles = $state<Record<string, string>>({});     // username -> confirmed role
	let declined_set = $state<Set<string>>(new Set());

	const propose_role = (username: string, role: string) => {
		socket.emit('propose_role', { username, role });
		pending_proposals = { ...pending_proposals, [username]: role };
	};

	const is_tabletop = $derived(quiz_data?.scenario_type === 'tabletop' && (quiz_data?.roles?.length ?? 0) > 0);

	// Hands up state
	let raised_hands = $state<string[]>([]);
	socket.on('hands_updated', (data: { hands: string[] }) => {
		raised_hands = data?.hands ?? [];
	});

	const dismiss_hand = (username: string) => socket.emit('dismiss_hand', { username });
	const dismiss_all_hands = () => socket.emit('dismiss_all_hands', {});

	// Role readiness check
	const roles_ready = $derived(
		!is_tabletop ||
		(quiz_data?.roles ?? []).every(role =>
			Object.values(accepted_roles).includes(role)
		)
	);

	socket.on('role_accepted_ack', (data: { username: string; role: string }) => {
		if (data?.username) {
			accepted_roles = { ...accepted_roles, [data.username]: data.role };
			const pending = { ...pending_proposals };
			delete pending[data.username];
			pending_proposals = pending;
		}
	});
	socket.on('role_declined', (data: { username: string; role: string }) => {
		if (data?.username) {
			const pending = { ...pending_proposals };
			delete pending[data.username];
			pending_proposals = pending;
			declined_set = new Set([...declined_set, data.username]);
			setTimeout(() => {
				declined_set = new Set([...declined_set].filter(u => u !== data.username));
			}, 4000);
		}
	});

	// Drag handlers
	function on_dragstart(e: DragEvent, username: string) {
		drag_player = username;
		e.dataTransfer?.setData('text/plain', username);
	}
	function on_dragover(e: DragEvent, role: string) {
		e.preventDefault();
		drag_over_role = role;
	}
	function on_dragleave() { drag_over_role = null; }
	function on_drop(e: DragEvent, role: string) {
		e.preventDefault();
		drag_over_role = null;
		const un = e.dataTransfer?.getData('text/plain') ?? drag_player;
		if (un) propose_role(un, role);
		drag_player = null;
	}
	function on_dragend() { drag_player = null; drag_over_role = null; }

	const friendlyChatBlockReason = (reason: string | null) => {
		if (!reason) {
			return null;
		}
		const reasonMap: Record<string, string> = {
			not_in_game: 'You are not in an active lobby.',
			game_already_started: 'Chat is closed after the quiz starts.',
			empty_message: 'Message cannot be empty.',
			message_too_long: 'Message is too long (max 280 characters).',
			message_blocked_by_moderation: 'Message blocked by moderation policy.',
			rate_limited: 'You are sending messages too quickly. Slow down a bit.',
			too_many_messages: 'Too many messages in a short time. Please wait a moment.'
		};
		return reasonMap[reason] ?? 'Message blocked.';
	};

	if (cqc_code === 'null') {
		cqc_code = null;
	}

	const kick_player = (username: string) => {
		socket.emit('kick_player', { username: username });
		for (let i = 0; i < players.length; i++) {
			console.log(players[i].username, username);
			if (players[i].username === username) {
				players.splice(i, 1);
				break;
			}
		}
		players = players;
	};

	const send_chat_message = () => {
		const content = chat_input.trim();
		if (!content) {
			return;
		}
		socket.emit('send_chat_message', { content });
		chat_input = '';
	};
</script>

<div class="w-full h-full">
	<!-- <AudioPlayer bind:play={play_music} /> -->
	<div class="grid grid-cols-3 pt-12">
		<!--mt-12 -->
		<div class="flex justify-center">
			<p class="m-auto text-2xl">
				{$t('play_page.join_description', {
					url:
						window.location.host === 'classquiz.de'
							? 'cquiz.de'
							: `${window.location.host}/play`,
					pin: game_pin
				})}
			</p>
		</div>
		<img
			onclick={() => (fullscreen_open = true)}
			alt="QR code to join the game"
			src="/api/v1/utils/qr/{game_pin}"
			class="block mx-auto w-1/2 dark:bg-white shadow-2xl rounded-sm hover:cursor-pointer"
		/>
		{#if cqc_code}
			<div class="m-auto">
				<div class="flex justify-center my-4">
					<p class="m-auto text-2xl">
						{#if players.length <= 1}
							{$t('play_page.players_waiting', {
								count: players.length ?? 0
							})}
						{:else}
							{$t('play_page.players_waiting_plural', {
								count: players.length ?? 0
							})}
						{/if}
					</p>
				</div>
				<div class="flex-col flex justify-center">
					<p class="mx-auto">{$t('play_page.join_by_entering_code')}</p>
					<ControllerCodeDisplay code={cqc_code} />
				</div>
			</div>
		{:else}
			<div class="flex justify-center">
				<p class="m-auto text-2xl">
					{#if players.length <= 1}
						{$t('play_page.players_waiting', {
							count: players.length ?? 0
						})}
					{:else}
						{$t('play_page.players_waiting_plural', {
							count: players.length ?? 0
						})}
					{/if}
				</p>
			</div>
		{/if}
	</div>
	<p class="text-3xl text-center">
		{$t('words.pin')}: <span class="select-all">{game_pin}</span>
	</p>
	<div class="flex flex-col justify-center items-center w-full mt-4 gap-2">
		{#if !roles_ready}
			<p class="text-xs text-amber-600 dark:text-amber-400 font-medium">⚠ Not all roles have been accepted yet. You can still start, but some roles remain unassigned.</p>
		{/if}
		<GrayButton
			disabled={players.length < 1}
			onclick={() => {
				socket.emit('start_game', '');
			}}
			>{$t('admin_page.start_game')}
		</GrayButton>
	</div>
	<div class="flex flex-row w-full mt-4 px-10 flex-wrap">
		{#if players.length > 0}
			{#each players as player}
				<div class="p-2 m-2 rounded-sm">
					<div class="group relative">
						<button type="button" onclick={() => kick_player(player.username)} class="rounded-2xl">
							<PlayerAvatarChip username={player.username} avatar_params={player.avatar_params} compact={true} clickable={true} />
						</button>
						<span class="pointer-events-none absolute -top-2 right-0 rounded-full bg-red-600 px-2 py-0.5 text-[10px] font-semibold text-white opacity-0 transition-opacity group-hover:opacity-100">kick</span>
					</div>
				</div>
			{/each}
		{/if}
	</div>

	<!-- Hands Up Panel -->
	{#if raised_hands.length > 0}
		<div class="mx-auto mt-4 w-full max-w-5xl rounded-2xl border border-amber-300 bg-amber-50/80 p-4 dark:border-amber-700 dark:bg-amber-900/20">
			<div class="flex items-center justify-between mb-2">
				<h2 class="text-sm font-bold uppercase tracking-wide text-amber-700 dark:text-amber-300">✋ Hands Raised ({raised_hands.length})</h2>
				<button type="button" onclick={dismiss_all_hands} class="text-xs text-amber-600 hover:text-amber-800 dark:text-amber-400 dark:hover:text-amber-200 underline">Dismiss All</button>
			</div>
			<div class="flex flex-wrap gap-2">
				{#each raised_hands as username}
					<div class="inline-flex items-center gap-1.5 rounded-full bg-amber-200 dark:bg-amber-800 px-3 py-1 text-sm font-medium text-amber-900 dark:text-amber-100">
						<span>✋ {username}</span>
						<button type="button" onclick={() => dismiss_hand(username)} class="text-amber-700 hover:text-red-600 dark:text-amber-300 dark:hover:text-red-400 font-bold leading-none" title="Dismiss">×</button>
					</div>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Tabletop Role Assignment -->
	{#if is_tabletop}
		<div class="mx-auto mt-6 w-full max-w-5xl rounded-2xl border border-teal-200 bg-teal-50/80 p-5 dark:border-teal-700 dark:bg-teal-900/30">
			<h2 class="text-sm font-bold uppercase tracking-wide text-teal-700 dark:text-teal-300 mb-1">Role Assignment</h2>
			<p class="text-xs text-teal-600 dark:text-teal-400 mb-4">Drag a player chip onto a role to propose it. Players will be prompted to accept or decline.</p>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<!-- Players (draggable) -->
				<div>
					<h3 class="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400 mb-2">Players</h3>
					<div class="flex flex-wrap gap-2">
						{#each players as player}
							{@const assigned = accepted_roles[player.username]}
							{@const pending = pending_proposals[player.username]}
							{@const declined = declined_set.has(player.username)}
							<!-- svelte-ignore a11y_no_static_element_interactions -->
							<div
								class="relative cursor-grab active:cursor-grabbing rounded-full select-none transition"
								class:opacity-50={!!assigned}
								draggable="true"
								ondragstart={(e) => on_dragstart(e, player.username)}
								ondragend={on_dragend}
							>
								<PlayerAvatarChip username={player.username} avatar_params={player.avatar_params} compact={true} clickable={false} />
								{#if assigned}
									<span class="absolute -top-1 -right-1 rounded-full bg-teal-600 text-[9px] font-bold text-white px-1.5 py-0.5 max-w-[5rem] truncate" title={assigned}>{assigned}</span>
								{:else if pending}
									<span class="absolute -top-1 -right-1 rounded-full bg-amber-500 text-[9px] font-bold text-white px-1.5 py-0.5">pending…</span>
								{:else if declined}
									<span class="absolute -top-1 -right-1 rounded-full bg-red-600 text-[9px] font-bold text-white px-1.5 py-0.5" transition:fade>declined</span>
								{/if}
							</div>
						{/each}
						{#if players.length === 0}
							<p class="text-xs text-gray-400 italic">No players yet</p>
						{/if}
					</div>
				</div>

				<!-- Role drop zones -->
				<div>
					<h3 class="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400 mb-2">Roles</h3>
					<div class="grid grid-cols-2 gap-2">
						{#each quiz_data?.roles ?? [] as role}
							{@const assigned_players = Object.entries(accepted_roles).filter(([, r]) => r === role).map(([u]) => u)}
							{@const pending_players = Object.entries(pending_proposals).filter(([, r]) => r === role).map(([u]) => u)}
							<!-- svelte-ignore a11y_no_static_element_interactions -->
							<div
								class="relative min-h-[4rem] rounded-xl border-2 p-2 text-sm font-semibold transition"
								class:border-teal-400={drag_over_role === role}
								class:bg-teal-100={drag_over_role === role}
								class:dark:bg-teal-800={drag_over_role === role}
								class:border-gray-300={drag_over_role !== role}
								class:dark:border-gray-600={drag_over_role !== role}
								class:bg-white={drag_over_role !== role}
								class:dark:bg-gray-800={drag_over_role !== role}
								ondragover={(e) => on_dragover(e, role)}
								ondragleave={on_dragleave}
								ondrop={(e) => on_drop(e, role)}
							>
								<span class="text-gray-700 dark:text-gray-200 font-semibold">{role}</span>
						{#if quiz_data?.role_descriptions?.[role]}
							<p class="text-[10px] text-gray-500 dark:text-gray-400 leading-snug mt-0.5 font-normal">{quiz_data.role_descriptions[role]}</p>
						{/if}
								<div class="flex flex-wrap gap-1 mt-1">
									{#each assigned_players as un}
										<span class="rounded-full bg-teal-600 text-white text-[10px] px-1.5 py-0.5 font-semibold">{un} ✓</span>
									{/each}
									{#each pending_players as un}
										<span class="rounded-full bg-amber-400 text-white text-[10px] px-1.5 py-0.5 font-semibold">{un} …</span>
									{/each}
								</div>
								{#if drag_over_role === role}
									<div class="absolute inset-0 flex items-center justify-center rounded-xl text-xs text-teal-600 font-bold pointer-events-none">Drop here</div>
								{/if}
							</div>
						{/each}
					</div>
				</div>
			</div>
		</div>
	{/if}

	<div class="mx-auto mt-4 w-full max-w-3xl rounded-2xl border border-slate-300/70 bg-white/70 p-4 dark:border-slate-700 dark:bg-slate-900/70">
		<p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">Community Chat</p>
		<div class="mt-3 max-h-48 space-y-2 overflow-auto rounded-xl border border-slate-200/70 bg-white/80 p-3 dark:border-slate-700 dark:bg-slate-950/60">
			{#if chat_messages.length === 0}
				<p class="text-xs text-slate-500 dark:text-slate-400">No messages yet.</p>
			{:else}
				{#each chat_messages as message}
					<div class="rounded-lg bg-slate-100/70 px-2 py-1 text-xs dark:bg-slate-800/80">
						<p class="font-semibold text-slate-700 dark:text-slate-200">
							{message.sender}{message.sender_is_admin ? ' (host)' : ''}
						</p>
						<p class="text-slate-700 dark:text-slate-200">{message.content}</p>
					</div>
				{/each}
			{/if}
		</div>
		{#if chat_block_reason}
			<p class="mt-2 text-xs font-medium text-red-600 dark:text-red-400">{friendlyChatBlockReason(chat_block_reason)}</p>
		{/if}
		<div class="mt-3 flex gap-2">
			<input
				class="min-w-0 flex-1 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-hidden focus:border-teal-600 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
				bind:value={chat_input}
				maxlength="280"
				onkeydown={(e) => {
					if (e.key === 'Enter') {
						send_chat_message();
					}
				}}
				placeholder="Type a message"
			/>
			<button type="button" class="rounded-xl bg-teal-600 px-3 py-2 text-xs font-semibold text-white hover:bg-teal-700" onclick={send_chat_message}>
				Send
			</button>
		</div>
	</div>
</div>

{#if fullscreen_open}
	<div
		class="fixed top-0 left-0 z-50 w-screen h-screen bg-black/50 flex p-2"
		transition:fade|global={{ duration: 80 }}
		onclick={() => (fullscreen_open = false)}
		tabindex="0"
		role="button"
		aria-label="Close modal"
		onkeydown={(e) =>
			e.key === 'Enter' || e.key === ' '
				? () => {
						fullscreen_open = false;
					}
				: null}
	>
		<img
			alt="QR code to join the game"
			src="/api/v1/utils/qr/{game_pin}"
			class="object-contain rounded-sm m-auto h-full bg-white"
		/>
	</div>
{/if}
