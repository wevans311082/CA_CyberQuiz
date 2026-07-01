<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Button from '$lib/ui/Button.svelte';
	import Card from '$lib/ui/Card.svelte';
	import Input from '$lib/ui/Input.svelte';
	import PageHeader from '$lib/ui/PageHeader.svelte';
	import Spinner from '$lib/ui/Spinner.svelte';
	import { pageTitle } from '$lib/brand';

	type TemplateMeta = {
		id: string;
		name: string;
		summary: string;
		topic: string;
		slide_count: number;
		branch_count: number;
		inject_count: number;
		difficulty: string;
	};

	type WizardContext = {
		company_name: string;
		industry: string;
		location: string;
		exercise_date: string;
		ceo_name: string;
		ciso_name: string;
		employee_count: string;
		primary_system: string;
		regulator: string;
		region: string;
		domain: string;
		data_classification: string;
	};

	type Preview = {
		title: string;
		description: string;
		slide_count: number;
		branch_count: number;
		inject_count: number;
		roles: string[];
		question_titles: string[];
	};

	let step = $state(1);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');
	let templates = $state<TemplateMeta[]>([]);
	let selected_template = $state<string | null>(null);
	let create_all = $state(false);
	let preview = $state<Preview | null>(null);
	let created_ids = $state<string[]>([]);

	let context = $state<WizardContext>({
		company_name: 'Acme Financial Services',
		industry: 'Financial Services',
		location: 'London, United Kingdom',
		exercise_date: new Date().toLocaleDateString('en-GB', {
			day: 'numeric',
			month: 'long',
			year: 'numeric'
		}),
		ceo_name: 'Jane Morgan',
		ciso_name: 'David Chen',
		employee_count: '2,400',
		primary_system: 'customer banking portal',
		regulator: 'ICO',
		region: 'UK',
		domain: 'acmefinancial.example',
		data_classification: 'PCI and personal financial data'
	});

	const selected_meta = $derived(templates.find((t) => t.id === selected_template) ?? null);

	const load_templates = async () => {
		loading = true;
		error = '';
		try {
			const res = await fetch('/api/v1/seed/templates');
			if (!res.ok) throw new Error('Could not load templates');
			const data = await res.json();
			templates = data.templates ?? [];
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load templates';
		} finally {
			loading = false;
		}
	};

	const load_preview = async () => {
		if (!selected_template) return;
		error = '';
		try {
			const res = await fetch('/api/v1/seed/preview', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ template_id: selected_template, context })
			});
			if (!res.ok) {
				const body = await res.json().catch(() => ({}));
				throw new Error(body.detail ?? 'Preview failed');
			}
			preview = await res.json();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Preview failed';
			preview = null;
		}
	};

	const create_exercise = async () => {
		saving = true;
		error = '';
		try {
			const res = await fetch('/api/v1/seed/create', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					template_id: selected_template,
					context,
					create_all
				})
			});
			if (!res.ok) {
				const body = await res.json().catch(() => ({}));
				throw new Error(body.detail ?? 'Create failed');
			}
			const data = await res.json();
			created_ids = data.quiz_ids ?? [];
			step = 4;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Create failed';
		} finally {
			saving = false;
		}
	};

	const next_step = async () => {
		error = '';
		if (step === 1) {
			if (!create_all && !selected_template) {
				error = 'Select a scenario template or choose "Create all".';
				return;
			}
			step = 2;
			return;
		}
		if (step === 2) {
			if (!context.company_name.trim()) {
				error = 'Company name is required.';
				return;
			}
			step = 3;
			if (!create_all) await load_preview();
			return;
		}
		if (step === 3) {
			await create_exercise();
		}
	};

	onMount(load_templates);
</script>

<svelte:head>
	<title>{pageTitle('Exercise Wizard')}</title>
</svelte:head>

