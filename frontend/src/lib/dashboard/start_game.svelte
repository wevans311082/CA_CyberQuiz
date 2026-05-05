<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	// import { alertModal } from '$lib/stores';
	import { captcha_enabled } from '$lib/config';
	import { fade } from 'svelte/transition';
	import Spinner from '$lib/Spinner.svelte';
	import { onMount } from 'svelte';
	import { createTippy } from 'svelte-tippy';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	let { quiz_id = $bindable() } = $props();
	let captcha_selected = $state(false);
	let selected_game_mode = $state('kahoot');
	let loading = $state(false);
	let custom_field = $state('');
	let cqcs_enabled = $state(false);
	let randomized_answers = $state(false);

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'top-start',
		allowHTML: true
	});

	onMount(() => {
		const ls_data = localStorage.getItem('custom_field');
		custom_field = ls_data ? ls_data : '';
	});

	const start_game = async (id: string) => {
		let res;
		loading = true;
		localStorage.setItem('custom_field', custom_field);
		const cqcs_enabled_parsed = cqcs_enabled ? 'True' : 'False';
		const randomized_answers_parsed = randomized_answers ? 'True' : 'False';
		if (captcha_enabled && captcha_selected) {
			res = await fetch(
				`/api/v1/quiz/start/${id}?captcha_enabled=True&game_mode=${selected_game_mode}&custom_field=${custom_field}&cqcs_enabled=${cqcs_enabled_parsed}`,
				{
					method: 'POST'
				}
			);
		} else {
			res = await fetch(
				`/api/v1/quiz/start/${id}?captcha_enabled=False&game_mode=${selected_game_mode}&custom_field=${custom_field}&cqcs_enabled=${cqcs_enabled_parsed}&randomize_answers=${randomized_answers_parsed}`,
				{
					method: 'POST'
				}
			);
		}
		if (res.status !== 200) {
			/*			alertModal.set({
				open: true,
				title: 'Start failed',
				body: `Failed to start game, ${await res.text()}`
			});*/
			/*alertModal.subscribe((_) => {
				window.location.assign('/account/login?returnTo=/dashboard');
			});*/
			alert('Starting game failed');
			window.location.assign('/account/login?returnTo=/dashboard');
		} else {
			const data = await res.json();
			// eslint-disable-next-line no-undef
			plausible('Started Game', { props: { quiz_id: id, game_id: data.game_id } });
			window.location.assign(
				`/admin?token=${data.game_id}&pin=${data.game_pin}&connect=1&cqc_code=${data.cqc_code}`
			);
		}
	};

	const on_parent_click = (e: Event) => {
		if (e.target !== e.currentTarget) {
			return;
		}
		quiz_id = null;
	};
	const close_start_game_if_esc_is_pressed = (key: KeyboardEvent) => {
		if (key.code === 'Escape') {
			quiz_id = null;
		}
	};
	onMount(() => {
		document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
	});
</script>

<div
	class="fixed top-0 left-0 flex justify-center items-center w-screen h-screen bg-black/70 z-50"
	transition:fade|global={{ duration: 100 }}
	onclick={on_parent_click}
