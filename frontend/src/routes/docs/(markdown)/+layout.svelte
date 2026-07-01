<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount } from 'svelte';
	import Card from '$lib/ui/Card.svelte';
	import '$lib/hljs.css';

	interface Props {
		children?: import('svelte').Snippet;
	}

	let { children }: Props = $props();

	onMount(async () => {
		const { default: hljs } = await import('highlight.js/lib/common');
		hljs.highlightAll();
	});
</script>

<Card variant="glass" padding="lg" class="prose prose-sm sm:prose lg:prose-lg max-w-none prose-slate dark:prose-invert">
	{@render children?.()}
</Card>