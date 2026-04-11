<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import '../app.css';
	import Navbar from '$lib/navbar.svelte';
	import { pathname, signedIn } from '$lib/stores';
	import { navbarVisible } from '$lib/stores.svelte';

	import { initLocalizationContext } from '$lib/i18n';
	import { browser } from '$app/environment';
	import CommandPalette from '$lib/components/commandpalette.svelte';
	interface Props {
		children?: import('svelte').Snippet;
	}

	let { children }: Props = $props();

	if (browser) {
		pathname.set(window.location.pathname);
		if (
			localStorage.theme === 'dark' ||
			(!('theme' in localStorage) &&
				window.matchMedia('(prefers-color-scheme: dark)').matches)
		) {
			document.documentElement.classList.add('dark');
		} else {
			document.documentElement.classList.remove('dark');
		}
	}
	let start_language = 'en';
	if (browser) {
		start_language = localStorage.getItem('language') ?? 'en';
	}
	initLocalizationContext(start_language);
</script>

{#if navbarVisible.visible}
	<Navbar />
	<div class="pt-16">
		<div class="z-40"></div>
	</div>
{/if}
{@render children?.()}
{#if $signedIn}
	<CommandPalette />
{/if}

<style lang="scss">
	:global(html:not(.dark)) {
		background:
			radial-gradient(circle at top left, rgba(14, 165, 233, 0.15), transparent 35%),
			radial-gradient(circle at top right, rgba(20, 184, 166, 0.16), transparent 30%),
			linear-gradient(180deg, #f8fbff 0%, #edf6fb 48%, #f4f7fb 100%);
		color: black;
	}

	:global(html.dark) {
		background:
			radial-gradient(circle at top left, rgba(34, 211, 238, 0.12), transparent 30%),
			radial-gradient(circle at top right, rgba(20, 184, 166, 0.14), transparent 30%),
			linear-gradient(180deg, #07111d 0%, #0f172a 52%, #111827 100%);
		color: white;

		:global(#pips-slider) {
			--pip: white;
			--pip-active: white;
		}
	}
</style>
