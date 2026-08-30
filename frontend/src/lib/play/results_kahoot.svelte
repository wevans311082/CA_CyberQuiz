<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	function sortObjectbyValue(obj) {
		const ret = {};
		Object.keys(obj)
			.sort((a, b) => obj[b] - obj[a])
			.forEach((s) => (ret[s] = obj[s]));
		return ret;
	}

	interface Props {
		scores: any;
		question_results: Array<{
			username: string;
			answer: string;
			right: boolean;
			time_taken: number;
			score: number;
		}>;
		username: any;
	}

	let { scores = $bindable(), question_results, username }: Props = $props();
	let score_by_username = $derived(Object.fromEntries(question_results.map((result) => [result.username, result.score])));
	$effect(() => {
		const next_scores = { ...scores };
		if (Object.keys(next_scores).length === 0) for (const result of question_results) next_scores[result.username] = 0;
		for (const player of Object.keys(score_by_username)) next_scores[player] = (score_by_username[player] ?? 0) + (next_scores[player] ?? 0);
		scores = next_scores;
	});
	let sorted_scores = $derived(sortObjectbyValue(scores));
</script>

<div>
	<div class="flex justify-center h-screen">
		<div class="m-auto flex flex-col">
			<p class="p-4 bg-black/40 rounded-lg text-2xl">
				+{score_by_username[username] ?? '0'}
			</p>
			<p>Total score: {sorted_scores[username] ?? '0'}</p>
		</div>
	</div>
</div>
