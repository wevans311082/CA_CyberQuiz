<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import Button from '$lib/ui/Button.svelte';

	interface Props {
		disabled?: boolean;
		flex?: boolean;
		href?: undefined | string;
		target?: undefined | string;
		type?: 'button' | 'submit' | 'reset';
		ariaLabel?: string;
		children?: import('svelte').Snippet;
		onclick?: (event: MouseEvent) => void;
	}

	let {
		disabled = false,
		flex = false,
		href = undefined,
		target = '_self',
		type = 'button',
		ariaLabel = undefined,
		children,
		onclick
	}: Props = $props();
</script>

<Button
	variant="icon"
	{disabled}
	{href}
	{target}
	{type}
	ariaLabel={ariaLabel}
	fullWidth={!flex}
	class={flex ? 'w-auto' : ''}
	{onclick}
>
	{@render children?.()}
</Button>