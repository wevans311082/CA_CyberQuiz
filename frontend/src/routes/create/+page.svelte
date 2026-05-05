<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount } from 'svelte';
	import Editor from '$lib/editor.svelte';
	import { getLocalization } from '$lib/i18n';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import type { EditorData, Question } from '$lib/quiz_types';
	import { page } from '$app/state';

	navbarVisible.visible = false;

	const { t } = getLocalization();

	interface Data {
		public: boolean;
		title: string;
		description: string;
		questions: Question[];
		scenario_type?: string;
		roles?: string[];
	}

	type QuizMode = 'classic' | 'tabletop';

	let responseData = {
		open: false
	};

	let data: Data = $state();
	let quiz_id = $state(null);
	let create_mode_dialog_open = $state(false);
	let selected_mode = $state<QuizMode>('classic');
	let pending_title = $state('');

	const initialize_quiz_data = (mode: QuizMode) => {
		data = {
			description: '',
			public: false,
			title: pending_title,
			questions: [],
			scenario_type: mode === 'tabletop' ? 'tabletop' : undefined,
			roles: mode === 'tabletop' ? [] : undefined
		};
		create_mode_dialog_open = false;
	};

	const resolve_requested_mode = (): QuizMode | null => {
		const mode = page.url.searchParams.get('mode') ?? page.url.searchParams.get('scenario_type');
		if (mode === 'tabletop') {
			return 'tabletop';
		}
		if (mode === 'classic' || mode === 'quiz') {
			return 'classic';
		}
		return null;
	};

	onMount(() => {
		const from_localstorage = localStorage.getItem('create_game');
		let title = page.url.searchParams.get('title');
		title ??= '';
		pending_title = title;
		if (from_localstorage === null) {
			const requested_mode = resolve_requested_mode();
			if (requested_mode) {
				selected_mode = requested_mode;
				initialize_quiz_data(requested_mode);
			} else {
				create_mode_dialog_open = true;
			}
		} else {
			data = JSON.parse(from_localstorage) as EditorData;
		}
	});
</script>

<svelte:head>
	<title>ClassQuiz - Create</title>
</svelte:head>

