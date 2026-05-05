<!--
SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData } from '$lib/quiz_types';
	import HoverRichTextEditor from '$lib/editor/HoverRichTextEditor.svelte';

	interface Props {
		data: EditorData;
		selected_question: number;
	}

	let { data = $bindable(), selected_question = $bindable() }: Props = $props();

	const sync_information_body = (value: string | undefined) => {
		const q = data.questions[selected_question];
		q.information_body = value || undefined;
		q.answers = value || '';
		data = data;
	};

	$effect(() => {
		const current_value = data.questions[selected_question].information_body;
		if (!current_value && typeof data.questions[selected_question].answers === 'string') {
			data.questions[selected_question].information_body = String(data.questions[selected_question].answers);
		}
	});

	$effect(() => {
		sync_information_body(data.questions[selected_question].information_body);
	});
</script>

<div class="w-full max-w-3xl space-y-3">
	<div>
		<label class="block text-sm font-medium mb-1">Information Body</label>
		<p class="text-xs text-gray-500 mb-2">Use this for facilitator context, briefings, or instructions shown to all viewers.</p>
		<HoverRichTextEditor
			bind:text={data.questions[selected_question].information_body}
			placeholder="Write the slide body..."
			minHeightClass="min-h-[14rem]"
			toolbarLabel="Information body formatting tools"
		/>
	</div>
</div>
