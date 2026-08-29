<script lang="ts">
	import { onMount } from 'svelte';
	import SlideOutPanel from '$lib/ui/SlideOutPanel.svelte';
import { notify } from '$lib/notifications.svelte';

	interface Props { open?: boolean; game_id: string; }
	let { open = $bindable(false), game_id }: Props = $props();
	let notes = $state<{ id: string; body: string; author?: string; created_at: string }[]>([]);
	let facilitators = $state<{ id: string; email: string; permission: string }[]>([]);
	let audit = $state<{ id: string; action: string; created_at: string }[]>([]);
	let note = $state('');
	let email = $state('');
	let permission = $state('facilitator');
	let participant_name = $state('');
	let evidence_title = $state('');
	let busy = $state(false);
	let error = $state('');
	let file_input: HTMLInputElement;
	let retention = $state({ results_days: 365, evidence_days: 180, audit_days: 730 });

	const request = async (url: string, options?: RequestInit) => {
		const response = await fetch(url, options);
		if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? 'Request failed');
		return response.json();
	};
	const refresh = async () => {
		if (!game_id) return;
		try {
			const [next_notes, next_facilitators, next_audit] = await Promise.all([
				request(`/api/v1/exercises/${game_id}/notes`),
				request(`/api/v1/exercises/${game_id}/facilitators`).catch(() => []),
				request(`/api/v1/exercises/${game_id}/audit`).catch(() => [])
			]);
			notes = next_notes; facilitators = next_facilitators; audit = next_audit;
		} catch (err) { error = err instanceof Error ? err.message : 'Unable to load exercise operations'; }
		try { retention = await request('/api/v1/exercises/retention'); } catch { /* facilitator accounts do not manage policy */ }
	};
	const save_retention = async () => {
		try { retention = await request('/api/v1/exercises/retention', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(retention) }); notify('Retention policy saved', 'success'); }
		catch (err) { notify(err instanceof Error ? err.message : 'Only the exercise owner can change retention', 'error'); }
	};
	const add_note = async () => {
		if (!note.trim()) return;
		busy = true;
		try { await request(`/api/v1/exercises/${game_id}/notes`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ body: note }) }); note = ''; await refresh(); notify('Note added to the live workspace', 'success'); }
		catch (err) { notify(err instanceof Error ? err.message : 'Unable to add note', 'error'); }
		finally { busy = false; }
	};
	const add_facilitator = async () => {
		if (!email.trim()) return;
		busy = true;
		try { await request(`/api/v1/exercises/${game_id}/facilitators`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, permission }) }); email = ''; await refresh(); notify('Facilitator access updated', 'success'); }
		catch (err) { notify(err instanceof Error ? err.message : 'Unable to update facilitator access', 'error'); }
		finally { busy = false; }
	};
	const upload_evidence = async (file: File) => {
		busy = true;
		try {
			const form = new FormData(); form.append('file', file);
			const item = await request('/api/v1/storage/', { method: 'POST', body: form });
			await request(`/api/v1/exercises/${game_id}/evidence`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title: evidence_title || file.name, storage_item_id: item.id }) });
			evidence_title = ''; await refresh(); notify('Evidence attached to the exercise', 'success');
		} catch (err) { notify(err instanceof Error ? err.message : 'Evidence upload failed', 'error'); }
		finally { busy = false; }
	};
	const issue_completion = async () => {
		if (!participant_name.trim()) return;
		try { const result = await request(`/api/v1/exercises/${game_id}/completion`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ participant_name }) }); await navigator.clipboard?.writeText(result.completion_code); participant_name = ''; notify(`Completion issued: ${result.completion_code}`, 'success'); }
		catch (err) { notify(err instanceof Error ? err.message : 'Unable to issue completion', 'error'); }
	};
	onMount(() => { refresh(); const timer = window.setInterval(refresh, 4000); return () => window.clearInterval(timer); });
</script>

