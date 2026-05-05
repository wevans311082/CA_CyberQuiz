<!--
SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData } from '$lib/quiz_types';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import Spinner from '$lib/Spinner.svelte';

	interface Props {
		data: EditorData;
		selected_question: number;
		modalOpen: boolean;
	}

	let { data = $bindable(), selected_question, modalOpen = $bindable() }: Props = $props();
	let search_term = $state('security');
	let loading = $state(false);
	let importing = $state(false);
	let icons = $state<any[]>([]);
	let error = $state<string | null>(null);

	const icon_url = (icon: any) => {
		const slug = icon?.slug ?? icon?.id ?? icon?.name;
		if (!slug) return '';
		return `https://thesvg.org/icons/${slug}/default.svg`;
	};

	const fetch_registry = async () => {
		loading = true;
		error = null;
		try {
			const res = await fetch('https://thesvg.org/api/registry.json');
			if (!res.ok) {
				throw new Error(`HTTP ${res.status}`);
			}
			const payload = await res.json();
			const list = Array.isArray(payload)
				? payload
				: Array.isArray(payload?.icons)
					? payload.icons
					: Array.isArray(payload?.data)
						? payload.data
						: [];
			icons = list;
		} catch (e) {
			error = 'Failed to load theSVG registry.';
			icons = [];
		} finally {
			loading = false;
		}
	};

	const select_icon = async (icon: any) => {
		const url = icon_url(icon);
		if (!url) return;
		importing = true;
		try {
			const res = await fetch('/api/v1/storage/import-url', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ url })
			});
			if (!res.ok) {
				throw new Error('import failed');
			}
			const json = await res.json();
			const storage_id = json.id;
			if (selected_question === undefined) {
				data.cover_image = storage_id;
			} else if (selected_question === -1) {
				data.background_image = storage_id;
			} else {
				data.questions[selected_question].image = storage_id;
			}
			modalOpen = false;
		} catch {
			error = 'Unable to import selected icon into storage.';
		} finally {
			importing = false;
		}
	};

	let filtered_icons = $derived.by(() => {
		if (!search_term.trim()) return icons.slice(0, 120);
		const q = search_term.trim().toLowerCase();
		return icons
			.filter((icon) => {
				const title = (icon?.title ?? icon?.name ?? icon?.slug ?? '').toLowerCase();
				const tags = Array.isArray(icon?.tags) ? icon.tags.join(' ').toLowerCase() : '';
				return title.includes(q) || tags.includes(q);
			})
			.slice(0, 120);
	});

	fetch_registry();
</script>

{#if loading || importing}
	<Spinner />
{:else}
	<div class="flex w-screen p-8 h-full mt-8 mb-1">
		<div class="flex flex-col w-2/3 m-auto overflow-scroll h-full rounded-sm p-4 gap-3 bg-white dark:bg-gray-700">
			<h1 class="text-2xl text-center">theSVG Icon Bank</h1>
			<p class="text-xs text-center text-gray-500">Search and import SVG icons into your storage library.</p>
			<form class="w-full flex gap-2" onsubmit={(e) => e.preventDefault()}>
				<input
					class="w-full outline-hidden p-1 rounded-sm dark:bg-gray-500 bg-gray-300"
					bind:value={search_term}
					placeholder="Search icons"
				/>
				<div class="w-fit">
					<BrownButton type="button" onclick={fetch_registry}>Refresh</BrownButton>
				</div>
			</form>
			{#if error}
				<p class="text-sm text-red-600">{error}</p>
			{/if}
			<div class="grid grid-cols-4 gap-2">
				{#each filtered_icons as icon}
					<div class="rounded-sm border border-[#B07156] p-2 flex flex-col gap-2">
						<img
							src={icon.preview_url ?? icon_url(icon)}
							alt={icon?.title ?? icon?.name ?? 'icon'}
							class="w-full h-20 object-contain bg-white"
						/>
						<p class="text-xs truncate">{icon?.title ?? icon?.name ?? icon?.slug}</p>
						<BrownButton type="button" onclick={() => select_icon(icon)}>Select</BrownButton>
					</div>
				{/each}
			</div>
		</div>
	</div>
{/if}
