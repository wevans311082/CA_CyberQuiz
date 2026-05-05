<!--
SPDX-FileCopyrightText: 2026 CA CyberQuiz Team

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Socket } from 'socket.io-client';

	interface Props {
		socket: Socket;
		players: Array<{ username: string }>;
	}

	let { socket, players }: Props = $props();

	// Available emoji presets
	const emoji_presets = [
		{ emoji: '👍', label: 'Thumbs Up', description: 'Great job!' },
		{ emoji: '😉', label: 'Wink', description: 'You got this' },
		{ emoji: '🚀', label: 'Rocket', description: 'Launch!' },
		{ emoji: '⭐', label: 'Star', description: 'Excellent work' },
		{ emoji: '🔥', label: 'Fire', description: 'On fire!' },
		{ emoji: '💡', label: 'Lightbulb', description: 'Smart thinking' },
		{ emoji: '❌', label: 'X', description: 'Not quite' },
		{ emoji: '⏰', label: 'Clock', description: 'Time is ticking' },
		{ emoji: '🎯', label: 'Target', description: 'Focus!' },
		{ emoji: '🏆', label: 'Trophy', description: 'Champion!' },
	];

	let panel_open = $state(false);
	let selected_emoji = $state('👍');
	let custom_message = $state('');
	let selected_player = $state<string | null>(null);

	const send_emoji = () => {
		if (!selected_player) {
			alert('Please select a player');
			return;
		}

		socket.emit('send_emoji_prompt', {
			target_player: selected_player,
			emoji: selected_emoji,
			message: custom_message.trim()
		});

		// Reset form
		custom_message = '';
		selected_emoji = '👍';
		selected_player = null;
	};

	const send_to_all = () => {
		socket.emit('send_emoji_prompt', {
			target_player: null, // null means broadcast to all
			emoji: selected_emoji,
			message: custom_message.trim()
		});

		// Reset form
		custom_message = '';
		selected_emoji = '👍';
		selected_player = null;
	};
</script>

<div class="border-t border-white/10 pt-3">
	<button
		onclick={() => (panel_open = !panel_open)}
		class="admin-button w-full mb-2"
	>
		{panel_open ? '✕ Emoji Prompts' : '😊 Emoji Prompts'}
	</button>

	{#if panel_open}
		<div class="bg-white/5 rounded border border-white/10 p-3 space-y-3">
			<!-- Emoji Selector -->
			<div>
				<label class="block text-xs font-semibold text-white/80 mb-2">Select Emoji</label>
				<div class="grid grid-cols-5 gap-2">
					{#each emoji_presets as preset (preset.emoji)}
						<button
							onclick={() => (selected_emoji = preset.emoji)}
							class="text-2xl p-2 rounded border {selected_emoji === preset.emoji
								? 'border-white/40 bg-white/10'
								: 'border-white/10 hover:bg-white/5'}"
							title={preset.description}
						>
							{preset.emoji}
						</button>
					{/each}
				</div>
			</div>

			<!-- Custom Message -->
			<div>
				<label class="block text-xs font-semibold text-white/80 mb-1">Custom Message (optional)</label>
				<input
					type="text"
					bind:value={custom_message}
					maxlength="50"
					placeholder="e.g. 'Great job!' or 'Keep thinking'"
					class="w-full rounded border border-white/20 bg-white/10 px-2 py-1.5 text-xs text-white placeholder:text-white/40 outline-hidden"
				/>
				<p class="text-[10px] text-white/50 mt-1">{custom_message.length}/50</p>
			</div>

			<!-- Player Selection -->
			<div>
				<label class="block text-xs font-semibold text-white/80 mb-2">Send To</label>
				<select
					bind:value={selected_player}
					class="w-full rounded border border-white/20 bg-white/10 px-2 py-1.5 text-xs text-white outline-hidden"
				>
					<option value={null}>Select a player...</option>
					{#each players as player (player.username)}
						<option value={player.username}>
							{player.username}
						</option>
					{/each}
				</select>
			</div>

			<!-- Send Buttons -->
			<div class="flex gap-2">
				<button
					onclick={send_emoji}
					disabled={!selected_player}
					class="admin-button flex-1 text-xs disabled:opacity-50"
				>
					Send to Player
				</button>
				<button
					onclick={send_to_all}
					class="admin-button flex-1 text-xs bg-blue-600 hover:bg-blue-700"
				>
					Send to All
				</button>
			</div>
		</div>
	{/if}
</div>
