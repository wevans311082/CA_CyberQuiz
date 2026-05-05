<!--
SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { MasterTheme } from '$lib/quiz_types';

	interface Props {
		master_theme?: MasterTheme;
	}

	let { master_theme = $bindable() }: Props = $props();

	const update_theme = (patch: Partial<MasterTheme>) => {
		master_theme = {
			...(master_theme ?? {}),
			...patch
		};
	};

	const clear_property = (key: keyof MasterTheme) => {
		if (!master_theme) {
			return;
		}
		master_theme = { ...master_theme, [key]: undefined };
	};
</script>

<div class="flex flex-col gap-3">
	<p class="text-xs text-gray-500 dark:text-gray-400">
		Set the default styling for slide and content screens. Individual slide overrides still win.
	</p>
	<div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
		<label class="flex flex-col gap-1 text-xs">
			<span>Background colour</span>
			<div class="flex items-center gap-2">
				<input
					type="color"
					class="h-8 w-12 rounded border border-gray-400 p-0.5"
					value={master_theme?.background_color ?? '#ffffff'}
					oninput={(e) => update_theme({ background_color: e.currentTarget.value })}
				/>
				<button
					type="button"
					class="text-xs text-gray-400 hover:text-red-500"
					onclick={() => clear_property('background_color')}
				>clear</button>
			</div>
		</label>
		<label class="flex flex-col gap-1 text-xs">
			<span>Text colour</span>
			<div class="flex items-center gap-2">
				<input
					type="color"
					class="h-8 w-12 rounded border border-gray-400 p-0.5"
					value={master_theme?.text_color ?? '#111111'}
					oninput={(e) => update_theme({ text_color: e.currentTarget.value })}
				/>
				<button
					type="button"
					class="text-xs text-gray-400 hover:text-red-500"
					onclick={() => clear_property('text_color')}
				>clear</button>
			</div>
		</label>
		<label class="flex flex-col gap-1 text-xs">
			<span>Accent colour</span>
			<div class="flex items-center gap-2">
				<input
					type="color"
					class="h-8 w-12 rounded border border-gray-400 p-0.5"
					value={master_theme?.accent_color ?? '#B07156'}
					oninput={(e) => update_theme({ accent_color: e.currentTarget.value })}
				/>
				<button
					type="button"
					class="text-xs text-gray-400 hover:text-red-500"
					onclick={() => clear_property('accent_color')}
				>clear</button>
			</div>
		</label>
		<label class="flex flex-col gap-1 text-xs">
			<span>Font family</span>
			<select
				class="rounded-lg border border-gray-400 p-1.5 text-sm dark:bg-gray-600 outline-hidden"
				value={master_theme?.font_family ?? ''}
				onchange={(e) => update_theme({ font_family: e.currentTarget.value || undefined })}
			>
				<option value="">Default</option>
				<option value="serif">Serif</option>
				<option value="monospace">Monospace</option>
				<option value="'Inter', sans-serif">Inter</option>
				<option value="'Georgia', serif">Georgia</option>
			</select>
		</label>
	</div>
	{#if Object.values(master_theme ?? {}).some(Boolean)}
		<button
			type="button"
			class="w-fit rounded-lg border border-gray-300 px-3 py-1 text-xs text-gray-500 hover:border-red-300 hover:text-red-500"
			onclick={() => {
				master_theme = undefined;
			}}
		>Clear master theme</button>
	{/if}
</div>