<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import Button from '$lib/ui/Button.svelte';
	import Card from '$lib/ui/Card.svelte';
	import Input from '$lib/ui/Input.svelte';
	import PageHeader from '$lib/ui/PageHeader.svelte';
	import Spinner from '$lib/ui/Spinner.svelte';
	import { pageTitle } from '$lib/brand';

	navbarVisible.visible = true;

	const { t } = getLocalization();
	let url_input = $state('');
	let file_input: FileList | null = $state(null);
	let kahoot_regex = /^https:\/\/create\.kahoot\.it\/details\/.*\/?([a-zA-Z-\d]{36})\/?$/;

	let url_valid = $derived(kahoot_regex.test(url_input));
	let is_loading = $state(false);

	const submit = async (e: Event) => {
		e.preventDefault();
		if (!url_valid) {
			return;
		}
		is_loading = true;
		const regex_res = kahoot_regex.exec(url_input);
		const res = await fetch(`/api/v1/quiz/import/${regex_res[1]}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (res.status === 200) {
			window.location.href = '/dashboard';
		} else if (res.status === 400) {
			/*			alertModal.set({
				open: true,
				title: 'Import failed',
				body: "This quiz isn't (yet) supported!"
			});*/
			alert("This quiz isn't (yet) supported!");
		} else if (res.status === 403) {
			/*			alertModal.set({
				open: true,
				title: 'Import failed',
				body: 'Unknown error while importing the quiz!'
			});*/
			alert('Quiz is probably private!');
		} else {
			alert(`Kahoot replied with ${res.status}`);
		}
		is_loading = false;
	};

	const file_submit = async (e: Event) => {
		e.preventDefault();
		is_loading = true;
		const formdata = new FormData();
		formdata.append('file', file_input[0]);
		let res;
		if (file_input[0].name.includes('.xlsx')) {
			res = await fetch('/api/v1/quiz/excel-import', {
				method: 'POST',
				body: formdata
			});
		} else if (file_input[0].name.includes('.cqa')) {
			res = await fetch('/api/v1/eximport/', {
				method: 'POST',
				body: formdata
			});
		} else {
			alert('Wrong file type');
			is_loading = false;
			return;
		}

		if (res.status === 200) {
			window.location.href = '/dashboard';
		} else {
			/*			alertModal.set({
				open: true,
				title: 'Import failed',
				body: 'Something went wrong!'
			});*/
			alert('Something went wrong!');
		}
		is_loading = false;
	};

	onMount(() => {
		let url_from_path = page.url.searchParams.get('url');
		if (url_from_path === '') {
			url_from_path = null;
		}
		url_input = url_from_path ?? '';
	});
</script>

<svelte:head>
	<title>{pageTitle('Import')}</title>
</svelte:head>

<div class="mx-auto max-w-5xl px-4 py-8">
	<PageHeader
		eyebrow="Content"
		title={$t('words.import')}
		description="Bring in quizzes from Kahoot or your own CyberAsk export files."
	/>

	<div class="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
		<Card variant="glass" padding="md">
			<form class="flex h-full flex-col gap-4" onsubmit={submit}>
				<h2 class="text-xl font-semibold text-slate-900 dark:text-white">
					{$t('import_page.a_kahoot_quiz')}
				</h2>
				<Input
					id="url"
					type="url"
					bind:value={url_input}
					placeholder="https://create.kahoot.it/details/something"
					ariaLabel={$t('words.url')}
					class={!url_valid && url_input ? 'border-red-400' : url_valid ? 'border-emerald-500' : ''}
				/>
				<p class="text-sm text-slate-500 dark:text-slate-400">
					{$t('import_page.url_should_look_like_this')}
				</p>
				<p class="text-sm text-slate-600 dark:text-slate-300">{$t('import_page.side_import_kahoot')}</p>
				<div class="mt-auto flex justify-end">
					<Button type="submit" variant="primary" disabled={!url_valid || is_loading}>
						{#if is_loading}
							<Spinner size="sm" />
						{:else}
							{$t('words.submit')}
						{/if}
					</Button>
				</div>
			</form>
		</Card>

		<Card variant="glass" padding="md">
			<form class="flex h-full flex-col gap-4" onsubmit={file_submit}>
				<h2 class="text-xl font-semibold text-slate-900 dark:text-white">
					{$t('import_page.classquiz_quiz')}
				</h2>
				<input
					id="file"
					type="file"
					bind:files={file_input}
					accept=".cqa,.xlsx"
					aria-label="Import file"
					class="w-full rounded-xl border border-slate-200/80 bg-white/90 px-4 py-2.5 text-sm text-slate-900 file:mr-3 file:rounded-lg file:border-0 file:bg-brand-accent file:px-3 file:py-1.5 file:text-sm file:font-semibold file:text-slate-950 dark:border-slate-700 dark:bg-slate-900/80 dark:text-slate-100"
				/>
				<p class="text-sm text-slate-500 dark:text-slate-400">{$t('import_page.upload_file_ending')}</p>
				<p class="text-sm text-slate-600 dark:text-slate-300">
					{$t('import_page.this_side_classquiz')}<br />
					{$t('import_page.this_side_classquiz_excel')}
				</p>
				<a
					class="text-sm font-medium text-teal-700 underline hover:text-teal-800 dark:text-cyan-300"
					download
					href="https://blog.web.garage.realux.mawoka.eu/classquiz/ClassQuizImportTemplate.xlsx"
				>
					{$t('import_page.download_template_here')}
				</a>
				<div class="mt-auto flex justify-end">
					<Button type="submit" variant="primary" disabled={!file_input || is_loading}>
						{#if is_loading}
							<Spinner size="sm" />
						{:else}
							{$t('words.submit')}
						{/if}
					</Button>
				</div>
			</form>
		</Card>

		<Card variant="glass" padding="md" class="flex flex-col gap-4">
			<h2 class="text-xl font-semibold text-slate-900 dark:text-white">Tabletop Exercise Template</h2>
			<p class="text-sm leading-7 text-slate-600 dark:text-slate-300">
				Download a pre-formatted tabletop template with roles, inject starter content, file evidence
				placeholder, and a decision slide.
			</p>
			<ul class="list-disc space-y-1 pl-5 text-sm text-slate-600 dark:text-slate-300">
				<li>Scenario type pre-set to tabletop</li>
				<li>Includes role setup and facilitator notes</li>
				<li>Includes SLA checkpoint example</li>
			</ul>
			<div class="mt-auto">
				<Button href="/api/v1/eximport/tabletop-template" variant="secondary" fullWidth={true}>
					Download Tabletop .cqa Template
				</Button>
			</div>
		</Card>
	</div>

	<Card variant="flat" padding="sm" class="mt-6 text-center text-sm text-slate-600 dark:text-slate-300">
		{$t('import_page.need_help')}
		<a
			href="/docs/import-from-kahoot"
			class="ml-2 font-medium text-teal-700 underline hover:text-teal-800 dark:text-cyan-300"
		>
			{$t('import_page.visit_docs')}
		</a>
	</Card>
</div>