>
	<div class="relative w-full max-w-2xl mx-4 rounded-[2rem] border border-white/15 bg-[#0f172a]/95 backdrop-blur-2xl shadow-[0_30px_120px_rgba(15,23,42,0.7)] p-8 flex flex-col gap-6 text-white">

		<!-- Header -->
		<div class="text-center">
			<p class="text-xs uppercase tracking-[0.35em] text-slate-400/80 mb-2">Session Configuration</p>
			<h2 class="text-3xl font-semibold">{$t('start_game.start_game')}</h2>
		</div>

		<!-- Game Mode -->
		<div>
			<p class="text-xs uppercase tracking-[0.3em] text-slate-400/70 mb-3">Game Mode</p>
			<div class="grid grid-cols-2 gap-4">
				<button
					class="{selected_game_mode === 'kahoot' ? 'border-[#B07156] bg-[#B07156]/10' : 'border-white/10 bg-white/5 opacity-60'} rounded-2xl border p-4 text-left transition-all cursor-pointer hover:opacity-100"
					onclick={() => { selected_game_mode = 'kahoot'; }}
				>
					<h3 class="text-base font-semibold mb-1">{$t('words.normal')}</h3>
					<p class="text-sm text-slate-400">{$t('start_game.normal_mode_description')}</p>
				</button>
				<button
					class="{selected_game_mode === 'normal' ? 'border-[#B07156] bg-[#B07156]/10' : 'border-white/10 bg-white/5 opacity-60'} rounded-2xl border p-4 text-left transition-all cursor-pointer hover:opacity-100"
					onclick={() => { selected_game_mode = 'normal'; }}
				>
					<h3 class="text-base font-semibold mb-1">{$t('start_game.old_school_mode')}</h3>
					<p class="text-sm text-slate-400">{$t('start_game.old_school_mode_description')}</p>
				</button>
			</div>
		</div>

		<!-- Custom field -->
		<div>
			<label class="text-xs uppercase tracking-[0.3em] text-slate-400/70 block mb-2" for="custom-field-input">{$t('result_page.custom_field')}</label>
			<input
				id="custom-field-input"
				bind:value={custom_field}
				class="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 outline-none focus:border-[#B07156]/60 transition-colors"
				placeholder="Phone Number or Email"
			/>
		</div>

		<!-- Toggle options -->
		<div class="flex flex-col gap-3">
			{#if captcha_enabled}
				<label class="flex items-center gap-3 cursor-pointer group">
					<div class="relative">
						<input type="checkbox" bind:checked={captcha_selected} id="large-toggle" class="sr-only peer" />
						<div class="w-10 h-5 rounded-full bg-white/10 peer-checked:bg-[#B07156] transition-colors"></div>
						<div class="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform peer-checked:translate-x-5"></div>
					</div>
					<span class="text-sm text-slate-300 group-hover:text-white transition-colors">Captcha {captcha_selected ? 'enabled' : 'disabled'}</span>
				</label>
				{#if captcha_selected}
					<p class="text-xs text-slate-400 pl-13 -mt-1" in:fade|global>{$t('start_game.captcha_message')}</p>
				{/if}
			{/if}

			<label class="flex items-center gap-3 cursor-pointer group">
				<div class="relative">
					<input type="checkbox" bind:checked={cqcs_enabled} id="cqc-toggle" class="sr-only peer" />
					<div class="w-10 h-5 rounded-full bg-white/10 peer-checked:bg-[#B07156] transition-colors"></div>
					<div class="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform peer-checked:translate-x-5"></div>
				</div>
				<span class="text-sm text-slate-300 group-hover:text-white transition-colors">
					<a
						href="/controller"
						target="_blank"
						use:tippy={{ content: 'ClassQuizControllers are small physical devices to play ClassQuiz. Click to learn more.' }}
						class="decoration-dashed underline cursor-help"
					>ClassQuizControllers</a> are {cqcs_enabled ? 'enabled' : 'disabled'}
				</span>
			</label>

			<label class="flex items-center gap-3 cursor-pointer group">
				<div class="relative">
					<input type="checkbox" bind:checked={randomized_answers} id="randomized-answers-toggle" class="sr-only peer" />
					<div class="w-10 h-5 rounded-full bg-white/10 peer-checked:bg-[#B07156] transition-colors"></div>
					<div class="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform peer-checked:translate-x-5"></div>
				</div>
				<span class="text-sm text-slate-300 group-hover:text-white transition-colors">Randomize answers</span>
			</label>
		</div>

		<!-- Action buttons -->
		<div class="flex gap-3 pt-2">
			<button
				class="flex-1 rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-white/90 hover:bg-white/6 transition-colors"
				onclick={() => { quiz_id = null; }}
			>
				Cancel
			</button>
			<button
				class="flex-1 rounded-full bg-[#B07156] px-6 py-3 text-sm font-semibold text-slate-950 hover:bg-[#c07d62] transition-colors flex items-center justify-center gap-2"
				onclick={() => { start_game(quiz_id); }}
			>
				{#if loading}
					<Spinner my_20={false} />
				{:else}
					{$t('start_game.start_game')}
				{/if}
			</button>
		</div>
	</div>
</div>
