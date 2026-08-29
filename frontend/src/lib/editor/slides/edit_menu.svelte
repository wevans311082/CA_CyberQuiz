<!-- SPDX-License-Identifier: MPL-2.0 -->
<script lang="ts">
	import type { Konva, ShapeModel } from 'pikaso';
	import Icon from '$lib/ui/Icon.svelte';
	import type { ElementAnimation } from '$lib/quiz_types';

	interface Props { selected_el: null | ShapeModel<Konva.Shape | Konva.Group, Konva.ShapeConfig>; }
	let { selected_el }: Props = $props();
	let open = $state<string | null>(null);
	const is_text = $derived(selected_el?.type === 'label');
	const text_node = $derived((selected_el?.node as any)?.children?.[1] as any);
	const current_font = $derived(text_node?.attrs?.fontFamily ?? 'Inter');
	const current_size = $derived(text_node?.attrs?.fontSize ?? 20);
	const current_animation = $derived((selected_el?.node?.attrs?.animation ?? 'none') as ElementAnimation);
	const current_delay = $derived(selected_el?.node?.attrs?.animationDelay ?? 0);
	const current_duration = $derived(selected_el?.node?.attrs?.animationDuration ?? 520);
	const current_trigger = $derived(selected_el?.node?.attrs?.animationTrigger ?? 'auto');
	const update_text = (patch: Record<string, unknown>) => (selected_el as any)?.updateText(patch as any);
	const update_shape = (patch: Record<string, unknown>) => selected_el?.update(patch as any);
	const toggle = (name: string) => (open = open === name ? null : name);
	const button_class = 'inline-flex h-8 min-w-8 items-center justify-center rounded-lg px-2 text-xs font-semibold text-slate-600 transition hover:bg-teal-50 hover:text-teal-700 disabled:cursor-not-allowed disabled:opacity-35';
</script>

