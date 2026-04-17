<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import PlayerAvatarChip from '$lib/play/player_avatar_chip.svelte';
	import RolesPanel from '$lib/play/RolesPanel.svelte';

	interface AvatarParams {
		skin_color?: number;
		hair_color?: number;
		facial_hair_type?: number;
		facial_hair_color?: number;
		top_type?: number;
		hat_color?: number;
		mouth_type?: number;
		eyebrow_type?: number;
		nose_type?: number;
		accessories_type?: number;
		clothe_type?: number;
		clothe_color?: number;
		clothe_graphic_type?: number;
	}

	interface LobbyPlayer {
		username: string;
		avatar_params?: AvatarParams | null;
	}

	interface Props {
		title: string;
		description: string;
		cover_image: string | undefined;
		players?: LobbyPlayer[];
		player_count?: number;
		started?: boolean;
		socket?: any;
		chat_messages?: Array<{
			sender: string;
			content: string;
			timestamp: string;
			sender_is_admin?: boolean;
		}>;
		chat_block_reason?: string | null;
		my_role?: string;
		player_roles?: Record<string, string>;
		scenario_type?: string;
		role_descriptions?: Record<string, string>;
		roles?: string[];
		hand_raised?: boolean;
	}

	let {
		title,
		description,
		cover_image,
		players = [],
		player_count = 0,
		started = false,
		socket,
		chat_messages = [],
		chat_block_reason = null,
		my_role = undefined,
		player_roles = {},
		scenario_type = undefined,
		role_descriptions = {},
		roles = [],
		hand_raised = $bindable(false)
	}: Props = $props();
	let chat_input = $state('');
	let roles_panel_open = $state(false);

	const toggle_hand = () => {
		if (!socket) return;
		if (hand_raised) {
			socket.emit('lower_hand', {});
			hand_raised = false;
		} else {
			socket.emit('raise_hand', {});
			hand_raised = true;
		}
	};

	// Admin can dismiss our hand
	if (socket) {
		socket.on('hand_dismissed', () => { hand_raised = false; });
	}

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

	const send_chat_message = () => {
		const content = chat_input.trim();
		if (!content || !socket) {
			return;
		}
		socket.emit('send_chat_message', { content });
		chat_input = '';
	};

	const sceneElements = Array.from({ length: 14 }, (_, index) => ({
		id: index,
		size: 80 + ((index * 19) % 120),
		left: (index * 9) % 100,
		delay: `${(index % 5) * 0.7}s`,
		duration: `${12 + (index % 6) * 2}s`
	}));
</script>

