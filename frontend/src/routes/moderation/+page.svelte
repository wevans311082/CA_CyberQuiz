<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import Button from '$lib/ui/Button.svelte';
	import Card from '$lib/ui/Card.svelte';
	import PageHeader from '$lib/ui/PageHeader.svelte';
	import { pageTitle } from '$lib/brand';

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();

	const pageNum = $derived(parseInt(data.page, 10) || 1);
	const hasPrev = $derived(pageNum > 1);
	const hasNext = $derived(data.quizzes.length === 20);
</script>

<svelte:head>
	<title>{pageTitle('Moderation')}</title>
</svelte:head>

<div class="mx-auto max-w-6xl px-4 py-8">
	<PageHeader
		eyebrow="Admin"
		title="Moderation queue"
		description="Review community quizzes before they appear in public search. Open a quiz to inspect questions and approve or reject."
	/>

	{#if data.quizzes.length === 0}
		<Card variant="glass" padding="lg" class="mt-8 text-center">
			<p class="text-lg text-slate-500 dark:text-slate-400">No quizzes awaiting moderation.</p>
		</Card>
	{:else}
		<div class="mt-8 flex flex-col gap-4">
			{#each data.quizzes as quiz}
				<Card variant="glass" padding="md">
					<div class="grid gap-4 lg:grid-cols-[140px_1fr_auto] lg:items-center">
						<div class="relative aspect-[4/3] overflow-hidden rounded-xl border border-slate-200/70 bg-slate-100 dark:border-slate-700 dark:bg-slate-900">
							{#if quiz.cover_image}
								<img
									src="/api/v1/storage/download/{quiz.cover_image}"
									alt=""
									loading="lazy"
									class="h-full w-full object-cover"
								/>
							{:else}
								<div class="flex h-full items-center justify-center text-xs text-slate-400">No cover</div>
							{/if}
						</div>

						<div class="min-w-0">
							<h2 class="truncate text-xl font-semibold text-slate-900 dark:text-white">
								{@html quiz.title}
							</h2>
							{#if quiz.description}
								<p class="mt-1 line-clamp-2 text-sm text-slate-500 dark:text-slate-400">
									{@html quiz.description}
								</p>
							{/if}
							<p class="mt-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
								{quiz.questions.length} questions
							</p>
						</div>

						<div class="flex lg:justify-end">
							<Button href="/view/{quiz.id}?mod=true&autoExpand=true&autoReturn=true" size="sm">
								Review quiz
							</Button>
						</div>
					</div>
				</Card>
			{/each}
		</div>
	{/if}

	<div class="mt-8 flex items-center justify-center gap-4">
		<Button href="/moderation?page={pageNum - 1}" variant="secondary" size="sm" disabled={!hasPrev}>
			Previous
		</Button>
		<span class="text-sm text-slate-500 dark:text-slate-400">Page {pageNum}</span>
		<Button href="/moderation?page={pageNum + 1}" variant="secondary" size="sm" disabled={!hasNext}>
			Next
		</Button>
	</div>
</div>