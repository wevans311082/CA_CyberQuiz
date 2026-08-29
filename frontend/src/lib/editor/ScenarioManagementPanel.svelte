<script lang="ts">
	import Button from '$lib/ui/Button.svelte';
	import SlideOutPanel from '$lib/ui/SlideOutPanel.svelte';
	import Icon from '$lib/ui/Icon.svelte';
	import { notify } from '$lib/notifications.svelte';
	import type { EditorData } from '$lib/quiz_types';

	interface Props { quiz_id: string | null; data: EditorData; open?: boolean; onclose?: () => void; }
	let { quiz_id, data, open = $bindable(), onclose }: Props = $props();
	let loading = $state(false);
	let versions = $state<any[]>([]);
	let selected_version = $state<any>(null);
	let compare_version = $state<any>(null);
	let compare_result = $state<{ changed: string[]; summary: string } | null>(null);
	let tags = $state((data.tags ?? []).join(', '));
	let difficulty = $state('');
	let duration_minutes = $state<number | undefined>(undefined);
	let frameworks = $state('');

	const load = async () => {
		if (!quiz_id) return;
		loading = true;
		try {
			const [meta_res, version_res] = await Promise.all([
				fetch(`/api/v1/scenarios/${quiz_id}/metadata`),
				fetch(`/api/v1/scenarios/${quiz_id}/versions`)
			]);
			if (meta_res.ok) {
				const meta = await meta_res.json();
				tags = (meta.tags ?? []).join(', ');
				difficulty = meta.difficulty ?? '';
				duration_minutes = meta.duration_minutes;
				frameworks = Object.entries(meta.framework_mappings ?? {}).map(([key, values]) => `${key}: ${(values as string[]).join(', ')}`).join('\n');
			}
			if (version_res.ok) versions = await version_res.json();
		} catch { notify('Scenario management data could not be loaded.', 'error'); }
		finally { loading = false; }
	};

	$effect(() => { if (open) load(); });
	const metadata_payload = () => ({
		tags: tags.split(',').map((tag) => tag.trim()).filter(Boolean),
		difficulty: difficulty || null,
		duration_minutes: duration_minutes || null,
		framework_mappings: Object.fromEntries(frameworks.split('\n').map((line) => line.split(':')).filter(([key, value]) => key?.trim() && value?.trim()).map(([key, value]) => [key.trim(), value.split(',').map((item) => item.trim()).filter(Boolean)])),
		reusable_roles: data.roles?.map((role) => ({ name: role, description: data.role_descriptions?.[role] ?? '' })) ?? [],
		reusable_injects: data.injects ?? [],
		evidence_packs: data.questions?.filter((question) => question.file_attachments?.length).map((question) => ({ question_id: question.id, attachments: question.file_attachments })) ?? []
	});

	const save_metadata = async () => {
		if (!quiz_id) return;
		const response = await fetch(`/api/v1/scenarios/${quiz_id}/metadata`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(metadata_payload()) });
		if (response.ok) notify('Scenario metadata saved.', 'success'); else notify('Metadata could not be saved.', 'error');
	};
	const create_draft = async () => {
		if (!quiz_id) return;
		const response = await fetch(`/api/v1/scenarios/${quiz_id}/versions`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ label: 'Editor checkpoint', change_summary: 'Saved from the scenario editor', content: { ...data, ...metadata_payload() } }) });
		if (response.ok) { notify('Draft version saved.', 'success'); await load(); } else notify('Draft could not be saved.', 'error');
	};
	const version_action = async (version: any, action: 'publish' | 'rollback') => {
		if (!quiz_id) return;
		const response = await fetch(`/api/v1/scenarios/${quiz_id}/versions/${version.id}/${action}`, { method: 'POST' });
		if (response.ok) { notify(action === 'publish' ? 'Version published.' : 'Version restored to the scenario.', 'success'); await load(); } else notify(`Version could not be ${action}ed.`, 'error');
	};
	const compare_versions = async () => {
		if (!quiz_id || !selected_version || !compare_version) return;
		const response = await fetch(`/api/v1/scenarios/${quiz_id}/versions/compare/${selected_version.id}/${compare_version.id}`);
		if (!response.ok) { notify('Versions could not be compared.', 'error'); return; }
		const result = await response.json();
		compare_result = { changed: result.changed ?? [], summary: `${result.changed?.length ?? 0} content area${result.changed?.length === 1 ? '' : 's'} changed between v${selected_version.version_number} and v${compare_version.version_number}.` };
	};
	const duplicate_or_fork = async (action: 'duplicate' | 'fork') => {
		if (!quiz_id) return;
		const response = await fetch(`/api/v1/scenarios/${quiz_id}/${action}`, { method: 'POST' });
		if (response.ok) { const result = await response.json(); notify(`Scenario ${action}ed. Opening the new copy.`, 'success'); window.location.href = `/edit/${result.id}`; } else notify(`Scenario could not be ${action}ed.`, 'error');
	};