<div class="relative mx-auto flex w-fit max-w-full items-center gap-1 rounded-xl border border-slate-200 bg-white/95 p-1.5 shadow-lg shadow-slate-900/10 backdrop-blur">
	<span class="hidden px-2 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400 sm:inline">Format</span>
	<button type="button" class={button_class} disabled={!selected_el} aria-label="Colour" title="Text or shape colour" onclick={() => toggle('color')}><span class="h-4 w-4 rounded border border-slate-300 bg-gradient-to-br from-teal-500 to-violet-500"></span></button>
	{#if open === 'color'}<div class="absolute left-2 top-11 z-50 rounded-xl border border-slate-200 bg-white p-3 shadow-xl"><input type="color" aria-label="Choose colour" onchange={(e) => { const colour = e.currentTarget.value; is_text ? update_text({ fill: colour }) : update_shape({ fill: colour }); open = null; }} /></div>{/if}
	<button type="button" class={button_class} disabled={!is_text} aria-label="Bold" title="Bold" onclick={() => update_text({ fontStyle: text_node?.attrs?.fontStyle === 'bold' ? 'normal' : 'bold' })}><strong>B</strong></button>
	<button type="button" class={button_class} disabled={!is_text} aria-label="Italic" title="Italic" onclick={() => update_text({ fontStyle: text_node?.attrs?.fontStyle === 'italic' ? 'normal' : 'italic' })}><em>I</em></button>
	<div class="mx-1 h-5 w-px bg-slate-200"></div>
	<select class="h-8 w-28 rounded-lg border border-slate-200 bg-white px-2 text-xs font-medium text-slate-700 outline-none focus:border-teal-500" disabled={!is_text} aria-label="Font family" value={current_font} onchange={(e) => update_text({ fontFamily: e.currentTarget.value })}><option value="Inter">Inter</option><option value="Arial">Arial</option><option value="Segoe UI">Segoe UI</option><option value="Trebuchet MS">Trebuchet MS</option><option value="Georgia">Georgia</option><option value="Courier New">Courier New</option></select>
	<input class="h-8 w-16 rounded-lg border border-slate-200 px-2 text-xs text-slate-700 outline-none focus:border-teal-500" type="number" min="8" max="240" step="1" disabled={!is_text} aria-label="Font size" value={current_size} onchange={(e) => update_text({ fontSize: Number(e.currentTarget.value) || 20 })} />
	<select class="h-8 w-24 rounded-lg border border-slate-200 bg-white px-2 text-xs font-medium text-slate-700 outline-none focus:border-teal-500" disabled={!selected_el} aria-label="Element animation" title="Element animation" value={current_animation} onchange={(e) => update_shape({ animation: e.currentTarget.value })}><option value="none">No motion</option><option value="fade">Fade</option><option value="rise">Rise</option><option value="zoom">Zoom</option><option value="slide-left">Slide</option></select>
	{#if selected_el && current_animation !== 'none'}
		<input class="h-8 w-16 rounded-lg border border-slate-200 px-2 text-xs text-slate-700 outline-none focus:border-teal-500" type="number" min="0" max="10000" step="50" aria-label="Animation delay in milliseconds" title="Delay (ms)" value={current_delay} onchange={(e) => update_shape({ animationDelay: Number(e.currentTarget.value) || 0 })} />
		<input class="h-8 w-16 rounded-lg border border-slate-200 px-2 text-xs text-slate-700 outline-none focus:border-teal-500" type="number" min="100" max="5000" step="50" aria-label="Animation duration in milliseconds" title="Duration (ms)" value={current_duration} onchange={(e) => update_shape({ animationDuration: Number(e.currentTarget.value) || 520 })} />
		<select class="h-8 w-20 rounded-lg border border-slate-200 bg-white px-2 text-xs font-medium text-slate-700 outline-none focus:border-teal-500" aria-label="Animation trigger" title="Trigger" value={current_trigger} onchange={(e) => update_shape({ animationTrigger: e.currentTarget.value })}><option value="auto">Auto</option><option value="click">On click</option></select>
	{/if}
	<div class="mx-1 h-5 w-px bg-slate-200"></div>
	<button type="button" class={button_class} disabled={!is_text} aria-label="Align left" title="Align left" onclick={() => update_text({ align: 'left' })}><Icon name="align-left" size={15} /></button>
	<button type="button" class={button_class} disabled={!is_text} aria-label="Align centre" title="Align centre" onclick={() => update_text({ align: 'center' })}><Icon name="align-center" size={15} /></button>
	<button type="button" class={button_class} disabled={!is_text} aria-label="Align right" title="Align right" onclick={() => update_text({ align: 'right' })}><Icon name="align-right" size={15} /></button>
	<div class="mx-1 h-5 w-px bg-slate-200"></div>
	<button type="button" class={button_class} disabled={!selected_el} aria-label="Bring forward" title="Bring forward" onclick={() => selected_el && update_shape({ zIndex: selected_el.node.getZIndex() + 1 })}><Icon name="arrow-up" size={15} /></button>
	<button type="button" class={button_class} disabled={!selected_el} aria-label="Send backward" title="Send backward" onclick={() => selected_el && update_shape({ zIndex: selected_el.node.getZIndex() - 1 })}><Icon name="arrow-down" size={15} /></button>
	<button type="button" class={button_class} disabled={!selected_el} aria-label="Opacity" title="Opacity" onclick={() => toggle('opacity')}>◐</button>
	{#if open === 'opacity'}<div class="absolute right-2 top-11 z-50 rounded-xl border border-slate-200 bg-white p-3 shadow-xl"><label class="text-[11px] font-semibold text-slate-500">Opacity <input class="ml-2 w-24 align-middle" type="range" min="0.1" max="1" step="0.05" value={selected_el?.node?.attrs?.opacity ?? 1} oninput={(e) => update_shape({ opacity: Number(e.currentTarget.value) })} /></label></div>{/if}
</div>
