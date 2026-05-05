<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	export let quiz: QuizData | undefined = undefined;

	const on_parent_click = (e: Event) => {
		if (e.target !== e.currentTarget) {
			return;
		}
		quiz = undefined;
	};
	const close_start_game_if_esc_is_pressed = (key: KeyboardEvent) => {
		if (key.code === 'Escape') {
			quiz = undefined;
		}
	};
	onMount(() => {
		document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
	});
</script>

{#if quiz}
	<div
		class="fixed inset-0 flex bg-black/70 z-50 overflow-y-auto"
		onclick={on_parent_click}
		transition:fade={{ duration: 100 }}
	>
		<div
			class="m-auto rounded-[1.75rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_80px_rgba(15,23,42,0.6)] flex p-8 flex-col lg:w-2/3 w-11/12 max-h-[90vh] overflow-y-auto text-white"
		>
			<h1 class="text-center text-3xl font-semibold text-white">{$t('words.analytics')}</h1>
			<div class="border-t border-white/8 mt-6"></div>

			<section class="flex flex-col gap-4 mt-6">
				<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80 text-center">{$t('words.rating')}</p>
				<div class="grid grid-cols-2 gap-4">
					<div class="rounded-2xl border border-white/10 bg-white/5 p-4 text-center">
						<p class="text-xs uppercase tracking-[0.25em] text-slate-400/70 mb-1">{$t('words.like', { count: 2 })}</p>
						<p class="text-2xl font-semibold text-white">{quiz.likes}</p>
					</div>
					<div class="rounded-2xl border border-white/10 bg-white/5 p-4 text-center">
						<p class="text-xs uppercase tracking-[0.25em] text-slate-400/70 mb-1">{$t('words.dislike', { count: 2 })}</p>
						<p class="text-2xl font-semibold text-white">{quiz.dislikes}</p>
					</div>
				</div>
			</section>

			<section class="flex flex-col gap-4 mt-6">
				<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80 text-center">{$t('dashboard.views_n_plays')}</p>
				<div class="grid grid-cols-2 gap-4">
					<div class="rounded-2xl border border-white/10 bg-white/5 p-4 text-center">
						<p class="text-xs uppercase tracking-[0.25em] text-slate-400/70 mb-1">{$t('words.view', { count: 2 })}</p>
						<p class="text-2xl font-semibold text-white">{quiz.views}</p>
					</div>
					<div class="rounded-2xl border border-white/10 bg-white/5 p-4 text-center">
						<p class="text-xs uppercase tracking-[0.25em] text-slate-400/70 mb-1">{$t('words.play', { count: 2 })}</p>
						<p class="text-2xl font-semibold text-white">{quiz.plays}</p>
					</div>
				</div>
			</section>

			<section class="flex flex-col gap-2 mt-6">
				<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80 text-center">{$t('words.info')}</p>
				<p class="text-sm text-slate-400 text-center max-w-lg mx-auto">
					{$t('dashboard.info_analytics')}
				</p>
			</section>

			<div class="mt-auto pt-6 border-t border-white/8">
				<button onclick={() => (quiz = undefined)} class="mx-auto block rounded-full border border-white/15 px-6 py-2.5 text-sm font-semibold text-white/90 hover:bg-white/6 transition-colors">
					Close
				</button>
			</div>
		</div>
	</div>
{/if}
