<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$lib/ui/Button.svelte';
	import Card from '$lib/ui/Card.svelte';
	import Input from '$lib/ui/Input.svelte';
	import PageHeader from '$lib/ui/PageHeader.svelte';
	import Spinner from '$lib/ui/Spinner.svelte';
	import Icon from '$lib/ui/Icon.svelte';
	import { pageTitle } from '$lib/brand';

	type Template = { id: string; name: string; summary: string; topic: string; slide_count: number; branch_count: number; inject_count: number; difficulty: string };
	let templates = $state<Template[]>([]);
	let search = $state('');
	let loading = $state(true);
	let error = $state('');
	const filtered = $derived(templates.filter((template) => `${template.name} ${template.topic} ${template.summary}`.toLowerCase().includes(search.toLowerCase())));

	onMount(async () => {
		try { const response = await fetch('/api/v1/seed/templates'); if (!response.ok) throw new Error('Unable to load scenarios'); templates = (await response.json()).templates ?? []; }
		catch (e) { error = e instanceof Error ? e.message : 'Unable to load scenarios'; }
		finally { loading = false; }
	});
</script>

<svelte:head><title>{pageTitle('Scenario library')}</title></svelte:head>

	<div class="app-shell min-h-screen px-4 py-8 sm:px-6 lg:px-10">
	<div class="mx-auto max-w-7xl">
		<PageHeader eyebrow="Scenario library" title="Ready-to-run cyber exercises" description="Start with a proven tabletop scenario, personalise it for your organisation, then edit every decision, branch, inject, and facilitator note.">
			{#snippet actions()}<Button href="/seed" variant="primary">Build from template</Button>{/snippet}
		</PageHeader>
		<div class="mt-8 grid gap-4 sm:grid-cols-3"><div class="app-panel p-5"><p class="eyebrow">Templates</p><p class="mt-2 text-3xl font-bold text-slate-950">{templates.length || '—'}</p><p class="mt-1 text-sm text-slate-500">Deep scenario blueprints</p></div><div class="app-panel p-5"><p class="eyebrow">Format</p><p class="mt-2 text-3xl font-bold text-slate-950">Tabletop</p><p class="mt-1 text-sm text-slate-500">Facilitator-led decisions</p></div><div class="app-panel p-5"><p class="eyebrow">Editable</p><p class="mt-2 text-3xl font-bold text-slate-950">100%</p><p class="mt-1 text-sm text-slate-500">Content, paths, and injects</p></div></div>
		<div class="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"><div><h2 class="text-xl font-bold text-slate-950">Choose a threat theme</h2><p class="mt-1 text-sm text-slate-500">Every template contains meaningful branches and consequences.</p></div><div class="w-full sm:max-w-sm"><Input bind:value={search} placeholder="Search scenarios" ariaLabel="Search scenarios" /></div></div>
		{#if loading}<div class="flex justify-center py-20"><Spinner size="lg" /></div>{:else if error}<div class="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>{:else}<div class="mt-6 grid gap-5 md:grid-cols-2 xl:grid-cols-3">{#each filtered as template}
			<Card variant="elevated" padding="none" class="overflow-hidden transition hover:-translate-y-0.5 hover:shadow-xl"><div class="h-2 bg-gradient-to-r from-teal-500 to-cyan-400"></div><div class="p-6"><div class="flex items-start justify-between gap-3"><div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-teal-50 text-xl text-teal-700">⌁</div><span class="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-600">{template.difficulty}</span></div><p class="mt-5 text-xs font-bold uppercase tracking-[0.16em] text-teal-700">{template.topic}</p><h3 class="mt-2 text-xl font-bold text-slate-950">{template.name}</h3><p class="mt-2 min-h-12 text-sm leading-6 text-slate-500">{template.summary}</p><div class="mt-6 grid grid-cols-3 gap-2 border-y border-slate-100 py-4 text-center"><div><p class="text-lg font-bold text-slate-900">{template.slide_count}</p><p class="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Slides</p></div><div><p class="text-lg font-bold text-slate-900">{template.branch_count}</p><p class="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Branches</p></div><div><p class="text-lg font-bold text-slate-900">{template.inject_count}</p><p class="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Injects</p></div></div><Button href="/seed?template={template.id}" variant="secondary" fullWidth={true} class="mt-5">Use this scenario</Button></div></Card>
		{/each}</div>{/if}
	</div>
</div>
