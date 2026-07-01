<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	interface Props {
		id?: string;
		name?: string;
		type?: string;
		value?: string;
		placeholder?: string;
		disabled?: boolean;
		required?: boolean;
		maxlength?: number;
		accept?: string;
		files?: FileList | null;
		ariaLabel?: string;
		autocomplete?: string;
		class?: string;
		oninput?: (event: Event) => void;
		onchange?: (event: Event) => void;
	}

	let {
		id = undefined,
		name = undefined,
		type = 'text',
		value = $bindable(''),
		placeholder = undefined,
		disabled = false,
		required = false,
		maxlength = undefined,
		accept = undefined,
		files = $bindable(null),
		ariaLabel = undefined,
		autocomplete = undefined,
		class: className = '',
		oninput,
		onchange
	}: Props = $props();

	const inputClass =
		'w-full rounded-xl border border-slate-200/80 bg-white/90 px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 transition-colors focus-visible:border-brand-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-accent/30 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:bg-slate-900/80 dark:text-slate-100 dark:placeholder:text-slate-500 ' +
		className;
</script>

{#if type === 'file'}
	<input
		{id}
		{name}
		type="file"
		bind:files
		{accept}
		{disabled}
		{required}
		aria-label={ariaLabel}
		class={inputClass}
		{oninput}
		{onchange}
	/>
{:else if type === 'password'}
	<input
		{id}
		{name}
		type="password"
		bind:value
		{placeholder}
		{disabled}
		{required}
		{maxlength}
		aria-label={ariaLabel}
		autocomplete={autocomplete}
		class={inputClass}
		{oninput}
		{onchange}
	/>
{:else if type === 'search'}
	<input
		{id}
		{name}
		type="search"
		bind:value
		{placeholder}
		{disabled}
		{required}
		{maxlength}
		aria-label={ariaLabel}
		autocomplete={autocomplete}
		class={inputClass}
		{oninput}
		{onchange}
	/>
{:else if type === 'url'}
	<input
		{id}
		{name}
		type="url"
		bind:value
		{placeholder}
		{disabled}
		{required}
		{maxlength}
		aria-label={ariaLabel}
		autocomplete={autocomplete}
		class={inputClass}
		{oninput}
		{onchange}
	/>
{:else}
	<input
		{id}
		{name}
		type="text"
		bind:value
		{placeholder}
		{disabled}
		{required}
		{maxlength}
		aria-label={ariaLabel}
		autocomplete={autocomplete}
		class={inputClass}
		{oninput}
		{onchange}
	/>
{/if}