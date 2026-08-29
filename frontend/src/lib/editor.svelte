<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { dataSchema } from '$lib/yupSchemas';
	import type { EditorData, Question } from './quiz_types';
	import Sidebar from '$lib/editor/sidebar.svelte';
	import SettingsCard from '$lib/editor/settings-card.svelte';
	import QuizCard from '$lib/editor/card.svelte';
	import Spinner from './Spinner.svelte';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	let schemaInvalid = $state(false);
	let yupErrorMessage = $state('');

	interface Props {
		data: EditorData;
		quiz_id: string | null;
	}

	let { data = $bindable(), quiz_id }: Props = $props();
	let selected_question = $state(-1);

	const validateInput = async (data: EditorData) => {
		try {
			await dataSchema.validate(data, { abortEarly: false });
			schemaInvalid = false;
			yupErrorMessage = '';
		} catch (err) {
			schemaInvalid = true;
			yupErrorMessage = err.errors ? err.errors[0] : '';
		}
	};
	$effect(() => {
		validateInput(data);
	});
	let edit_id: string = $state();
	let confirm_to_leave = true;

	const getEditID = async () => {
		let res: Response;
		if (quiz_id === null) {
			res = await fetch(`/api/v1/editor/start?edit=false`, {
				method: 'POST'
			});
		} else {
			res = await fetch(`/api/v1/editor/start?edit=true&quiz_id=${quiz_id}`, {
				method: 'POST'
			});
		}
		if (res.status === 200) {
			const json = await res.json();
			edit_id = json.token;
		} else {
			alert('Error!');
		}
	};

	const confirmUnload = (event: BeforeUnloadEvent) => {
		if (!confirm_to_leave) {
			return;
		}
		event.preventDefault();
		event.returnValue = 'Are you sure you want to leave?';
		localStorage.setItem('edit_game', JSON.stringify(data));
		return 'unload';
	};
	const saveQuiz = async (e: Event) => {
		e.preventDefault();
		if (schemaInvalid) {
			return;
		}
		const res = await fetch(`/api/v1/editor/finish?edit_id=${edit_id}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(data)
		});
		if (res.ok) {
			confirm_to_leave = false;
			console.log(confirm_to_leave);
			window.location.href = '/dashboard';
		} else {
			alert('Error');
		}
	};
</script>

<svelte:window onbeforeunload={confirmUnload} />
{#await getEditID()}
	<Spinner />
{:then _}
	<form onsubmit={saveQuiz}>
		<div class="flex h-screen w-screen flex-col overflow-hidden bg-[#f7f9fc] text-slate-900">
			<div class="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-5 shadow-sm">
				<div class="flex items-center gap-4"><a href="/dashboard" class="text-sm font-semibold text-slate-500 hover:text-teal-700">← Workspace</a><span class="h-5 w-px bg-slate-200"></span><span class="max-w-xs truncate text-sm font-bold text-slate-900">{@html data.title || 'Untitled exercise'}</span><span class="rounded-full bg-teal-50 px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-teal-700">Editor</span></div>
				<div class="flex items-center gap-3"><span class="hidden text-xs text-slate-400 sm:inline">{schemaInvalid ? 'Needs attention' : 'All changes saved locally'}</span><button type="submit" disabled={schemaInvalid} class="inline-flex items-center gap-2 rounded-lg bg-slate-950 px-4 py-2 text-xs font-bold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"><span>{$t('words.save')}</span><span>↗</span></button></div>
			</div>
			<div class="grid min-h-0 flex-1 grid-cols-6">
			<div class="min-h-0">
				<Sidebar bind:data bind:selected_question />
			</div>
			<div class="col-span-5 flex flex-col">
				<div
					class="hidden"
				>
					{#if schemaInvalid}
						<p class="text-center w-full text-red-600 h-full mt-0.5 font-semibold">
							{yupErrorMessage}
						</p>
					{:else}
						<p class="text-center w-full text-black h-full align-bottom mt-0.5">
							{@html data.title}
						</p>
					{/if}
				</div>
				<div class="min-h-0 flex-1 overflow-y-auto p-4 sm:p-6">
					{#if selected_question === -1}
						<SettingsCard bind:data bind:edit_id />
					{:else}
						<QuizCard bind:data bind:selected_question bind:edit_id />
					{/if}
				</div>
			</div>
			</div>
		</div>
	</form>
{/await}
