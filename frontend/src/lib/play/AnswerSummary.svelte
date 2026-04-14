<!--
SPDX-FileCopyrightText: 2025

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { fade } from 'svelte/transition';

	interface Props {
		total: number;
		answers: Record<string, number>;
	}

	let { total, answers }: Props = $props();

	let sorted_answers = $derived(
		Object.entries(answers).sort(([, a], [, b]) => b - a)
	);

	const bar_colors = ['bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-red-500', 'bg-purple-500', 'bg-teal-500', 'bg-orange-500', 'bg-pink-500'];
</script>

<div class="w-full max-w-lg mx-auto mt-6 mb-4" transition:fade={{ duration: 200 }}>
	<h3 class="text-center text-xl font-semibold mb-4">Answer Summary</h3>
	<p class="text-center text-sm text-gray-500 dark:text-gray-400 mb-4">{total} response{total !== 1 ? 's' : ''}</p>
	<div class="space-y-3">
		{#each sorted_answers as [answer, count], i}
			{@const pct = total > 0 ? Math.round((count / total) * 100) : 0}
			<div>
				<div class="flex justify-between text-sm mb-1">
					<span class="font-medium truncate max-w-[70%]">{answer}</span>
					<span class="text-gray-500 dark:text-gray-400">{count} ({pct}%)</span>
				</div>
				<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
					<div
						class="h-full rounded-full transition-all duration-500 {bar_colors[i % bar_colors.length]}"
						style="width: {pct}%"
					></div>
				</div>
			</div>
		{/each}
	</div>
</div>
