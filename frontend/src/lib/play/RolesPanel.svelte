<!--
SPDX-FileCopyrightText: 2024 CA CyberQuiz Contributors
SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	interface Props {
		open?: boolean;
		embedded?: boolean;
		roles: string[];
		role_descriptions?: Record<string, string>;
		player_roles?: Record<string, string>;
		onclose?: () => void;
	}

	let {
		open = $bindable(false),
		embedded = false,
		roles = [],
		role_descriptions = {},
		player_roles = {},
		onclose
	}: Props = $props();

	// Build reverse map: role -> [usernames]
	const role_to_players = $derived(() => {
		const map: Record<string, string[]> = {};
		for (const role of roles) {
			map[role] = [];
		}
		for (const [username, role] of Object.entries(player_roles)) {
			if (map[role]) {
				map[role].push(username);
			} else {
				map[role] = [username];
			}
		}
		return map;
	});
</script>

{#snippet roleList()}
	{#each roles as role}
		{@const assigned = role_to_players()[role] ?? []}
		<div class="rounded-lg border border-slate-600/50 bg-slate-800/50 p-3">
			<div class="flex items-start gap-2">
				<span class="mt-0.5 inline-block whitespace-nowrap rounded-full border border-cyan-500/40 bg-cyan-500/15 px-2.5 py-0.5 text-xs font-semibold text-cyan-200">{role}</span>
				<div class="min-w-0 flex-1">
					{#if role_descriptions[role]}
						<p class="text-xs leading-snug text-slate-400">{role_descriptions[role]}</p>
					{/if}
					{#if assigned.length > 0}
						<div class="mt-1.5 flex flex-wrap gap-1">
							{#each assigned as player}
								<span class="rounded-full border border-slate-600/60 bg-slate-700/60 px-2 py-0.5 text-xs text-slate-200">{player}</span>
							{/each}
						</div>
					{:else}
						<p class="mt-1 text-xs italic text-slate-500">Unassigned</p>
					{/if}
				</div>
			</div>
		</div>
	{/each}
	{#if roles.length === 0}
		<p class="py-4 text-center text-sm text-slate-500">No roles defined for this exercise.</p>
	{/if}
{/snippet}

{#if embedded}
	<div class="flex flex-col gap-3">
		{@render roleList()}
	</div>
{:else if open}
	<div
		class="fixed inset-0 z-40 bg-black/30"
		onclick={() => {
			open = false;
			if (onclose) onclose();
		}}
		role="button"
		tabindex="-1"
		aria-label="Close roles panel"
		onkeydown={(e) => {
			if (e.key === 'Escape') {
				open = false;
				if (onclose) onclose();
			}
		}}
	></div>

	<div class="host-panel fixed right-4 top-16 z-50 w-80 max-h-[80vh] overflow-y-auto border-cyan-500/40">
		<div class="mb-3 flex items-center justify-between border-b border-slate-700/60 pb-3">
			<h3 class="text-sm font-bold text-cyan-300">🎭 Roles</h3>
			<button type="button" class="host-btn px-2.5" onclick={() => { open = false; if (onclose) onclose(); }} aria-label="Close">✕</button>
		</div>
		<div class="flex flex-col gap-3">
			{@render roleList()}
		</div>
	</div>
{/if}
