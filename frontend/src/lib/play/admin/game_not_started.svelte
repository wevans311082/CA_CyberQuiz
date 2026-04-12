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

	interface Props {
		game_pin: string;
		players: any;
		socket: any;
		cqc_code: string;
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
		chat_messages = [],
		chat_block_reason = null
	}: Props = $props();

	let fullscreen_open = $state(false);
	const { t } = getLocalization();
	let play_music = $state(false);
	let chat_input = $state('');

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
	<div class="flex justify-center w-full mt-4">
		<div>
			<GrayButton
				disabled={players.length < 1}
				onclick={() => {
					socket.emit('start_game', '');
				}}
				>{$t('admin_page.start_game')}
			</GrayButton>
		</div>
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
