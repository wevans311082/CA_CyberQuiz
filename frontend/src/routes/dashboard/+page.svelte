<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import DownloadQuiz from '$lib/components/DownloadQuiz.svelte';
	import type { QuizData } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import Footer from '$lib/footer.svelte';
	import { signedIn } from '$lib/stores';
	import { navbarVisible } from '$lib/stores.svelte';
	import CommandpaletteNotice from '$lib/components/popover/commandpalettenotice.svelte';
	import Fuse from 'fuse.js';
	import Button from '$lib/ui/Button.svelte';
	import Card from '$lib/ui/Card.svelte';
	import Input from '$lib/ui/Input.svelte';
	import PageHeader from '$lib/ui/PageHeader.svelte';
	import Spinner from '$lib/ui/Spinner.svelte';
	import { pageTitle } from '$lib/brand';
	import type { PageData } from './$types';
	import StartGamePopup from '$lib/dashboard/start_game.svelte';
	import Analytics from './Analytics.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { onMount } from 'svelte';

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();
	let search_term = $state('');
	let start_game = $state(null);
	let download_id: string | null = $state(null);
	signedIn.set(true);
	navbarVisible.visible = true;
	const { t } = getLocalization();

	let items_to_show = $state([]);
	let all_items: Array<any> = $state();
	let fuse;

	const getData = async (): Promise<{ items: Array<QuizData>; fuse: Fuse<any> }> => {
		const items: any[] = [];
		for (const q of data.quizzes) items.push({ ...q, type: 'quiz' });
		for (const q of data.quiztivities) items.push({ ...q, type: 'quiztivity' });
		const f = new Fuse(items, {
			keys: ['title', 'description', 'questions.title'],
			findAllMatches: true
		});
		return { items, fuse: f };
	};

	const search = () => {
		if (search_term === '') {
			items_to_show = all_items;
			return;
		}
		const res = fuse.search(search_term);
		items_to_show = res.map((r) => r.item);
	};

	const rebuild_search_index = () => {
		fuse = new Fuse(all_items, {
			keys: ['title', 'description', 'questions.title'],
			findAllMatches: true
		});
		search();
	};

	onMount(async () => {
		const { items, fuse: f } = await getData();
		all_items = items;
		items_to_show = items;
		fuse = f;
		search();
	});

	const deleteQuiz = async (to_delete: string, type: 'quiz' | 'quiztivity') => {
		if (!confirm('Do you really want to delete this quiz?')) {
			return;
		}
		let res: Response;
		if (type === 'quiz') {
			res = await fetch(`/api/v1/quiz/delete/${to_delete}`, { method: 'DELETE' });
		} else {
			res = await fetch(`/api/v1/quiztivity/${to_delete}`, { method: 'DELETE' });
		}
		if (!res.ok) {
			alert('Delete failed. Please try again.');
			return;
		}
		all_items = all_items.filter((item) => item.id !== to_delete);
		rebuild_search_index();
	};

	let analytics_quiz_selected: undefined | QuizData = $state(undefined);
</script>

<svelte:head>
	<title>{pageTitle('Dashboard')}</title>
</svelte:head>

<Analytics bind:quiz={analytics_quiz_selected} />
<CommandpaletteNotice />

