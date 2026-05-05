<!--
SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData, FileAttachment } from '$lib/quiz_types';

	interface Props {
		data: EditorData;
		selected_question: number;
	}

	let { data = $bindable(), selected_question = $bindable() }: Props = $props();

	const ensure_attachments = () => {
		const q = data.questions[selected_question];
		if (!q.file_attachments) {
			q.file_attachments = [];
		}
		return q.file_attachments;
	};

	const add_attachment = () => {
		const attachments = ensure_attachments();
		attachments.push({ filename: '', mime_type: 'application/pdf', url: '' });
		data = data;
	};

	const remove_attachment = (index: number) => {
		const attachments = ensure_attachments();
		attachments.splice(index, 1);
		data = data;
	};

	const update_attachment = (index: number, patch: Partial<FileAttachment>) => {
		const attachments = ensure_attachments();
		attachments[index] = {
			...attachments[index],
			...patch
		};
		data = data;
	};
</script>

<div class="w-full max-w-3xl space-y-3">
	<div class="flex items-center justify-between">
		<div>
			<h3 class="text-base font-semibold">Evidence Files</h3>
			<p class="text-xs text-gray-500">Attach files players can preview or download during this slide.</p>
		</div>
		<button
			type="button"
			class="rounded-md bg-[#B07156] px-3 py-1 text-sm text-white hover:opacity-90"
			onclick={add_attachment}
		>
			Add file
		</button>
	</div>

	{#if !data.questions[selected_question].file_attachments?.length}
		<div class="rounded-lg border border-dashed border-gray-400 p-4 text-sm text-gray-500">
			No files attached yet.
		</div>
	{/if}

	{#each data.questions[selected_question].file_attachments ?? [] as attachment, i}
		<div class="rounded-lg border border-gray-400 p-3 grid grid-cols-1 md:grid-cols-2 gap-2">
			<input
				type="text"
				placeholder="Filename"
				class="rounded border border-gray-300 p-2 text-sm dark:bg-gray-600"
				value={attachment.filename}
				oninput={(e) => update_attachment(i, { filename: e.currentTarget.value })}
			/>
			<input
				type="text"
				placeholder="MIME type"
				class="rounded border border-gray-300 p-2 text-sm dark:bg-gray-600"
				value={attachment.mime_type}
				oninput={(e) => update_attachment(i, { mime_type: e.currentTarget.value })}
			/>
			<input
				type="url"
				placeholder="https://..."
				class="rounded border border-gray-300 p-2 text-sm dark:bg-gray-600 md:col-span-2"
				value={attachment.url}
				oninput={(e) => update_attachment(i, { url: e.currentTarget.value })}
			/>
			<input
				type="text"
				placeholder="Description (optional)"
				class="rounded border border-gray-300 p-2 text-sm dark:bg-gray-600 md:col-span-2"
				value={attachment.description ?? ''}
				oninput={(e) => update_attachment(i, { description: e.currentTarget.value || undefined })}
			/>
			<div class="md:col-span-2 flex justify-end">
				<button
					type="button"
					class="rounded-md bg-red-500 px-3 py-1 text-sm text-white hover:opacity-90"
					onclick={() => remove_attachment(i)}
				>
					Remove
				</button>
			</div>
		</div>
	{/each}
</div>
