<!--
SPDX-FileCopyrightText: 2024 CA CyberQuiz Contributors
SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	interface Props {
		open: boolean;
		roles: string[];
		role_descriptions?: Record<string, string>;
		player_roles?: Record<string, string>;  // username -> role
		onclose?: () => void;
	}

	let { open = $bindable(), roles = [], role_descriptions = {}, player_roles = {}, onclose }: Props = $props();

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

{#if open}
	<!-- Backdrop -->
	<div
		class="fixed inset-0 bg-black/30 z-40"
		onclick={() => { open = false; if (onclose) onclose(); }}
		role="button"
		tabindex="-1"
		aria-label="Close roles panel"
		onkeydown={(e) => { if (e.key === 'Escape') { open = false; if (onclose) onclose(); } }}
	></div>

	<!-- Panel -->
	<div class="fixed right-4 top-16 z-50 w-80 max-h-[80vh] overflow-y-auto rounded-xl shadow-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
		<div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
			<h3 class="font-semibold text-base text-gray-800 dark:text-gray-100">🎭 Roles</h3>
			<button
				type="button"
				class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 text-xl leading-none"
				onclick={() => { open = false; if (onclose) onclose(); }}
				aria-label="Close"
			>&times;</button>
		</div>
		<div class="p-3 flex flex-col gap-3">
			{#each roles as role}
				{@const assigned = role_to_players()[role] ?? []}
				<div class="rounded-lg border border-gray-200 dark:border-gray-600 p-3">
					<div class="flex items-start gap-2">
						<span class="mt-0.5 inline-block rounded-full bg-teal-600 px-2.5 py-0.5 text-xs font-semibold text-white whitespace-nowrap">{role}</span>
						<div class="flex-1 min-w-0">
							{#if role_descriptions[role]}
								<p class="text-xs text-gray-500 dark:text-gray-400 leading-snug">{role_descriptions[role]}</p>
							{/if}
							{#if assigned.length > 0}
								<div class="mt-1.5 flex flex-wrap gap-1">
									{#each assigned as player}
										<span class="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-0.5 rounded-full">{player}</span>
									{/each}
								</div>
							{:else}
								<p class="mt-1 text-xs text-gray-400 italic">Unassigned</p>
							{/if}
						</div>
					</div>
				</div>
			{/each}
			{#if roles.length === 0}
				<p class="text-sm text-gray-400 text-center py-4">No roles defined for this exercise.</p>
			{/if}
		</div>
	</div>
{/if}
