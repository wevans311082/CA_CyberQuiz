<!--
SPDX-FileCopyrightText: 2026 CA CyberQuiz Team

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { fade, scale } from 'svelte/transition';

	interface Props {
		emoji: string;
		message?: string;
	}

	let { emoji, message }: Props = $props();
	let visible = $state(true);

	// Auto-dismiss after 4 seconds
	let timer: ReturnType<typeof setTimeout> | null = null;
	$effect(() => {
		if (visible) {
			if (timer) clearTimeout(timer);
			timer = setTimeout(() => {
				visible = false;
			}, 4000);
		}
		return () => {
			if (timer) clearTimeout(timer);
		};
	});

	const dismiss = () => {
		visible = false;
	};
</script>

{#if visible}
	<div
		transition:scale={{ duration: 300, start: 0.3 }}
		class="fixed inset-0 flex items-center justify-center pointer-events-auto z-50"
		on:click={dismiss}
	>
		<div class="flex flex-col items-center gap-4">
			<!-- Large animated emoji -->
			<div class="text-9xl animate-bounce select-none drop-shadow-2xl" role="img" aria-label="emoji prompt">
				{emoji}
			</div>

			<!-- Optional message -->
			{#if message}
				<p class="text-2xl font-bold text-white text-center drop-shadow-lg max-w-md px-4">
					{message}
				</p>
			{/if}

			<!-- Dismiss hint -->
			<p class="text-sm text-white/60 mt-2">
				(Click to dismiss)
			</p>
		</div>
	</div>
{/if}

<style>
	@keyframes bounce {
		0%, 100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-20px);
		}
	}

	:global(.animate-bounce) {
		animation: bounce 1s infinite;
	}
</style>
