<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import Spinner from '$lib/Spinner.svelte';
	import { getLocalization } from '$lib/i18n';
	import AvatarPicker from '$lib/play/AvatarPicker.svelte';

	const { t } = getLocalization();

	let data = $state({
		skin_color: 0,
		top_type: 0,
		hair_color: 0,
		facial_hair_type: 0,
		facial_hair_color: 0,
		mouth_type: 0,
		eyebrow_type: 0,
		accessories_type: 0,
		hat_color: 0,
		clothe_type: 0,
		clothe_color: 0,
		clothe_graphic_type: 0,
		nose_type: 0
	});

	let confirmed = $state(false);
	let save_finished: undefined | boolean = $state(undefined);

	const save_avatar = async () => {
		save_finished = false;
		const res = await fetch(`/api/v1/avatar/save?${new URLSearchParams(
			Object.fromEntries(Object.entries(data).map(([k, v]) => [k, String(v)]))
		).toString()}`, {
			method: 'POST'
		});
		if (res.ok) {
			save_finished = true;
		}
	};
</script>

<div class="mx-auto max-w-lg px-4 py-8">
	<h1 class="mb-6 text-center text-2xl font-bold text-slate-900 dark:text-white">{$t('avatar_settings.title', { defaultValue: 'Customise Your Avatar' })}</h1>

	<AvatarPicker
		bind:avatar_params={data}
		bind:confirmed={confirmed}
		onconfirm={() => { confirmed = true; }}
	/>

	<div class="mt-6 flex justify-center gap-3">
		<BrownButton href="/account/settings">{$t('avatar_settings.go_back', { defaultValue: 'Back' })}</BrownButton>
		<BrownButton onclick={save_avatar} disabled={save_finished === true || !confirmed}>
			{#if save_finished === undefined}{$t('words.save', { defaultValue: 'Save Avatar' })}
			{:else if save_finished === true}
				<svg class="h-5 w-5 inline" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
					<path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round" />
				</svg>
				Saved
			{:else if save_finished === false}
				<Spinner my_20={false} />
			{/if}
		</BrownButton>
	</div>
</div>
