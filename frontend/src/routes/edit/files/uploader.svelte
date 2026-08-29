<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import Spinner from '$lib/Spinner.svelte';
	import type { EditorData } from '$lib/quiz_types';

	let uppyOpen = $state(false);
	let selected_question = $state<number | undefined>(undefined);
	let data = $state<EditorData>({ public: false, title: '', description: '', questions: [], cover_image: undefined });

	$effect(() => {
		if (data.cover_image) {
			window.location.reload();
		}
	});
</script>

{#await import('$lib/editor/uploader.svelte')}
	<Spinner my_20={false} />
{:then c}
	<c.default
		bind:modalOpen={uppyOpen}
		{data}
		{selected_question}
		video_upload={true}
		library_enabled={false}
	/>
{/await}