<div class="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 py-8">
	<PageHeader
		eyebrow="Scenario Builder"
		title="Tabletop Exercise Wizard"
		description="Generate branched tabletop exercises with your company details, roles, injects, and facilitator notes."
	>
		{#snippet actions()}
			<Button href="/dashboard" variant="ghost">Back to dashboard</Button>
		{/snippet}
	</PageHeader>

	<div class="flex flex-wrap gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
		<span class:rounded-full={step === 1} class:bg-brand-accent={step === 1} class:px-3={step === 1} class:py-1={step === 1} class:text-slate-950={step === 1}>1. Scenario</span>
		<span class:rounded-full={step === 2} class:bg-brand-accent={step === 2} class:px-3={step === 2} class:py-1={step === 2} class:text-slate-950={step === 2}>2. Customise</span>
		<span class:rounded-full={step === 3} class:bg-brand-accent={step === 3} class:px-3={step === 3} class:py-1={step === 3} class:text-slate-950={step === 3}>3. Preview</span>
		<span class:rounded-full={step === 4} class:bg-brand-accent={step === 4} class:px-3={step === 4} class:py-1={step === 4} class:text-slate-950={step === 4}>4. Done</span>
	</div>

	{#if error}
		<div class="rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</div>
	{/if}

	{#if loading}
		<div class="flex justify-center py-16">
			<Spinner size="lg" />
		</div>
	{:else if step === 1}
		<Card variant="glass" padding="lg">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white">Choose a scenario</h2>
			<p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
				Each template includes 14+ slides, branching decisions, facilitator notes, and inject cards.
			</p>

			<label class="mt-6 flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200/70 p-4 dark:border-slate-700">
				<input type="checkbox" bind:checked={create_all} class="h-4 w-4 rounded border-slate-400" />
				<span>
					<span class="font-medium text-slate-900 dark:text-white">Create all four exercises</span>
					<span class="block text-xs text-slate-500">Ransomware, data leak, insider threat, and disaster recovery</span>
				</span>
			</label>

			<div class="mt-4 grid gap-3 md:grid-cols-2">
				{#each templates as template}
					<button
						type="button"
						class="rounded-xl border p-4 text-left transition-colors {selected_template === template.id && !create_all ? 'border-brand-accent bg-brand-accent/10' : 'border-slate-200/70 dark:border-slate-700'} {create_all ? 'opacity-60' : ''}"
						disabled={create_all}
						onclick={() => {
							selected_template = template.id;
							create_all = false;
						}}
					>
						<div class="flex items-start justify-between gap-2">
							<p class="font-semibold text-slate-900 dark:text-white">{template.name}</p>
							<span class="shrink-0 rounded-full bg-slate-200/80 px-2 py-0.5 text-[10px] font-semibold uppercase dark:bg-slate-800">{template.difficulty}</span>
						</div>
						<p class="mt-1 text-xs uppercase tracking-wide text-teal-700 dark:text-cyan-300">{template.topic}</p>
						<p class="mt-2 text-sm text-slate-600 dark:text-slate-400">{template.summary}</p>
						<p class="mt-3 text-xs text-slate-500">
							{template.slide_count} slides · {template.branch_count} branches · {template.inject_count} injects
						</p>
					</button>
				{/each}
			</div>

			<div class="mt-6 flex justify-end">
				<Button onclick={next_step}>Continue</Button>
			</div>
		</Card>
	{:else if step === 2}
		<Card variant="glass" padding="lg">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white">Customise your organisation</h2>
			<p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
				These values are woven into slides, injects, and facilitator notes across the exercise.
			</p>

			<div class="mt-6 grid gap-4 md:grid-cols-2">
				<div>
					<label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500" for="company">Company name</label>
					<Input id="company" bind:value={context.company_name} />
				</div>
				<div>
					<label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500" for="industry">Industry</label>
					<Input id="industry" bind:value={context.industry} />
				</div>
				<div>
					<label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500" for="location">Location</label>
					<Input id="location" bind:value={context.location} />
				</div>
				<div>
					<label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500" for="date">Exercise date</label>
					<Input id="date" bind:value={context.exercise_date} />
				</div>
				<div>
					<label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500" for="ceo">CEO name</label>
					<Input id="ceo" bind:value={context.ceo_name} />
				</div>
				<div>
					<label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500" for="ciso">CISO name</label>
					<Input id="ciso" bind:value={context.ciso_name} />
				</div>
				<div>
					<label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500" for="employees">Employee count</label>
					<Input id="employees" bind:value={context.employee_count} />
				</div>
				<div>
					<label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500" for="system">Primary system</label>
					<Input id="system" bind:value={context.primary_system} />
				</div>
				<div>
					<label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500" for="regulator">Regulator</label>
					<Input id="regulator" bind:value={context.regulator} />
				</div>
				<div>
					<label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500" for="region">Region</label>
					<Input id="region" bind:value={context.region} />
				</div>
				<div>
					<label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500" for="domain">Domain</label>
					<Input id="domain" bind:value={context.domain} />
				</div>
				<div class="md:col-span-2">
					<label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500" for="data">Data classification</label>
					<Input id="data" bind:value={context.data_classification} />
				</div>
			</div>

			<div class="mt-6 flex justify-between">
				<Button variant="ghost" onclick={() => (step = 1)}>Back</Button>
				<Button onclick={next_step}>Preview exercise</Button>
			</div>
		</Card>
	{:else if step === 3}
		<Card variant="glass" padding="lg">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white">Preview & create</h2>
			{#if create_all}
				<p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
					You are about to create <strong>four</strong> customised tabletop exercises for <strong>{context.company_name}</strong>.
				</p>
			{:else if preview}
				<p class="mt-2 text-sm text-slate-600 dark:text-slate-400">{preview.description}</p>
				<div class="mt-4 grid gap-3 sm:grid-cols-3">
					<div class="rounded-xl border border-slate-200/70 bg-slate-50/80 p-3 dark:border-slate-700 dark:bg-slate-900/50">
						<p class="text-xs uppercase text-slate-500">Slides</p>
						<p class="text-2xl font-semibold">{preview.slide_count}</p>
					</div>
					<div class="rounded-xl border border-slate-200/70 bg-slate-50/80 p-3 dark:border-slate-700 dark:bg-slate-900/50">
						<p class="text-xs uppercase text-slate-500">Branches</p>
						<p class="text-2xl font-semibold">{preview.branch_count}</p>
					</div>
					<div class="rounded-xl border border-slate-200/70 bg-slate-50/80 p-3 dark:border-slate-700 dark:bg-slate-900/50">
						<p class="text-xs uppercase text-slate-500">Injects</p>
						<p class="text-2xl font-semibold">{preview.inject_count}</p>
					</div>
				</div>
				<p class="mt-4 text-sm font-medium text-slate-900 dark:text-white">{preview.title}</p>
				<div class="mt-4 max-h-48 overflow-y-auto rounded-xl border border-slate-200/70 p-3 text-sm dark:border-slate-700">
					<ol class="list-decimal space-y-1 pl-5 text-slate-600 dark:text-slate-300">
						{#each preview.question_titles as title, i}
							<li>{title}</li>
						{/each}
					</ol>
				</div>
				<p class="mt-3 text-xs text-slate-500">Roles: {preview.roles.join(', ')}</p>
			{/if}

			<div class="mt-6 flex justify-between">
				<Button variant="ghost" onclick={() => (step = 2)}>Back</Button>
				<Button onclick={create_exercise} disabled={saving}>
					{saving ? 'Creating…' : 'Create exercise'}
				</Button>
			</div>
		</Card>
	{:else if step === 4}
		<Card variant="glass" padding="lg">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white">Exercises created</h2>
			<p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
				{created_ids.length} exercise{created_ids.length === 1 ? '' : 's'} ready. Open in the editor to tweak evidence files, injects, or branch paths.
			</p>
			<div class="mt-4 flex flex-wrap gap-2">
				{#each created_ids as id}
					<Button href="/edit?quiz_id={id}" variant="secondary">Edit exercise</Button>
				{/each}
				<Button href="/dashboard" variant="primary">Go to dashboard</Button>
			</div>
		</Card>
	{/if}
</div>