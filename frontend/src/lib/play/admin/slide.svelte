<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types';
	import type { MasterTheme } from '$lib/quiz_types';
	import { onMount } from 'svelte';
	import Pikaso from 'pikaso';

	interface Props {
		question: Question;
		master_theme?: MasterTheme;
	}

	let { question, master_theme = undefined }: Props = $props();
	const animation_class = $derived(question.animation && question.animation !== 'none' ? `slide-animation-${question.animation}` : '');

	let canvas_el: HTMLDivElement | undefined = $state();
	let canvas: Pikaso;
	let reduced_motion = false;
	let click_animation_queue: Array<{ node: any; animation: string; x: number; y: number; scale_x: number; scale_y: number }> = [];

	const effective_theme_style = $derived.by(() => {
		const base = master_theme ?? {};
		const override = (question.theme_override?.enabled ? question.theme_override : {}) as Record<string, string | undefined>;
		const bg = override.background_color ?? base.background_color;
		const fg = override.text_color ?? base.text_color;
		const font = base.font_family;
		const parts: string[] = [];
		if (bg) parts.push(`background-color: ${bg}`);
		if (fg) parts.push(`color: ${fg}`);
		if (font) parts.push(`font-family: ${font}`);
		return parts.join('; ');
	});

	onMount(() => {
		reduced_motion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
		if (question.type === QuizQuestionType.INFORMATION || question.type === QuizQuestionType.FILE) {
			return;
		}
		canvas = new Pikaso({
			container: canvas_el,
			snapToGrid: {},
			selection: {
				interactive: false
			}
		});
		if (typeof question.answers === 'string') {
			const data = JSON.parse(question.answers);
			canvas.import.json(data);
			if (!reduced_motion) animate_elements((canvas as any).board?.stage);
		}
	});

	const animate_elements = (root: any) => {
		if (!root) return;
		let sequence = 0;
		const visit = (node: any) => {
			const animation = node.getAttr?.('animation');
			if (animation && animation !== 'none' && typeof node.to === 'function') {
				const x = node.x?.() ?? 0;
				const y = node.y?.() ?? 0;
				const scale_x = node.scaleX?.() ?? 1;
				const scale_y = node.scaleY?.() ?? 1;
				const delay = Number(node.getAttr?.('animationDelay') ?? sequence++ * 90);
				const duration = Math.max(100, Number(node.getAttr?.('animationDuration') ?? 520)) / 1000;
				const trigger = node.getAttr?.('animationTrigger') ?? 'auto';
				node.opacity?.(0);
				if (animation === 'rise') node.y?.(y + 22);
				if (animation === 'slide-left') node.x?.(x + 28);
				if (animation === 'zoom') { node.scaleX?.(scale_x * 0.88); node.scaleY?.(scale_y * 0.88); }
				if (trigger === 'click') {
					click_animation_queue.push({ node, animation, x, y, scale_x, scale_y });
				} else {
					animate_node(node, animation, x, y, scale_x, scale_y, duration, delay);
				}
			}
			node.children?.forEach(visit);
		};
		root.children?.forEach(visit);
	};

	const animate_node = (node: any, animation: string, x: number, y: number, scale_x: number, scale_y: number, duration: number, delay = 0) => {
		const target: any = { opacity: 1, duration, delay };
		if (animation === 'rise') target.y = y;
		if (animation === 'slide-left') target.x = x;
		if (animation === 'zoom') { target.scaleX = scale_x; target.scaleY = scale_y; }
		node.to(target);
	};

	const play_next_click_animation = () => {
		const next = click_animation_queue.shift();
		if (!next) return;
		const duration = Math.max(100, Number(next.node.getAttr?.('animationDuration') ?? 520)) / 1000;
		animate_node(next.node, next.animation, next.x, next.y, next.scale_x, next.scale_y, duration);
	};
</script>

<div class="w-full h-full {animation_class}" style={effective_theme_style} role="button" tabindex="0" onclick={play_next_click_animation} onkeydown={(event) => event.key === 'Enter' && play_next_click_animation()}>
	{#if question.type === QuizQuestionType.INFORMATION || question.type === QuizQuestionType.FILE}
		<div class="mx-auto mt-10 max-w-5xl px-6 space-y-4">
			<h2 class="text-4xl text-center">{@html question.question}</h2>
			{#if question.information_body || typeof question.answers === 'string'}
				<div class="rounded-xl border border-gray-300 bg-white/90 p-6 text-gray-900 shadow">
					<div class="whitespace-pre-wrap">{@html question.information_body ?? question.answers}</div>
				</div>
			{/if}
			{#if question.type === QuizQuestionType.FILE && question.file_attachments?.length}
				<div class="space-y-2">
					{#each question.file_attachments as attachment}
						<div class="flex items-center justify-between rounded-lg border border-gray-300 bg-white px-4 py-3">
							<div>
								<p class="font-medium">{attachment.filename}</p>
								<p class="text-xs text-gray-500">{attachment.mime_type}</p>
								{#if attachment.description}
									<div class="text-xs text-gray-600">{@html attachment.description}</div>
								{/if}
							</div>
							<a
								href={attachment.url}
								target="_blank"
								rel="noopener noreferrer"
								class="rounded-md bg-[#B07156] px-3 py-1.5 text-sm font-semibold text-white"
							>
								Open
							</a>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{:else}
		<div bind:this={canvas_el} class="h-full w-full"></div>
	{/if}
</div>

<style>
	:global(.slide-animation-fade) { animation: cyberask-fade 520ms cubic-bezier(.2,.75,.25,1) both; }
	:global(.slide-animation-rise) { animation: cyberask-rise 560ms cubic-bezier(.2,.75,.25,1) both; }
	:global(.slide-animation-zoom) { animation: cyberask-zoom 520ms cubic-bezier(.2,.75,.25,1) both; }
	:global(.slide-animation-slide-left) { animation: cyberask-slide-left 560ms cubic-bezier(.2,.75,.25,1) both; }
	:global(.slide-animation-reveal) { animation: cyberask-reveal 680ms cubic-bezier(.2,.75,.25,1) both; clip-path: inset(0 100% 0 0); }
	@keyframes cyberask-fade { from { opacity: 0; } to { opacity: 1; } }
	@keyframes cyberask-rise { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }
	@keyframes cyberask-zoom { from { opacity: 0; transform: scale(.96); } to { opacity: 1; transform: scale(1); } }
	@keyframes cyberask-slide-left { from { opacity: 0; transform: translateX(28px); } to { opacity: 1; transform: translateX(0); } }
	@keyframes cyberask-reveal { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0 0 0 0); } }
	@media (prefers-reduced-motion: reduce) {
		:global(.slide-animation-fade), :global(.slide-animation-rise), :global(.slide-animation-zoom), :global(.slide-animation-slide-left), :global(.slide-animation-reveal) { animation: none; clip-path: none; transform: none; }
	}
</style>
