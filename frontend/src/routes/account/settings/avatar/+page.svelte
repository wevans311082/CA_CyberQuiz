<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import Button from '$lib/ui/Button.svelte';
	import Card from '$lib/ui/Card.svelte';
	import Spinner from '$lib/ui/Spinner.svelte';
	import { getLocalization } from '$lib/i18n';
	import AvatarPicker from '$lib/play/AvatarPicker.svelte';
	import { pageTitle } from '$lib/brand';

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
		const res = await fetch(
			`/api/v1/avatar/save?${new URLSearchParams(
				Object.fromEntries(Object.entries(data).map(([k, v]) => [k, String(v)]))
			).toString()}`,
			{ method: 'POST' }
		);
		if (res.ok) {
			save_finished = true;
		}
	};
</script>

<svelte:head>
	<title>{pageTitle('Avatar')}</title>
</svelte:head>

<div class="mx-auto max-w-lg px-4 py-8">
	<Card variant="glass" padding="lg">
		<h1 class="text-center text-2xl font-semibold text-slate-900 dark:text-white">
			{$t('avatar_settings.title', { defaultValue: 'Customise Your Avatar' })}
		</h1>
		<p class="mt-2 text-center text-sm text-slate-500 dark:text-slate-400">
			This avatar appears when you join live quiz sessions.
		</p>

		<div class="mt-6">
			<AvatarPicker
				bind:avatar_params={data}
				bind:confirmed={confirmed}
				onconfirm={() => {
					confirmed = true;
				}}
			/>
		</div>

		<div class="mt-6 flex justify-center gap-3">
			<Button href="/account/settings" variant="secondary">{$t('avatar_settings.go_back', { defaultValue: 'Back' })}</Button>
			<Button onclick={save_avatar} disabled={save_finished === true || !confirmed}>
				{#if save_finished === undefined}
					{$t('words.save', { defaultValue: 'Save Avatar' })}
				{:else if save_finished === true}
					Saved
				{:else}
					<Spinner size="sm" />
				{/if}
			</Button>
		</div>
	</Card>
</div>