</script>

<SlideOutPanel bind:open title="Scenario management" description="Control metadata, versions, reuse, and publishing for this exercise." onclose={onclose} width="max-w-2xl">
	{#if !quiz_id}
		<div class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-600">Save this new exercise first to enable server-backed scenario management.</div>
	{:else if loading}
		<div class="flex items-center gap-3 rounded-2xl bg-slate-50 p-5 text-sm text-slate-600"><span class="h-2.5 w-2.5 animate-pulse rounded-full bg-teal-500"></span>Loading scenario controls…</div>
	{:else}
		<div class="space-y-7">
			<section><p class="text-xs font-bold uppercase tracking-wider text-slate-400">Content profile</p><div class="mt-3 grid gap-3 sm:grid-cols-2"><label class="text-sm font-semibold text-slate-700">Difficulty<input bind:value={difficulty} class="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-500" placeholder="Intermediate" /></label><label class="text-sm font-semibold text-slate-700">Duration (minutes)<input type="number" bind:value={duration_minutes} class="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-500" placeholder="90" /></label></div><label class="mt-3 block text-sm font-semibold text-slate-700">Tags<input bind:value={tags} class="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-500" placeholder="ransomware, board, UK" /></label><label class="mt-3 block text-sm font-semibold text-slate-700">Framework mappings<span class="ml-1 font-normal text-slate-400">one framework per line, e.g. NIST CSF: ID.RA, RS.MI</span><textarea bind:value={frameworks} rows="3" class="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-500"></textarea></label><div class="mt-3 flex flex-wrap gap-2"><Button size="sm" onclick={save_metadata}><Icon name="check" size={14} />Save profile</Button><Button size="sm" variant="secondary" onclick={() => duplicate_or_fork('duplicate')}><Icon name="file" size={14} />Duplicate</Button><Button size="sm" variant="secondary" onclick={() => duplicate_or_fork('fork')}><Icon name="arrow-right" size={14} />Fork</Button></div></section>
			<section class="border-t border-slate-100 pt-6"><div class="flex items-center justify-between"><div><p class="text-xs font-bold uppercase tracking-wider text-slate-400">Version history</p><p class="mt-1 text-sm text-slate-500">Durable checkpoints are available across devices.</p></div><Button size="sm" variant="secondary" onclick={create_draft}><Icon name="plus" size={14} />Save draft</Button></div><div class="mt-3 space-y-2">{#each versions as version}<button type="button" class={`w-full rounded-xl border p-3 text-left transition ${selected_version?.id === version.id ? 'border-teal-400 bg-teal-50' : 'border-slate-200 hover:border-teal-300'}`} onclick={() => (selected_version = version)}><div class="flex items-center justify-between gap-3"><span class="text-sm font-bold text-slate-800">v{version.version_number} · {version.label}</span><span class="rounded-full px-2 py-1 text-[10px] font-bold uppercase ${version.status === 'published' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}">{version.status}</span></div><p class="mt-1 text-xs text-slate-500">{version.change_summary ?? 'No change summary'} · {new Date(version.created_at).toLocaleString()}</p></button>{:else}<p class="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">No server versions yet. Save a draft checkpoint to start the history.</p>{/each}</div>{#if selected_version}<div class="mt-3 space-y-3"><div class="grid gap-2 sm:grid-cols-2"><label class="text-xs font-semibold text-slate-600">Compare with<select bind:value={compare_version} class="mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"><option value={null}>Choose a version…</option>{#each versions.filter((version) => version.id !== selected_version.id) as version}<option value={version}>{`v${version.version_number} · ${version.label}`}</option>{/each}</select></label></div><div class="flex flex-wrap gap-2"><Button size="sm" variant="secondary" onclick={compare_versions} disabled={!compare_version}><Icon name="chart" size={14} />Compare</Button><Button size="sm" variant="secondary" onclick={() => version_action(selected_version, 'publish')}><Icon name="check" size={14} />Publish</Button><Button size="sm" variant="danger" onclick={() => version_action(selected_version, 'rollback')}><Icon name="arrow-down" size={14} />Rollback</Button></div>{#if compare_result}<div class="rounded-xl border border-teal-200 bg-teal-50 p-3 text-sm text-teal-900"><p class="font-semibold">{compare_result.summary}</p><p class="mt-1 text-xs">Changed areas: {compare_result.changed.join(', ') || 'None'}</p></div>{/if}</div>{/if}</section>
		</div>
	{/if}
</SlideOutPanel>
