<!--
SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	interface AvatarParams {
		skin_color?: number;
		hair_color?: number;
		facial_hair_type?: number;
		facial_hair_color?: number;
		top_type?: number;
		hat_color?: number;
		mouth_type?: number;
		eyebrow_type?: number;
		nose_type?: number;
		accessories_type?: number;
		clothe_type?: number;
		clothe_color?: number;
		clothe_graphic_type?: number;
	}

	interface Props {
		username: string;
		avatar_params?: AvatarParams | null;
		compact?: boolean;
		clickable?: boolean;
	}

	let { username, avatar_params = null, compact = false, clickable = false }: Props = $props();
	let avatar_load_failed = $state(false);

	const defaults: Required<AvatarParams> = {
		skin_color: 0,
		hair_color: 0,
		facial_hair_type: 0,
		facial_hair_color: 0,
		top_type: 0,
		hat_color: 0,
		mouth_type: 0,
		eyebrow_type: 0,
		nose_type: 0,
		accessories_type: 0,
		clothe_type: 0,
		clothe_color: 0,
		clothe_graphic_type: 0
	};

	const merged = $derived({ ...defaults, ...(avatar_params ?? {}) });
	const avatar_url = $derived(
		`/api/v1/avatar/custom?${new URLSearchParams(
			Object.fromEntries(Object.entries(merged).map(([key, value]) => [key, String(value)]))
		).toString()}`
	);
	const initials = $derived((username || '?').slice(0, 2).toUpperCase());
</script>

<div
	class="flex items-center gap-3 rounded-2xl border border-slate-200/70 bg-white/80 px-3 py-2 shadow-sm dark:border-slate-700 dark:bg-slate-950/70"
	class:hover:scale-[1.01]={clickable}
	class:hover:shadow-md={clickable}
	class:transition-all={clickable}
>
	{#if avatar_load_failed}
		<div
			class="avatar-fallback flex items-center justify-center rounded-full border border-slate-300 bg-gradient-to-br from-teal-500 to-cyan-600 font-semibold text-white dark:border-slate-700"
			class:h-10={!compact}
			class:w-10={!compact}
			class:h-8={compact}
			class:w-8={compact}
			class:text-xs={compact}
			class:text-sm={!compact}
			aria-label="avatar fallback"
		>
			{initials}
		</div>
	{:else}
		<img
			src={avatar_url}
			alt="avatar"
			class="rounded-full border border-slate-300 bg-white dark:border-slate-700 dark:bg-slate-900"
			class:h-10={!compact}
			class:w-10={!compact}
			class:h-8={compact}
			class:w-8={compact}
			onerror={() => {
				avatar_load_failed = true;
			}}
		/>
	{/if}
	<span class="truncate font-medium text-slate-900 dark:text-slate-100" class:text-sm={compact}>{username}</span>
</div>