<div class="min-h-screen flex flex-col text-slate-900 dark:text-slate-100">
	{#if !all_items}
		<div class="flex flex-1 items-center justify-center py-24">
			<Spinner size="lg" />
		</div>
	{:else}
		<div class="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-8">
			<PageHeader
				eyebrow="Facilitator Hub"
				title="Dashboard"
				description="Create, host, and manage live quiz sessions and tabletop exercises."
			>
				{#snippet actions()}
					<Button href="/create" variant="primary">{$t('dashboard.create_quiz')}</Button>
					<Button href="/seed" variant="secondary">Exercise wizard</Button>
					<Button href="/import" variant="secondary">{$t('words.import')}</Button>
				{/snippet}
			</PageHeader>

			<div class="flex flex-wrap gap-2">
				<Button href="/results" variant="ghost" size="sm">{$t('words.results')}</Button>
				<Button href="/edit/files" variant="ghost" size="sm">{$t('words.files_library')}</Button>
				<Button href="/account/settings" variant="ghost" size="sm">{$t('words.settings')}</Button>
			</div>

			{#if all_items.length !== 0}
				<div class="flex max-w-md items-center gap-2">
					<div class="relative flex-1">
						<Input
							bind:value={search_term}
							placeholder={$t('dashboard.search_for_own_quizzes')}
							ariaLabel={$t('dashboard.search_for_own_quizzes')}
							oninput={search}
						/>
					</div>
					{#if search_term}
						<Button
							variant="ghost"
							size="sm"
							ariaLabel="Clear search"
							onclick={() => {
								search_term = '';
								items_to_show = all_items;
							}}
						>
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						</Button>
					{/if}
				</div>

				<div class="flex flex-col gap-4">
					{#each items_to_show as quiz (quiz.id)}
						<Card variant="glass" padding="sm" class="transition-colors hover:border-brand-accent/30">
							<div class="grid gap-4 lg:grid-cols-[120px_1fr_auto] lg:items-center">
								<div class="hidden lg:block">
									<div class="relative flex h-24 w-full items-center justify-center overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800/80">
										{#if quiz.cover_image}
											<MediaComponent
												src={quiz.cover_image}
												css_classes="max-h-full max-w-full rounded-xl object-cover"
											/>
										{:else}
											<span class="text-xs uppercase tracking-[0.2em] text-slate-400">
												{quiz.type === 'quiztivity' ? 'Activity' : 'Quiz'}
											</span>
										{/if}
									</div>
								</div>

								<div class="min-w-0 px-1">
									<div class="flex items-center gap-2">
										<span
											class="rounded-full border border-slate-200 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500 dark:border-slate-600 dark:text-slate-400"
										>
											{quiz.type === 'quiztivity' ? 'Quiztivity' : 'Quiz'}
										</span>
										{#if quiz.scenario_type === 'tabletop'}
											<span
												class="rounded-full border border-teal-200 bg-teal-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-teal-700 dark:border-teal-800 dark:bg-teal-950/50 dark:text-teal-300"
											>
												Tabletop
											</span>
										{/if}
									</div>
									<p class="mt-2 truncate text-lg font-semibold text-slate-900 dark:text-white">
										{@html quiz.title}
									</p>
									<p class="mt-1 line-clamp-2 text-sm text-slate-500 dark:text-slate-400">
										{@html quiz.description ?? ''}
									</p>
								</div>

								<div
									class="grid gap-2 self-end"
									class:grid-cols-3={quiz.type === 'quiz'}
									class:grid-cols-2={quiz.type === 'quiztivity'}
								>
									<Button
										variant="icon"
										disabled={!quiz.public}
										href="/view/{quiz.id}"
										ariaLabel="View quiz"
									>
										<svg class="h-5 w-5" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
											<path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" stroke-linecap="round" stroke-linejoin="round" />
											<path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" stroke-linecap="round" stroke-linejoin="round" />
										</svg>
									</Button>
									<Button variant="icon" ariaLabel="Analytics" onclick={() => (analytics_quiz_selected = quiz)}>
										<svg class="h-5 w-5" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
											<path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" stroke-linecap="round" stroke-linejoin="round" />
										</svg>
									</Button>
									<Button
										variant="icon"
										ariaLabel="Edit"
										href={quiz.type === 'quiz' ? `/edit?quiz_id=${quiz.id}` : `/quiztivity/edit?id=${quiz.id}`}
									>
										<svg class="h-5 w-5" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
											<path d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" stroke-linecap="round" stroke-linejoin="round" />
										</svg>
									</Button>
									{#if quiz.type === 'quiz'}
										<Button variant="icon" ariaLabel="Start game" onclick={() => (start_game = quiz.id)}>
											<svg class="h-5 w-5" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
												<path d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" stroke-linecap="round" stroke-linejoin="round" />
												<path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" />
											</svg>
										</Button>
									{:else}
										<Button variant="icon" ariaLabel="Play activity" href="/quiztivity/play?id={quiz.id}">
											<svg class="h-5 w-5" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
												<path d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" stroke-linecap="round" stroke-linejoin="round" />
												<path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" />
											</svg>
										</Button>
									{/if}
									<Button variant="icon" ariaLabel="Delete" onclick={() => deleteQuiz(quiz.id, quiz.type)}>
										<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
										</svg>
									</Button>
									<Button
										variant="icon"
										ariaLabel="Download"
										disabled={quiz.type !== 'quiz'}
										onclick={() => (download_id = quiz.id)}
									>
										<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
										</svg>
									</Button>
								</div>
							</div>
						</Card>
					{/each}
				</div>
			{:else}
				<Card variant="glass" padding="lg" class="text-center">
					<p class="text-lg text-slate-500 dark:text-slate-400">{$t('overview_page.no_quizzes')}</p>
					<div class="mt-6 flex justify-center gap-3">
						<Button href="/create" variant="primary">{$t('dashboard.create_quiz')}</Button>
						<Button href="/import" variant="secondary">{$t('words.import')}</Button>
					</div>
				</Card>
			{/if}
		</div>
	{/if}
</div>

<Footer />
{#if start_game !== null}
	<StartGamePopup bind:quiz_id={start_game} />
{/if}
<DownloadQuiz bind:quiz_id={download_id} />