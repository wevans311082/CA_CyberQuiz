<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	type Variant = 'glass' | 'elevated' | 'flat';

	interface Props {
		variant?: Variant;
		padding?: 'none' | 'sm' | 'md' | 'lg';
		class?: string;
		children?: import('svelte').Snippet;
	}

	let { variant = 'glass', padding = 'md', class: className = '', children }: Props = $props();

	const variantClasses: Record<Variant, string> = {
		glass:
			'border-slate-200/70 bg-white/85 shadow-[0_20px_60px_rgba(15,23,42,0.08)] backdrop-blur-xl dark:border-slate-700/80 dark:bg-slate-900/70 dark:shadow-[0_20px_60px_rgba(0,0,0,0.35)]',
		elevated:
			'border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-900',
		flat: 'border-slate-200/60 bg-slate-50/80 dark:border-slate-700/60 dark:bg-slate-900/40'
	};

	const paddingClasses: Record<typeof padding, string> = {
		none: '',
		sm: 'p-4',
		md: 'p-6',
		lg: 'p-8'
	};
</script>

<div
	class="rounded-2xl border {variantClasses[variant]} {paddingClasses[padding]} {className}"
>
	{@render children?.()}
</div>