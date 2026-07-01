<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import { fade } from 'svelte/transition';
	// import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { onMount } from 'svelte';
	import Uploader from './uploader.svelte';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();
	let edit_popup = $state(null);
	let images = $state(data.images ?? []);
	let search_query = $state('');
	let mime_filter = $state('all');
	let only_unused = $state(false);

	const usage_count = (image) => (image.quiztivities?.length ?? 0) + (image.quizzes?.length ?? 0);

	let filtered_images = $derived(
		images.filter((image) => {
			const searchable = `${image.filename ?? ''} ${image.alt_text ?? ''} ${image.mime_type ?? ''}`.toLowerCase();
			const by_search = search_query.trim() === '' || searchable.includes(search_query.trim().toLowerCase());
			const by_mime = mime_filter === 'all' || (image.mime_type ?? '').startsWith(mime_filter);
			const by_usage = !only_unused || usage_count(image) === 0;
			return by_search && by_mime && by_usage;
		})
	);

	const close_popup_handler = (e: Event) => {
		if (e.target !== e.currentTarget) return;
		edit_popup = null;
	};
	onMount(() => {
		window.onkeydown = (e: KeyboardEvent) => {
			if (e.key === 'Escape') {
				edit_popup = null;
			}
		};
	});

	const save_image_metadata = async (e: Event) => {
		e.preventDefault();
		await fetch(`/api/v1/storage/meta/${edit_popup.id}`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ filename: edit_popup.filename, alt_text: edit_popup.alt_text })
		});
		images = images.map((img) =>
			img.id === edit_popup.id
				? { ...img, filename: edit_popup.filename, alt_text: edit_popup.alt_text }
				: img
		);
		edit_popup = null;
	};

	const delete_image = async (id: string) => {
		if (!confirm('Delete this asset? This cannot be undone.')) {
			return;
		}
		const res = await fetch(`/api/v1/storage/meta/${id}`, { method: 'DELETE' });
		if (!res.ok) {
			alert('Delete failed. This asset may still be in use.');
			return;
		}
		images = images.filter((img) => img.id !== id);
	};

	const copy_asset_url = async (id: string) => {
		const url = `${window.location.origin}/api/v1/storage/download/${id}`;
		await navigator.clipboard.writeText(url);
	};
</script>

<div>
	<h2 class="text-center text-4xl">
		{$t('file_dashboard.storage_usage', {
			used: (data.storage_usage.used / (1024 * 1024)).toFixed(2),
			total: (data.storage_usage.limit / (1024 * 1024)).toFixed(0),
			percent: ((data.storage_usage.used / data.storage_usage.limit) * 100).toFixed(0)
		})}
	</h2>
	<Uploader />
	<div class="grid grid-cols-1 md:grid-cols-4 gap-2 px-4 mt-4">
		<input
			type="text"
			placeholder="Search filename, alt text, or mime..."
			class="rounded border border-gray-400 bg-white/90 dark:bg-gray-700 p-2"
			bind:value={search_query}
		/>
		<select class="rounded border border-gray-400 bg-white/90 dark:bg-gray-700 p-2" bind:value={mime_filter}>
			<option value="all">All types</option>
			<option value="image/">Images</option>
			<option value="video/">Videos</option>
			<option value="audio/">Audio</option>
			<option value="application/">Documents</option>
		</select>
		<label class="flex items-center gap-2 rounded border border-gray-400 bg-white/90 dark:bg-gray-700 p-2">
			<input type="checkbox" bind:checked={only_unused} />
			<span>Only unused assets</span>
		</label>
		<div class="rounded border border-gray-400 bg-white/90 dark:bg-gray-700 p-2 text-sm flex items-center justify-center">
			Showing {filtered_images.length} of {images.length}
		</div>
	</div>
	<div class="grid grid-cols-1 lg:grid-cols-2 p-4 gap-4">
		{#each filtered_images as image}
			<div
				class="border-2 border-[#B07156] rounded-sm p-2 grid grid-cols-2 hover:opacity-100 transition-all"
				class:opacity-40={usage_count(image) === 0}
			>
				<img
					src="/api/v1/storage/download/{image.id}"
					class="m-auto h-auto w-auto max-h-[30vh]"
					loading="lazy"
					alt={image.alt_text || $t('file_dashboard.not_available')}
				/>
				<div class="flex flex-col my-auto ml-4">
					<p>
						{$t('file_dashboard.size', {
							size: (image.size / (1024 * 1024)).toFixed(2)
						})}
					</p>
					<p>
						{$t('file_dashboard.caption', {
							caption: image.alt_text ?? $t('file_dashboard.missing')
						})}
					</p>
					<p>
						{$t('file_dashboard.filename', {
							filename: image.filename ?? $t('file_dashboard.missing')
						})}
					</p>
					<p>
						{$t('file_dashboard.uploaded', {
							date: new Date(image.uploaded_at).toLocaleString()
						})}
					</p>
					<p>Used by {usage_count(image)} item(s)</p>
					<p>
						{$t('file_dashboard.imported', {
							yes_or_no: image.imported ? $t('words.yes') : $t('words.no')
						})}
					</p>
					<div class="flex flex-col gap-2">
						<BrownButton href={`/api/v1/storage/download/${image.id}`}>
							Download/Open
						</BrownButton>
						<BrownButton onclick={() => copy_asset_url(image.id)}>
							Copy Link
						</BrownButton>
						<BrownButton
							onclick={() => {
								edit_popup = image;
							}}
							>{$t('file_dashboard.edit_details')}
						</BrownButton>
						{#if usage_count(image) === 0}
							<BrownButton
								onclick={() => {
									delete_image(image.id);
								}}>{$t('file_dashboard.delete_image')}</BrownButton
							>
						{/if}
					</div>
				</div>
			</div>
		{/each}
	</div>
</div>

{#if edit_popup}
	<div
		transition:fade={{ duration: 100 }}
		class="fixed top-0 left-0 h-screen w-screen z-40 flex bg-black/50"
		onclick={close_popup_handler}
	>
		<div class="w-auto h-auto m-auto rounded-sm bg-white dark:bg-gray-700 p-4">
			<h1 class="text-2xl text-center">{$t('file_dashboard.edit_the_image')}</h1>
			<form class="flex flex-col" onsubmit={save_image_metadata}>
				<div class="flex flex-row">
					<div class="flex flex-col mr-4">
						<label for="name" class="m-auto">{$t('file_dashboard.filename_word')}</label
						>
						<label for="alt_text" class="m-auto">{$t('file_dashboard.alt_text')}</label>
					</div>
					<div class="flex flex-col gap-3">
						<input
							class="rounded-sm outline-hidden dark:bg-gray-500 p-0.5 border-4 border-transparent"
							id="name"
							type="text"
							bind:value={edit_popup.filename}
						/>
						<input
							class:border-red-700={!edit_popup.alt_text}
							class="transition rounded-sm outline-hidden dark:bg-gray-500 p-0.5 border-4 border-transparent"
							id="alt_text"
							type="text"
							bind:value={edit_popup.alt_text}
						/>
					</div>
				</div>
				<div class="mt-4">
					<BrownButton type="submit">{$t('words.save')}</BrownButton>
				</div>
			</form>
		</div>
	</div>
{/if}
