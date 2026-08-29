<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Markdown } from '$lib/quiztivity/types';
	import DOMPurify from 'dompurify';
	import { marked } from 'marked';
	import { browser } from '$app/environment';

	interface Props {
		data: any;
	}

	let { data }: Props = $props();

	let rendered_html = $derived(
		browser ? DOMPurify.sanitize(marked.parse(data.markdown ?? '') as string) : ''
	);
</script>

<div class="prose dark:prose-invert">
	{@html rendered_html}
</div>
