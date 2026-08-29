<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	type Variant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'icon';
	type Size = 'sm' | 'md' | 'lg';

	interface Props {
		variant?: Variant;
		size?: Size;
		disabled?: boolean;
		fullWidth?: boolean;
		href?: string;
		target?: string;
		download?: string | boolean;
		type?: 'button' | 'submit' | 'reset';
		ariaLabel?: string;
		class?: string;
		children?: import('svelte').Snippet;
		onclick?: (event: MouseEvent) => void;
	}

	let {
		variant = 'primary',
		size = 'md',
		disabled = false,
		fullWidth = false,
		href = undefined,
		target = '_self',
		download = undefined,
		type = 'button',
		ariaLabel = undefined,
		class: className = '',
		children,
		onclick
	}: Props = $props();

	const variantClasses: Record<Variant, string> = {
		primary:
			'bg-slate-950 text-white hover:bg-slate-800 border border-transparent shadow-[0_6px_16px_rgba(15,23,42,0.14)] dark:bg-brand-accent dark:text-slate-950 dark:hover:bg-brand-accent-hover',
		secondary:
			'border border-slate-200 bg-white text-slate-700 shadow-sm hover:border-teal-500 hover:bg-teal-50 hover:text-teal-800 dark:border-slate-600 dark:bg-slate-900/80 dark:text-slate-200 dark:hover:border-cyan-400 dark:hover:text-cyan-300',
		ghost:
			'border border-transparent bg-transparent text-slate-600 hover:border-slate-200 hover:bg-white hover:text-slate-900 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800/60',
		danger: 'bg-red-600 text-white hover:bg-red-700 border border-transparent',
		icon: 'border border-slate-200 bg-white text-slate-600 shadow-sm hover:border-teal-300 hover:bg-teal-50 hover:text-teal-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-cyan-400 dark:hover:bg-slate-800 dark:hover:text-cyan-300'
	};

	const sizeClasses: Record<Size, string> = {
		sm: 'px-3 py-1.5 text-xs rounded-lg',
		md: 'px-5 py-2.5 text-sm rounded-xl',
		lg: 'px-6 py-3 text-base rounded-xl'
	};

	const classes = $derived(
		[
			'inline-flex items-center justify-center gap-2 font-semibold transition-colors duration-200',
			'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent focus-visible:ring-offset-2',
			'focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-950',
			'disabled:cursor-not-allowed disabled:opacity-50',
			variant === 'icon' ? 'rounded-xl aspect-square' : sizeClasses[size],
			variantClasses[variant],
			fullWidth ? 'w-full' : '',
			className
		]
			.filter(Boolean)
			.join(' ')
	);
</script>

{#if href}
	<a
		{href}
		{target}
		{download}
		class={classes}
		class:pointer-events-none={disabled}
		class:opacity-50={disabled}
		aria-label={ariaLabel}
		{onclick}
	>
		{@render children?.()}
	</a>
{:else}
	<button {type} {disabled} class={classes} aria-label={ariaLabel} {onclick}>
		{@render children?.()}
	</button>
{/if}
