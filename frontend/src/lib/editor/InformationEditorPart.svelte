<!--
SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData } from '$lib/quiz_types';

	interface Props {
		data: EditorData;
		selected_question: number;
	}

	let { data = $bindable(), selected_question = $bindable() }: Props = $props();

	const sync_information_body = (value: string) => {
		const q = data.questions[selected_question];
		q.information_body = value || undefined;
		q.answers = value;
		data = data;
	};
</script>

<div class="w-full max-w-3xl space-y-3">
	<div>
		<label class="block text-sm font-medium mb-1">Information Body</label>
		<p class="text-xs text-gray-500 mb-2">Use this for facilitator context, briefings, or instructions shown to all viewers.</p>
		<textarea
			class="w-full min-h-[220px] rounded-lg border border-gray-400 p-3 text-sm dark:bg-gray-600 outline-hidden"
			placeholder="Write the slide body..."
			value={data.questions[selected_question].information_body ?? String(data.questions[selected_question].answers ?? '')}
			oninput={(e) => sync_information_body(e.currentTarget.value)}
		></textarea>
	</div>
</div>