<div class="relative flex min-h-screen w-screen items-center justify-center overflow-hidden px-6 py-10 text-slate-950 dark:text-white">
	<div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.14),transparent_30%),radial-gradient(circle_at_bottom_right,rgba(20,184,166,0.18),transparent_30%),linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.02))]"></div>
	{#each sceneElements as element}
		<div
			class="lobby-orb absolute rounded-full"
			style="width: {element.size}px; height: {element.size}px; left: {element.left}%; animation-delay: {element.delay}; animation-duration: {element.duration};"
		></div>
	{/each}

	<div class="relative z-10 grid w-full max-w-6xl gap-8 lg:grid-cols-[1.4fr,0.9fr]">
		<section class="rounded-[2rem] border border-white/60 bg-white/50 p-8 shadow-[0_24px_80px_rgba(15,23,42,0.16)] backdrop-blur dark:border-slate-700/80 dark:bg-slate-900/45">
			<p class="text-sm font-semibold uppercase tracking-[0.34em] text-teal-700 dark:text-cyan-300">
				{started ? 'Quiz starting' : 'Lobby'}
			</p>
			<h1 class="mt-4 text-4xl font-semibold tracking-tight sm:text-6xl">{@html title}</h1>
			<p class="mt-5 max-w-2xl text-lg leading-8 text-slate-700 dark:text-slate-300">
				{#if started}
					The host has started the session. Your first question will appear here in a moment.
				{:else}
					Waiting for the quiz to start. Stay on this screen while the host brings everyone in.
				{/if}
			</p>
			{#if description}
				<p class="mt-4 text-base leading-7 text-slate-600 dark:text-slate-400">{@html description}</p>
			{/if}
			{#if scenario_type === 'tabletop' && my_role}
				<div class="mt-6 flex flex-wrap items-start gap-3">
					<div class="inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-900 dark:text-cyan-100">
						<span class="h-2 w-2 rounded-full bg-cyan-500"></span>
						Your Role: <strong>{my_role}</strong>
					</div>
					{#if roles.length > 0}
						<button type="button" onclick={() => roles_panel_open = true} class="inline-flex items-center gap-1.5 rounded-full border border-teal-400/30 bg-teal-500/10 px-3 py-2 text-xs font-medium text-teal-800 dark:text-teal-200 hover:bg-teal-500/20 transition">
							🎭 View All Roles
						</button>
					{/if}
				</div>
				{#if role_descriptions[my_role]}
					<p class="mt-2 text-sm text-slate-600 dark:text-slate-300 italic max-w-lg">{role_descriptions[my_role]}</p>
				{/if}
			{:else if scenario_type === 'tabletop' && !my_role}
				<div class="mt-6 inline-flex items-center gap-2 rounded-full border border-amber-400/40 bg-amber-500/10 px-4 py-2 text-sm font-medium text-amber-900 dark:text-amber-100">
					<span class="h-2 w-2 animate-pulse rounded-full bg-amber-500"></span>
					Awaiting role assignment from the facilitator…
				</div>
			{/if}
			<div class="mt-8 flex flex-wrap gap-3 items-center">
				<div class="inline-flex items-center gap-3 rounded-full border border-teal-700/20 bg-teal-600/10 px-5 py-3 text-sm font-medium text-teal-900 dark:border-cyan-300/20 dark:bg-cyan-400/10 dark:text-cyan-100">
					<span class="h-2.5 w-2.5 rounded-full bg-teal-600 dark:bg-cyan-300"></span>
					{#if started}
						Waiting for the first question
					{:else}
						Waiting for the quiz to start
					{/if}
				</div>
				<!-- Hands Up button (shown in tabletop during lobby) -->
				{#if socket && scenario_type === 'tabletop'}
					<button
						type="button"
						onclick={toggle_hand}
						class="inline-flex items-center gap-2 rounded-full px-4 py-2.5 text-sm font-semibold transition shadow-sm"
						class:bg-amber-400={hand_raised}
						class:text-amber-900={hand_raised}
						class:hover:bg-amber-500={hand_raised}
						class:bg-slate-200={!hand_raised}
						class:dark:bg-slate-700={!hand_raised}
						class:text-slate-800={!hand_raised}
						class:dark:text-slate-100={!hand_raised}
						class:hover:bg-slate-300={!hand_raised}
						title={hand_raised ? 'Lower your hand' : 'Raise your hand to get the facilitator\'s attention'}
					>
						{hand_raised ? '✋ Hand Raised' : '🖐️ Raise Hand'}
					</button>
				{/if}
			</div>
			{#if cover_image}
				<div class="mt-8 overflow-hidden rounded-[1.5rem] border border-white/70 bg-white/70 p-3 dark:border-slate-700 dark:bg-slate-950/60">
					<MediaComponent src={cover_image} css_classes="max-h-[28vh] w-full object-contain" />
				</div>
			{/if}
		</section>

		<aside class="rounded-[2rem] border border-white/60 bg-white/50 p-6 shadow-[0_24px_80px_rgba(15,23,42,0.16)] backdrop-blur dark:border-slate-700/80 dark:bg-slate-900/45">
			<div class="flex items-center justify-between gap-4 border-b border-slate-200/70 pb-4 dark:border-slate-700/70">
				<div>
					<p class="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">Players</p>
					<h2 class="mt-2 text-3xl font-semibold">{player_count}</h2>
				</div>
				<div class="rounded-full bg-slate-950 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-white dark:bg-white dark:text-slate-950">
					Live Lobby
				</div>
			</div>
			{#if players.length > 0}
				<div class="mt-5 grid max-h-[45vh] gap-3 overflow-auto pr-2">
					{#each players as player, idx}
						<div style="animation-delay: {idx * 50}ms" class="chip-reveal flex items-center gap-2">
							<PlayerAvatarChip username={player.username} avatar_params={player.avatar_params} />
							{#if scenario_type === 'tabletop' && player_roles[player.username]}
								<span class="rounded-full bg-teal-600/80 px-2 py-0.5 text-[10px] font-semibold text-white">{player_roles[player.username]}</span>
							{/if}
						</div>
					{/each}
				</div>
			{:else}
				<p class="mt-5 text-sm leading-6 text-slate-600 dark:text-slate-400">No one else is in the lobby yet.</p>
			{/if}

			<div class="mt-6 border-t border-slate-200/70 pt-4 dark:border-slate-700/70">
				<p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Community Chat</p>
				<div class="mt-3 max-h-44 space-y-2 overflow-auto rounded-xl border border-slate-200/70 bg-white/70 p-3 dark:border-slate-700 dark:bg-slate-950/60">
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
		</aside>
	</div>
</div>

<RolesPanel bind:open={roles_panel_open} {roles} {role_descriptions} {player_roles} />

<style>
	.lobby-orb {
		top: -8%;
		background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.95), rgba(45, 212, 191, 0.18));
		filter: blur(1px);
		opacity: 0.7;
		animation-name: floatLobbyOrb;
		animation-iteration-count: infinite;
		animation-timing-function: ease-in-out;
	}

	@keyframes floatLobbyOrb {
		0% {
			transform: translate3d(0, 0, 0) scale(0.96);
			opacity: 0.28;
		}
		25% {
			transform: translate3d(18px, 22vh, 0) scale(1.04);
			opacity: 0.58;
		}
		50% {
			transform: translate3d(-12px, 48vh, 0) scale(1);
			opacity: 0.42;
		}
		75% {
			transform: translate3d(14px, 71vh, 0) scale(1.08);
			opacity: 0.5;
		}
		100% {
			transform: translate3d(-8px, 108vh, 0) scale(0.94);
			opacity: 0.14;
		}
	}

	.chip-reveal {
		opacity: 0;
		transform: translateY(6px) scale(0.98);
		animation: chipReveal 280ms ease-out forwards;
	}

	@keyframes chipReveal {
		to {
			opacity: 1;
			transform: translateY(0) scale(1);
		}
	}
</style>