{#if data !== undefined}
	<Editor bind:data bind:quiz_id />
{:else if create_mode_dialog_open}
	<div class="relative min-h-screen overflow-hidden bg-[#0f172a] text-slate-100">
		<div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(20,184,166,0.22),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(176,113,86,0.28),_transparent_35%),linear-gradient(180deg,_#0f172a_0%,_#111827_100%)]"></div>
		<div class="absolute inset-0 opacity-20 [background-image:linear-gradient(rgba(255,255,255,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.08)_1px,transparent_1px)] [background-size:32px_32px]"></div>
		<div class="relative z-10 flex min-h-screen items-center justify-center p-6">
			<div class="w-full max-w-5xl overflow-hidden rounded-[2rem] border border-white/15 bg-white/8 shadow-[0_30px_120px_rgba(15,23,42,0.55)] backdrop-blur-2xl">
				<div class="grid gap-0 lg:grid-cols-[1.1fr_1.4fr]">
					<div class="flex flex-col justify-between border-b border-white/10 bg-black/15 p-8 lg:border-b-0 lg:border-r">
						<div>
							<p class="text-xs font-semibold uppercase tracking-[0.35em] text-teal-200/80">New Quiz</p>
							<h1 class="mt-4 text-4xl font-semibold leading-tight text-white">Choose the format before the editor opens.</h1>
							<p class="mt-4 max-w-md text-sm leading-7 text-slate-300">
								Pick the experience first so the editor, lobby, and host tools all start in the right mode.
							</p>
						</div>
						<div class="mt-8 rounded-3xl border border-white/10 bg-white/8 p-5">
							<p class="text-xs uppercase tracking-[0.28em] text-slate-400">Selected</p>
							<p class="mt-2 text-2xl font-semibold text-white">
								{selected_mode === 'tabletop' ? 'Tabletop Exercise' : 'Classic Quiz'}
							</p>
							<p class="mt-2 text-sm text-slate-300">
								{#if selected_mode === 'tabletop'}
									Decision-focused flow with role assignment, branching, and facilitator controls.
								{:else}
									Standard quiz flow for questions, polls, slides, and classic player pacing.
								{/if}
							</p>
						</div>
					</div>

					<div class="p-8 lg:p-10">
						<div class="grid gap-5 md:grid-cols-2">
							<button
								type="button"
								class={`group relative overflow-hidden rounded-[1.75rem] border p-6 text-left transition duration-200 ${selected_mode === 'classic' ? 'border-[#B07156] bg-white text-slate-900 shadow-[0_18px_50px_rgba(176,113,86,0.28)]' : 'border-white/12 bg-white/6 text-white'}`}
								onclick={() => {
									selected_mode = 'classic';
								}}
							>
								<div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(176,113,86,0.22),_transparent_40%)] opacity-0 transition group-hover:opacity-100"></div>
								<div class="relative">
									<div class="flex items-center justify-between">
										<p class="text-xs font-semibold uppercase tracking-[0.28em] opacity-70">Classic</p>
										<span class={`rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] ${selected_mode === 'classic' ? 'border-slate-300' : 'border-white/20'}`}>
											Quiz
										</span>
									</div>
									<h2 class="mt-6 text-2xl font-semibold">Fast setup for standard quizzes</h2>
									<p class="mt-3 text-sm leading-7 opacity-80">Use classic quizzes for multiple choice, polls, ordering, slides, and the normal lobby flow.</p>
									<ul class="mt-5 space-y-2 text-sm opacity-80">
										<li>ABCD, poll, text, order, and range questions</li>
										<li>Slide and file screens</li>
										<li>Standard host and player experience</li>
									</ul>
								</div>
							</button>

							<button
								type="button"
								class={`group relative overflow-hidden rounded-[1.75rem] border p-6 text-left transition duration-200 ${selected_mode === 'tabletop' ? 'border-teal-300 bg-white text-slate-900 shadow-[0_18px_50px_rgba(45,212,191,0.25)]' : 'border-white/12 bg-white/6 text-white'}`}
								onclick={() => {
									selected_mode = 'tabletop';
								}}
							>
								<div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(45,212,191,0.22),_transparent_40%)] opacity-0 transition group-hover:opacity-100"></div>
								<div class="relative">
									<div class="flex items-center justify-between">
										<p class="text-xs font-semibold uppercase tracking-[0.28em] opacity-70">Scenario</p>
										<span class={`rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] ${selected_mode === 'tabletop' ? 'border-slate-300' : 'border-white/20'}`}>
											Tabletop
										</span>
									</div>
									<h2 class="mt-6 text-2xl font-semibold">Facilitated incident exercise</h2>
									<p class="mt-3 text-sm leading-7 opacity-80">Use tabletop mode for role assignment, branching decisions, injects, and facilitator-led discussion.</p>
									<ul class="mt-5 space-y-2 text-sm opacity-80">
										<li>Role-based participation and approvals</li>
										<li>Branching paths and discussion timers</li>
										<li>Injects, evidence files, and situation updates</li>
									</ul>
								</div>
							</button>
						</div>

						<div class="mt-8 flex flex-col gap-3 border-t border-white/10 pt-6 sm:flex-row sm:items-center sm:justify-between">
							<p class="text-sm text-slate-300">You can still edit content and styling afterwards; this just chooses the right workflow up front.</p>
							<div class="flex gap-3">
								<a
									href="/dashboard"
									class="inline-flex items-center justify-center rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-white/90 transition hover:border-white/30 hover:bg-white/6"
								>
									Back
								</a>
								<button
									type="button"
									class="inline-flex items-center justify-center rounded-full bg-[#B07156] px-6 py-3 text-sm font-semibold text-slate-950 shadow-[0_16px_40px_rgba(176,113,86,0.35)] transition hover:translate-y-[-1px] hover:opacity-90"
									onclick={() => initialize_quiz_data(selected_mode)}
								>
									Continue to editor
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}

<div
	class="fixed z-10 inset-0 overflow-y-auto"
	aria-labelledby="modal-title"
	role="dialog"
	aria-modal="true"
	class:hidden={!responseData.open}
>
	<div
		class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"
	>
		<div class="fixed inset-0 bg-gray-500/75 transition-opacity" aria-hidden="true"></div>

		<span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true"
			>&#8203;</span
		>
		<div
			class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"
		>
			<div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
				<div class="sm:flex sm:items-start">
					<div
						class="mx-auto shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"
					>
						<!-- Heroicon name: outline/exclamation -->
						<svg
							class="w-6 h-6 text-green-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					</div>
					<div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
						<h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
							{$t('create_page.success.title')}
						</h3>
						<div class="mt-2">
							<p class="text-sm text-gray-500">{$t('create_page.success.body')}</p>
						</div>
					</div>
				</div>
			</div>
			<div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
				<button
					type="button"
					onclick={() => {
						window.location.href = '/dashboard';
					}}
					class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-xm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-hidden focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
					>{$t('words.close')}
				</button>
			</div>
		</div>
	</div>
</div>
