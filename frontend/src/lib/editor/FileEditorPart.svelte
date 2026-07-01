<!--
SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData, FileAttachment } from '$lib/quiz_types';
	import HoverRichTextEditor from '$lib/editor/HoverRichTextEditor.svelte';

	interface Props {
		data: EditorData;
		selected_question: number;
	}

	let { data = $bindable(), selected_question = $bindable() }: Props = $props();

	const get_selected_question = () => {
		if (!Array.isArray(data?.questions)) {
			return null;
		}
		if (selected_question < 0 || selected_question >= data.questions.length) {
			return null;
		}
		return data.questions[selected_question];
	};

	const commit_selected_question = (next_question: (typeof data.questions)[number]) => {
		const next_questions = [...data.questions];
		next_questions[selected_question] = next_question;
		data = {
			...data,
			questions: next_questions
		};
	};

	const ensure_attachments = () => {
		const q = get_selected_question();
		if (!q) {
			return [];
		}
		if (!q.file_attachments) {
			const next_question = {
				...q,
				file_attachments: []
			};
			commit_selected_question(next_question);
			return next_question.file_attachments;
		}
		return q.file_attachments;
	};

	let uploading_index = $state<number | null>(null);
	let upload_error = $state<string | null>(null);

	const upload_file_for_attachment = async (index: number, file: File, question_id?: string) => {
		uploading_index = index;
		upload_error = null;
		try {
			if (!file) {
				throw new Error('No file selected');
			}
			const fd = new FormData();
			fd.append('file', file);
			const res = await fetch('/api/v1/storage/', { method: 'POST', body: fd });
			if (!res.ok) {
				const detail = await res.text();
				throw new Error(detail);
			}
			const item = await res.json();
			
			// Find question by ID to handle case where selected_question changes during upload
			let target_question = get_selected_question();
			if (question_id && question_id !== target_question?.id) {
				target_question = data.questions.find((q) => q.id === question_id) ?? null;
			}
			
			if (!target_question) {
				throw new Error('Question not found');
			}
			
			// Ensure attachments array exists
			const attachments = [...(target_question.file_attachments ?? [])];
			
			// Update the specific attachment
			attachments[index] = {
				...(attachments[index] ?? {}),
				url: `/api/v1/storage/download/${item.id}`,
				filename: file.name,
				mime_type: file.type || 'application/octet-stream',
				id: item.id,
			};

			const updated_question = {
				...target_question,
				file_attachments: attachments
			};

			const target_index = data.questions.findIndex((q) => q.id === target_question.id);
			if (target_index >= 0) {
				const next_questions = [...data.questions];
				next_questions[target_index] = updated_question;
				data = {
					...data,
					questions: next_questions
				};
			} else {
				commit_selected_question(updated_question);
			}
		} catch (err) {
			upload_error = err instanceof Error ? err.message : String(err);
		} finally {
			uploading_index = null;
		}
	};

	const add_attachment = () => {
		const q = get_selected_question();
		if (!q) {
			upload_error = 'No slide is selected.';
			return;
		}
		const attachments = [...(q.file_attachments ?? [])];
		attachments.push({ filename: '', mime_type: 'application/pdf', url: '', description: '' });
		commit_selected_question({
			...q,
			file_attachments: attachments
		});
	};

	const remove_attachment = (index: number) => {
		const q = get_selected_question();
		if (!q) {
			return;
		}
		const attachments = [...(q.file_attachments ?? [])];
		attachments.splice(index, 1);
		commit_selected_question({
			...q,
			file_attachments: attachments
		});
	};

	const update_attachment = (index: number, patch: Partial<FileAttachment>) => {
		const q = get_selected_question();
		if (!q) {
			return;
		}
		const attachments = [...(q.file_attachments ?? [])];
		attachments[index] = {
			...(attachments[index] ?? {}),
			...patch
		};
		commit_selected_question({
			...q,
			file_attachments: attachments
		});
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
			<div class="md:col-span-2 flex items-center gap-2">
				<input
					type="url"
					placeholder="https://... or upload below"
					class="flex-1 rounded border border-gray-300 p-2 text-sm dark:bg-gray-600"
					value={attachment.url}
					oninput={(e) => update_attachment(i, { url: e.currentTarget.value })}
				/>
				<label class="cursor-pointer rounded-md bg-[#4E6E58] px-2 py-1.5 text-xs font-semibold text-white hover:opacity-90 whitespace-nowrap">
					{#if uploading_index === i}⏳{:else}Upload file{/if}
					<input
						type="file"
						class="sr-only"
						disabled={uploading_index !== null}
						onchange={(e) => {
							const file = e.currentTarget.files?.[0];
							if (file) {
								const question_id = data.questions[selected_question]?.id;
								upload_file_for_attachment(i, file, question_id);
							}
							e.currentTarget.value = '';
						}}
					/>
				</label>
			</div>
			<div class="md:col-span-2">
				<HoverRichTextEditor
					bind:text={attachment.description}
					placeholder="Description (optional)"
					minHeightClass="min-h-[5rem]"
					toolbarLabel="Attachment description formatting tools"
				/>
			</div>
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
	{#if upload_error}
		<div class="rounded-md bg-red-50 border border-red-300 px-3 py-2 text-sm text-red-700">{upload_error}</div>
	{/if}
</div>