<SlideOutPanel bind:open title="Exercise operations" description="Coordinate facilitators, capture live evidence, and preserve an auditable exercise record." width="max-w-2xl" onclose={() => (open = false)}>
	<div class="space-y-6">
		{#if error}<div class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>{/if}
		<section>
			<div class="mb-3 flex items-center justify-between"><div><h3 class="text-sm font-bold text-slate-900">Collaborative notes</h3><p class="text-xs text-slate-500">Refreshes live for every facilitator in this exercise.</p></div><span class="rounded-full bg-teal-50 px-2 py-1 text-[10px] font-bold text-teal-700">{notes.length} notes</span></div>
			<div class="rounded-xl border border-slate-200 bg-slate-50 p-3"><textarea bind:value={note} rows="3" placeholder="Capture a decision, observation, or follow-up…" class="w-full resize-none rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-800 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"></textarea><div class="mt-2 flex justify-end"><button type="button" disabled={busy || !note.trim()} onclick={add_note} class="rounded-lg bg-slate-950 px-3 py-2 text-xs font-bold text-white disabled:opacity-40">Add note</button></div></div>
			<div class="mt-3 max-h-48 space-y-2 overflow-y-auto">{#each notes as item}<article class="rounded-lg border border-slate-100 bg-white px-3 py-2"><p class="text-sm text-slate-700">{item.body}</p><p class="mt-1 text-[10px] font-semibold text-slate-400">{item.author ?? 'Facilitator'} · {new Date(item.created_at).toLocaleTimeString()}</p></article>{:else}<p class="text-xs text-slate-400">No live notes yet.</p>{/each}</div>
		</section>
		<section class="border-t border-slate-100 pt-5"><h3 class="text-sm font-bold text-slate-900">Facilitator access</h3><p class="mb-3 text-xs text-slate-500">Invite observers or co-facilitators without sharing the host token.</p><div class="flex gap-2"><input bind:value={email} type="email" placeholder="colleague@company.com" class="min-w-0 flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-500" /><select bind:value={permission} class="rounded-lg border border-slate-200 bg-white px-2 text-xs"><option value="facilitator">Facilitator</option><option value="observer">Observer</option></select><button type="button" disabled={busy || !email.trim()} onclick={add_facilitator} class="rounded-lg bg-teal-600 px-3 py-2 text-xs font-bold text-white disabled:opacity-40">Add</button></div><div class="mt-3 space-y-2">{#each facilitators as person}<div class="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-xs"><span class="font-semibold text-slate-700">{person.email}</span><span class="rounded-full bg-white px-2 py-1 font-bold uppercase tracking-wide text-slate-500">{person.permission}</span></div>{:else}<p class="text-xs text-slate-400">No additional facilitators assigned.</p>{/each}</div></section>
		<section class="grid gap-4 border-t border-slate-100 pt-5 sm:grid-cols-2"><div><h3 class="text-sm font-bold text-slate-900">Live evidence</h3><p class="mb-3 text-xs text-slate-500">Attach screenshots, logs, or decision artefacts.</p><input bind:value={evidence_title} placeholder="Evidence title (optional)" class="mb-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-500" /><label class="flex cursor-pointer items-center justify-center rounded-xl border border-dashed border-teal-300 bg-teal-50 px-3 py-5 text-center text-xs font-bold text-teal-700 hover:bg-teal-100"><input bind:this={file_input} type="file" class="hidden" onchange={(event) => { const file = event.currentTarget.files?.[0]; if (file) upload_evidence(file); event.currentTarget.value = ''; }} />Drop or choose evidence</label></div><div><h3 class="text-sm font-bold text-slate-900">Completion record</h3><p class="mb-3 text-xs text-slate-500">Issue a verifiable completion code after the exercise.</p><div class="flex gap-2"><input bind:value={participant_name} placeholder="Participant name" class="min-w-0 flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-500" /><button type="button" disabled={!participant_name.trim()} onclick={issue_completion} class="rounded-lg bg-slate-950 px-3 py-2 text-xs font-bold text-white disabled:opacity-40">Issue</button></div></div></section>
		<section class="border-t border-slate-100 pt-5"><div class="flex items-center justify-between"><div><h3 class="text-sm font-bold text-slate-900">Audit trail</h3><p class="text-xs text-slate-500">Every governance action is timestamped.</p></div><span class="text-xs font-bold text-slate-500">{audit.length} events</span></div><div class="mt-3 max-h-36 space-y-1 overflow-y-auto">{#each audit as event}<div class="flex justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2 text-xs"><span class="font-semibold text-slate-700">{event.action.replaceAll('_', ' ')}</span><span class="shrink-0 text-slate-400">{new Date(event.created_at).toLocaleTimeString()}</span></div>{:else}<p class="mt-2 text-xs text-slate-400">No audit events yet.</p>{/each}</div></section>
		<section class="border-t border-slate-100 pt-5"><h3 class="text-sm font-bold text-slate-900">Retention policy</h3><p class="mb-3 text-xs text-slate-500">Owner-controlled retention for results, evidence, and audit records.</p><div class="grid grid-cols-3 gap-2">{#each [['results_days', 'Results'], ['evidence_days', 'Evidence'], ['audit_days', 'Audit']] as item}<label class="rounded-lg bg-slate-50 p-2"><span class="text-[10px] font-bold uppercase text-slate-400">{item[1]}</span><input type="number" min="1" max="3650" bind:value={retention[item[0]]} class="mt-1 w-full rounded border border-slate-200 bg-white px-2 py-1 text-sm font-bold text-slate-800" /></label>{/each}</div><button type="button" onclick={save_retention} class="mt-3 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-bold text-slate-700 hover:border-teal-300 hover:text-teal-700">Save retention policy</button></section>
	</div>
</SlideOutPanel>
