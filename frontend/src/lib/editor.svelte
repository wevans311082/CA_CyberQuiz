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
	import { onMount } from 'svelte';
	import ScenarioMap from '$lib/editor/ScenarioMap.svelte';
	import { validateScenario, type ScenarioIssue } from '$lib/scenarioGraph';
	import { confirmAction, notify } from '$lib/notifications.svelte';
	import ScenarioManagementPanel from '$lib/editor/ScenarioManagementPanel.svelte';

	const { t } = getLocalization();

	let schemaInvalid = $state(false);
	let yupErrorMessage = $state('');
	let show_scenario_tools = $state(false);
	let history_open = $state(false);
	let scenario_management_open = $state(false);
	let autosave_status = $state('Autosave ready');
	let history = $state<Array<{ id: string; saved_at: string; label: string; data: EditorData }>>([]);
	let autosave_timer: ReturnType<typeof setInterval> | null = null;

	interface Props {
		data: EditorData;
		quiz_id: string | null;
		submit_button_text?: string;
	}

	let { data = $bindable(), quiz_id = $bindable(), submit_button_text = 'Save' }: Props = $props();
	let selected_question = $state(-1);
	let scenarioIssues = $derived<ScenarioIssue[]>(validateScenario(data));
	let scenarioErrors = $derived(scenarioIssues.filter((issue) => issue.level === 'error'));
	const history_key = $derived(`cyberask:scenario-history:${quiz_id ?? 'new'}`);
	const read_history = () => {
		try {
			const saved = JSON.parse(localStorage.getItem(history_key) ?? '[]');
			if (Array.isArray(saved)) history = saved;
		} catch { history = []; }
	};
	const snapshot = (label = 'Autosave') => {
		if (typeof localStorage === 'undefined') return;
		const entry = { id: crypto.randomUUID(), saved_at: new Date().toISOString(), label, data: JSON.parse(JSON.stringify(data)) as EditorData };
		history = [entry, ...history].slice(0, 20);
		localStorage.setItem(history_key, JSON.stringify(history));
		autosave_status = `Saved ${new Date(entry.saved_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
	};
	const restore_snapshot = async (entry: (typeof history)[number]) => {
		if (!(await confirmAction(`Restore the snapshot from ${new Date(entry.saved_at).toLocaleString()}?`, { title: 'Restore version', confirmLabel: 'Restore' }))) return;
		data = JSON.parse(JSON.stringify(entry.data));
		autosave_status = 'Snapshot restored';
		history_open = false;
	};
	onMount(() => {
		read_history();
		autosave_timer = setInterval(() => snapshot(), 15000);
		return () => { if (autosave_timer) clearInterval(autosave_timer); };
	});
	$effect(() => { JSON.stringify(data); if (autosave_status.startsWith('Saved')) autosave_status = 'Unsaved changes'; });

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
			notify('Unable to initialise the editor. Please try again.', 'error');
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
		if (schemaInvalid || scenarioErrors.length) {
			return;
		}
		snapshot('Published version');
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
			const body = await res.json().catch(() => null);
			notify(body?.detail ? (Array.isArray(body.detail) ? body.detail.map((item) => item.message ?? item).join('\n') : body.detail) : 'Unable to save the exercise.', 'error', 8000);
		}
	};
</script>

<svelte:window onbeforeunload={confirmUnload} />
{#await getEditID()}
	<Spinner />
{:then _}
	<form onsubmit={saveQuiz}>
		<div class="flex h-screen w-screen flex-col overflow-hidden bg-[#f7f9fc] text-slate-900">
			<div class="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-5 shadow-[0_1px_10px_rgba(15,23,42,0.06)]">
				<div class="flex items-center gap-4"><a href="/dashboard" class="text-sm font-semibold text-slate-500 hover:text-teal-700">← Workspace</a><span class="h-5 w-px bg-slate-200"></span><span class="max-w-xs truncate text-sm font-bold text-slate-900">{@html data.title || 'Untitled exercise'}</span><span class="rounded-full bg-teal-50 px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-teal-700">Editor</span></div>
				<div class="flex items-center gap-2"><span class="hidden text-xs text-slate-400 sm:inline">{autosave_status}</span><button type="button" onclick={() => (history_open = !history_open)} class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-bold text-slate-600 hover:border-teal-300 hover:text-teal-700">History · {history.length}</button><button type="button" onclick={() => (scenario_management_open = true)} class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-bold text-slate-600 hover:border-teal-300 hover:text-teal-700">Manage</button><button type="submit" disabled={schemaInvalid || scenarioErrors.length > 0} class="inline-flex items-center gap-2 rounded-lg bg-slate-950 px-4 py-2 text-xs font-bold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"><span>{$t('words.save')}</span><span>↗</span></button></div>
			</div>
			{#if history_open}
				<div class="absolute right-5 top-14 z-50 w-80 rounded-2xl border border-slate-200 bg-white p-3 shadow-xl"><div class="flex items-center justify-between"><p class="text-xs font-bold text-slate-900">Version history</p><button type="button" class="text-xs text-slate-400" onclick={() => (history_open = false)}>Close</button></div><button type="button" class="mt-3 w-full rounded-lg bg-teal-600 px-3 py-2 text-xs font-bold text-white" onclick={() => snapshot('Manual checkpoint')}>Create checkpoint</button><div class="mt-3 max-h-64 space-y-1 overflow-y-auto">{#each history as entry}<button type="button" class="w-full rounded-lg border border-slate-100 px-3 py-2 text-left hover:bg-slate-50" onclick={() => restore_snapshot(entry)}><span class="block text-xs font-semibold text-slate-800">{entry.label}</span><span class="block text-[10px] text-slate-400">{new Date(entry.saved_at).toLocaleString()}</span></button>{:else}<p class="p-3 text-xs text-slate-400">No snapshots yet.</p>{/each}</div></div>
			{/if}
			<div class="grid min-h-0 flex-1 grid-cols-6">
			<div class="min-h-0">
				<Sidebar bind:data bind:selected_question />
			</div>
			<div class="col-span-5 flex flex-col">
				<div class="flex items-center justify-end gap-2 border-b border-slate-200 bg-white px-4 py-2">
					<button type="button" onclick={() => (show_scenario_tools = !show_scenario_tools)} class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-bold text-slate-600 shadow-sm hover:border-teal-300 hover:text-teal-700">{show_scenario_tools ? 'Hide map' : 'Scenario map'}{scenarioIssues.length ? ` · ${scenarioIssues.length}` : ''}</button>
					<span class="text-xs text-slate-400">{schemaInvalid || scenarioErrors.length ? 'Needs attention' : 'Ready to publish'}</span>
				</div>
				{#if show_scenario_tools && data.scenario_type === 'tabletop'}
					<div class="shrink-0 border-b border-slate-200 bg-slate-50 p-4 sm:p-5">
						<ScenarioMap questions={data.questions} {selected_question} issues={scenarioIssues} onselect={(index) => (selected_question = index)} />
						{#if scenarioIssues.length}
							<div class="mt-3 rounded-xl border border-amber-200 bg-amber-50/80 p-3 text-xs text-amber-900"><p class="font-bold">Scenario checks</p><div class="mt-2 grid gap-1 sm:grid-cols-2">{#each scenarioIssues.slice(0, 6) as issue}<button type="button" class="text-left hover:underline" onclick={() => issue.questionIndex !== undefined && (selected_question = issue.questionIndex)}>· {issue.message}</button>{/each}</div></div>
						{/if}
					</div>
				{/if}
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
		<ScenarioManagementPanel bind:open={scenario_management_open} {data} {quiz_id} onclose={() => (scenario_management_open = false)} />
	</form>
{/await}
