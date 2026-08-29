<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { run } from 'svelte/legacy';

	import type { Question } from '$lib/quiz_types';
	import { ElementTypes, QuizQuestionType } from '$lib/quiz_types';
	import ElementSelection from './slides/element_selection.svelte';
	import SettingsMenu from './slides/settings_menu.svelte';
	import { onMount } from 'svelte';
	import Pikaso, { createImageFromUrl } from 'pikaso';
	import EditMenu from './slides/edit_menu.svelte';
	import type { Konva, ShapeModel } from 'pikaso';
	import { browser } from '$app/environment';

	interface Props {
		data?: Question;
		master_theme?: import('$lib/quiz_types').MasterTheme;
	}

	let { data = $bindable({
		type: QuizQuestionType.SLIDE,
		time: '120',
		question: '',
		image: undefined,
		answers: ''
	}), master_theme = undefined }: Props = $props();
	let selected_element = $state(undefined);
	let canvas_el: HTMLDivElement | undefined = $state();
	let canvas: Pikaso;
	let selected_el: any = $state(null);
	let properties_open = $state(false);
	let history_open = $state(false);
	let history_stack = $state<string[]>([]);
	let history_index = $state(-1);
	let applying_history = false;
	let locked_elements = $state<Set<any>>(new Set());
	let layer_items = $state<any[]>([]);
	let layer_models = $state<any[]>([]);
	let format_clipboard = $state<Record<string, any> | null>(null);
	let animation_timeline_open = $state(false);
	let animation_drag_index = $state<number | null>(null);

	let elements_binds: Array<HTMLElement> | undefined = [];
	let main_el: undefined | HTMLElement = $state();
	let settings_menu_open = $state(false);
	let thesvg_open = $state(false);
	let thesvg_search = $state('security');
	let thesvg_icons = $state<any[]>([]);
	let thesvg_loading = $state(false);
	let image_input = $state<HTMLInputElement>();

	const set_correct_height = new ResizeObserver((e) => {
		for (const i of e) {
			const id = parseInt(i.target.getAttribute('el_id'));
			data.answers[id].width = i.contentRect.width / main_el.offsetWidth;
			data.answers[id].height = i.contentRect.height / main_el.offsetHeight;
		}
	});

	let darkMode = false;
	if (browser) {
		darkMode =
			localStorage.theme === 'dark' ||
			(!('theme' in localStorage) &&
				window.matchMedia('(prefers-color-scheme: dark)').matches);
	}
	const add_text_field = () => {
		if (selected_element === ElementTypes.Text) {
			canvas.shapes.label.insert({
				container: {
					x: 40,
					y: 40
				},
				text: {
					text: 'Text',
					fontSize: 20
				}
			});
		} else if (selected_element === ElementTypes.Headline) {
			canvas.shapes.label.insert({
				container: {
					x: 40,
					y: 40
				},
				text: {
					text: 'Headline',
					fontSize: 35
				}
			});
		} else if (selected_element === ElementTypes.Circle) {
			canvas.shapes.circle.insert({
				x: 40,
				y: 40,
				radius: 50,
				fill: '#ff000d'
			});
		} else if (selected_element === ElementTypes.Rectangle) {
			canvas.shapes.rect.insert({
				x: 40,
				y: 40,
				width: 50,
				height: 50,
				fill: '#ff000d'
			});
		}
	};

	const thesvg_icon_url = (icon: any) => {
		const slug = icon?.slug ?? icon?.id ?? icon?.name;
		if (!slug) return '';
		return `https://thesvg.org/icons/${slug}/default.svg`;
	};

	const load_thesvg_registry = async () => {
		thesvg_loading = true;
		try {
			const res = await fetch('https://thesvg.org/api/registry.json');
			if (!res.ok) {
				thesvg_icons = [];
				return;
			}
			const payload = await res.json();
			thesvg_icons = Array.isArray(payload)
				? payload
				: Array.isArray(payload?.icons)
					? payload.icons
					: Array.isArray(payload?.data)
						? payload.data
						: [];
		} catch {
			thesvg_icons = [];
		} finally {
			thesvg_loading = false;
		}
	};

	const insert_thesvg = async (icon: any, position = { x: 60, y: 60 }) => {
		const url = thesvg_icon_url(icon);
		if (!url) return;
		const res = await fetch('/api/v1/storage/import-url', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ url })
		});
		if (!res.ok) {
			return;
		}
		const json = await res.json();
		const src = `/api/v1/storage/download/${json.id}`;
		if (!canvas?.shapes?.image?.insert) return;
		const image = await createImageFromUrl(src);
		await canvas.shapes.image.insert(image, { ...position, width: 160, height: 160 });
	};

	const drop_svg = async (event: DragEvent) => {
		event.preventDefault();
		const dropped_file = event.dataTransfer?.files?.[0];
		const rect = canvas_el?.getBoundingClientRect();
		const position = rect ? { x: Math.max(20, event.clientX - rect.left - 80), y: Math.max(20, event.clientY - rect.top - 80) } : { x: 60, y: 60 };
		if (dropped_file?.type.startsWith('image/')) {
			await upload_image_file(dropped_file, position);
			return;
		}
		const slug = event.dataTransfer?.getData('application/x-cyberask-svg');
		if (slug) await insert_thesvg({ slug }, position);
	};

	const upload_image_file = async (file: File, position = { x: 60, y: 60 }) => {
		if (!canvas?.shapes?.image?.insert) return;
		const form = new FormData();
		form.append('file', file);
		const response = await fetch('/api/v1/storage/', { method: 'POST', body: form });
		if (!response.ok) throw new Error('Unable to upload image');
		const payload = await response.json();
		const image = await createImageFromUrl(`/api/v1/storage/download/${payload.id}`);
		await canvas.shapes.image.insert(image, { ...position, width: 220, height: 160 });
	};

	const selected_attrs = $derived(selected_el?.node?.attrs as Record<string, any> | undefined);
	const update_geometry = (key: string, value: string) => {
		if (!selected_el) return;
		const numeric = Number(value);
		if (!Number.isFinite(numeric)) return;
		selected_el.update({ [key]: numeric } as any);
	};

	const update_selected_fill = (event: Event) => {
		const value = (event.currentTarget as HTMLInputElement).value;
		if (selected_el?.type === 'label') selected_el.updateText({ fill: value });
		else selected_el?.update({ fill: value });
	};
	const sync_layers = () => {
		layer_models = [...((canvas as any)?.board?.shapes ?? [])].reverse();
		layer_items = layer_models.map((shape: any) => shape.node).filter((node: any) => node?.attrs?.name !== 'Transformer');
	};
	const record_history = () => {
		if (!canvas || applying_history) return;
		const json = JSON.stringify(canvas.export.toJson());
		if (history_stack[history_index] === json) return;
		history_stack = [...history_stack.slice(0, history_index + 1), json].slice(-50);
		history_index = history_stack.length - 1;
	};
	const restore_history = (index: number) => {
		const json = history_stack[index];
		if (!json || !canvas) return;
		applying_history = true;
		canvas.import.json(JSON.parse(json));
		data.answers = json;
		history_index = index;
		applying_history = false;
		sync_layers();
	};
	const undo = () => restore_history(Math.max(0, history_index - 1));
	const redo = () => restore_history(Math.min(history_stack.length - 1, history_index + 1));
	const duplicate_selected = () => {
		const node = selected_el?.node as any;
		if (!node) return;
		const clone = node.clone({ x: (node.x?.() ?? 40) + 24, y: (node.y?.() ?? 40) + 24 });
		node.getParent()?.add(clone);
		(canvas as any)?.board?.stage?.draw();
		record_history();
		sync_layers();
	};
	const toggle_lock = () => {
		if (!selected_el) return;
		const next = new Set(locked_elements);
		if (next.has(selected_el.node)) next.delete(selected_el.node); else next.add(selected_el.node);
		locked_elements = next;
		selected_el.update({ draggable: !next.has(selected_el.node), locked: next.has(selected_el.node) } as any);
		record_history();
	};
	const group_selected = () => {
		const selection = (canvas as any)?.board?.selection;
		if (!selection || selection.shapes.length < 2) return;
		selection.group(`group-${Date.now()}`);
		record_history();
		sync_layers();
	};
	const ungroup_selected = () => {
		const group = selected_el?.group;
		if (!group) return;
		(canvas as any)?.board?.groups?.ungroup(group);
		record_history();
		sync_layers();
	};
	const select_layer = (shape: any) => shape?.select?.();
	const selected_shapes = () => (canvas as any)?.board?.selection?.shapes ?? [];
	const align_selected = (mode: 'left' | 'center' | 'top') => {
		const shapes = selected_shapes();
		if (shapes.length < 2) return;
		const nodes = shapes.map((shape: any) => shape.node);
		const left = Math.min(...nodes.map((node: any) => node.x()));
		const top = Math.min(...nodes.map((node: any) => node.y()));
		const right = Math.max(...nodes.map((node: any) => node.x() + node.width() * node.scaleX()));
		const center = (left + right) / 2;
		nodes.forEach((node: any) => node.position({ x: mode === 'left' ? left : mode === 'center' ? center - (node.width() * node.scaleX()) / 2 : node.x(), y: mode === 'top' ? top : node.y() }));
		(canvas as any)?.board?.stage?.draw(); record_history();
	};
	const distribute_selected = (axis: 'x' | 'y') => {
		const shapes = selected_shapes();
		if (shapes.length < 3) return;
		const nodes = shapes.map((shape: any) => shape.node).sort((a: any, b: any) => a[axis]() - b[axis]());
		const first = nodes[0][axis](); const last = nodes[nodes.length - 1][axis](); const step = (last - first) / (nodes.length - 1);
		nodes.forEach((node: any, index: number) => node[axis](first + step * index));
		(canvas as any)?.board?.stage?.draw(); record_history();
	};
	const copy_format = () => { if (selected_el) format_clipboard = { ...(selected_el.node.attrs ?? {}) }; };
	const paste_format = () => {
		if (!selected_el || !format_clipboard) return;
		const format = { ...format_clipboard };
		delete format.x; delete format.y; delete format.width; delete format.height; delete format.rotation;
		if (selected_el.type === 'label') selected_el.updateText(format as any); else selected_el.update(format as any);
		record_history();
	};
	const timeline_items = $derived(layer_models);
	const reorder_animation = (from: number, to: number) => {
		if (from === to || from < 0 || to < 0 || from >= layer_models.length || to >= layer_models.length) return;
		const next = [...layer_models];
		const [moved] = next.splice(from, 1);
		next.splice(to, 0, moved);
		layer_models = next;
		next.forEach((shape: any, index) => {
			if (shape.node?.attrs?.animation && shape.node.attrs.animation !== 'none') shape.update({ animationDelay: index * 180 } as any);
		});
		animation_drag_index = null;
		record_history();
	};
	const timeline_animation = (shape: any) => shape.node?.attrs?.animation ?? 'none';
	const timeline_label = (shape: any) => shape.type === 'label' ? String(shape.node?.children?.[1]?.attrs?.text ?? 'Text').slice(0, 26) : shape.type;

	let filtered_thesvg_icons = $derived.by(() => {
		if (!thesvg_search.trim()) return thesvg_icons.slice(0, 40);
		const q = thesvg_search.toLowerCase();
		return thesvg_icons
			.filter((icon) => {
				const title = (icon?.title ?? icon?.name ?? icon?.slug ?? '').toLowerCase();
				const tags = Array.isArray(icon?.tags) ? icon.tags.join(' ').toLowerCase() : '';
				return title.includes(q) || tags.includes(q);
			})
			.slice(0, 40);
	});

	run(() => {
		if (selected_element) {
			add_text_field();
		}
	});
	const assign_resize_handlers = () => {
		for (let i = 0; i < elements_binds.length; i++) {
			set_correct_height.observe(elements_binds[i]);
		}
	};

	/*	if (data.answers.length !== 0) {
			for (let i = 0; i < data.answers.length; i++) {
				data.answers[i].width = data.answers[i].width * main_el.offsetWidth;
				data.answers[i].height = data.answers[i].height * main_el.offsetHeight;
			}
		}*/

	run(() => {
		elements_binds;
		assign_resize_handlers();
	});

	onMount(() => {
		/*		setTimeout(() => {
					for (let i = 0; i < data.answers.length; i++) {
						elements_binds[i].style.height = `${
							data.answers[i].height * main_el.offsetHeight
						}px`;
						elements_binds[i].style.width = `${data.answers[i].width * main_el.offsetWidth}px`;
					}
				}, 200);*/
		canvas = new Pikaso({
			container: canvas_el,
			snapToGrid: {},
			/*			transformer: {
							borderStroke: "#00ff00",
							anchorStroke: "#00ff00"
						},
						cropper: {
							transformer: {
								borderStroke: "#00ff00",
								// anchorFill: "#00ff00",
								anchorStroke: "#00ff00"
							},
							guides: {
								color: "#00ff00"
							}
						},*/
			selection: {
				transformer: {
					borderStroke: darkMode ? '#fff' : '#000000',
					anchorStroke: darkMode ? '#fff' : '#000000'
				}
			}
			/*			selection: {
							interactive: false
						}*/
		});
		if (data.answers) {
			if (typeof data.answers === 'string') {
				canvas.import.json(JSON.parse(data.answers));
			}
		}
		canvas.on('*', () => {
			data.answers = JSON.stringify(canvas.export.toJson());
			record_history();
		sync_layers();
		});
		canvas.on('selection:change', (data) => {
			/*			data.shapes[0].update({fill: "#ffffff"})
						console.log(data.shapes[0])*/
			// console.log(canvas.board.shapes)
			if (data.shapes.length > 0) {
				selected_el = data.shapes[0];
			} else {
				selected_el = null;
			}
		});
		record_history();
		sync_layers();
	});
</script>

<div class="flex h-full relative w-full" bind:this={main_el} style:background-color={master_theme?.background_color ?? '#ffffff'} style:color={master_theme?.text_color ?? '#0f172a'} style:font-family={master_theme?.font_family ?? 'Inter, sans-serif'}>
	<div class="absolute top-0 left-0 grid grid-cols-6 w-full">
		<div class="flex flex-col pl-2 rounded-t-lg z-40 pt-2">
			<button
				class="mr-auto"
				onclick={() => {
					settings_menu_open = !settings_menu_open;
				}}
				type="button"
			>
				<svg
					class="w-6 h-6"
					stroke-width="2"
					viewBox="0 0 24 24"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
					color="currentColor"
				>
					<path
						d="M12 15a3 3 0 100-6 3 3 0 000 6z"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
					<path
						d="M19.622 10.395l-1.097-2.65L20 6l-2-2-1.735 1.483-2.707-1.113L12.935 2h-1.954l-.632 2.401-2.645 1.115L6 4 4 6l1.453 1.789-1.08 2.657L2 11v2l2.401.655L5.516 16.3 4 18l2 2 1.791-1.46 2.606 1.072L11 22h2l.604-2.387 2.651-1.098C16.697 18.831 18 20 18 20l2-2-1.484-1.75 1.098-2.652 2.386-.62V11l-2.378-.605z"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
				</svg>
			</button>
			<button type="button" class="mt-2 mr-auto rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs font-semibold text-slate-600 shadow-sm hover:border-teal-300 hover:text-teal-700" onclick={() => image_input?.click()}>Add image</button>
			<input bind:this={image_input} class="hidden" type="file" accept="image/*" onchange={async (event) => { const file = event.currentTarget.files?.[0]; if (file) await upload_image_file(file); event.currentTarget.value = ''; }} />
			{#if settings_menu_open}
				<SettingsMenu bind:time={data.time} bind:title={data.question} bind:animation={data.animation} />
			{/if}
			<button
				class="mt-2 mr-auto rounded border border-gray-500 bg-white/80 px-2 py-1 text-xs dark:bg-gray-700/80"
				onclick={async () => {
					thesvg_open = !thesvg_open;
					if (thesvg_open && thesvg_icons.length === 0) {
						await load_thesvg_registry();
					}
				}}
				type="button"
			>
				SVG Bank
			</button>
			{#if thesvg_open}
				<div class="mt-2 w-64 rounded-lg border border-gray-300 bg-white p-2 shadow-xl dark:bg-gray-700 dark:border-gray-500">
					<input
						type="text"
						placeholder="Search SVGs"
						bind:value={thesvg_search}
						class="w-full rounded border border-gray-300 p-1 text-xs dark:bg-gray-600"
					/>
					<div class="mt-2 max-h-64 overflow-y-auto space-y-1">
						{#if thesvg_loading}
							<p class="text-xs text-gray-500">Loading...</p>
						{:else}
							{#each filtered_thesvg_icons as icon}
								<button
									type="button"
									draggable="true"
									ondragstart={(event) => event.dataTransfer?.setData('application/x-cyberask-svg', icon?.slug ?? icon?.id ?? icon?.name ?? '')}
									class="w-full rounded border border-gray-200 px-2 py-1 text-left text-xs hover:bg-gray-100 dark:border-gray-500 dark:hover:bg-gray-600"
									onclick={() => insert_thesvg(icon)}
								>
									<div class="flex items-center gap-2">
										<img src={icon.preview_url ?? thesvg_icon_url(icon)} alt="icon" class="h-6 w-6 object-contain" />
										<span class="truncate">{icon?.title ?? icon?.name ?? icon?.slug ?? 'Icon'}</span>
									</div>
								</button>
							{/each}
						{/if}
					</div>
				</div>
			{/if}
		</div>
		<div class="col-start-2 col-end-6 transition bg-transparent pt-2">
			<div class="mb-1 flex items-center justify-center gap-1"><button type="button" class="rounded-lg border border-slate-200 bg-white px-2 py-1 text-[11px] font-semibold text-slate-600 shadow-sm disabled:opacity-40" title="Undo" onclick={undo} disabled={history_index <= 0}>↶ Undo</button><button type="button" class="rounded-lg border border-slate-200 bg-white px-2 py-1 text-[11px] font-semibold text-slate-600 shadow-sm disabled:opacity-40" title="Redo" onclick={redo} disabled={history_index < 0 || history_index >= history_stack.length - 1}>Redo ↷</button><button type="button" class="rounded-lg border border-slate-200 bg-white px-2 py-1 text-[11px] font-semibold text-slate-600 shadow-sm" onclick={() => (history_open = !history_open)}>History</button></div>
			<div class="mb-1 flex justify-center"><button type="button" class="rounded-lg border border-slate-200 bg-white px-3 py-1 text-[11px] font-semibold text-slate-600 shadow-sm hover:border-teal-300 hover:text-teal-700" onclick={() => (animation_timeline_open = !animation_timeline_open)}>Animation timeline · {timeline_items.filter((shape: any) => timeline_animation(shape) !== 'none').length}</button></div>
			<EditMenu bind:selected_el />
			{#if history_open}<div class="mx-auto mt-1 max-w-xs rounded-xl border border-slate-200 bg-white p-2 text-[10px] shadow-lg"><p class="font-bold text-slate-500">Edit history · {history_stack.length} states</p><p class="mt-1 text-slate-400">Use Undo/Redo to move through the current slide history.</p></div>{/if}
		</div>

		<div class="flex flex-col pr-2 rounded-t-lg z-40 pt-2">
			<button
				class="ml-auto"
				onclick={() => {
					selected_element = selected_element === null ? undefined : null;
				}}
				type="button"
				class:add-button={selected_element === null}
			>
				<svg
					class="w-6 h-6"
					stroke-width="2"
					viewBox="0 0 24 24"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
					color="currentColor"
				>
					<path
						d="M9 12h3m3 0h-3m0 0V9m0 3v3M21 3.6v16.8a.6.6 0 01-.6.6H3.6a.6.6 0 01-.6-.6V3.6a.6.6 0 01.6-.6h16.8a.6.6 0 01.6.6z"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
				</svg>
			</button>
			{#if selected_element === null}
				<ElementSelection bind:selected_element />
			{/if}
			<button type="button" class="mt-2 ml-auto rounded-lg border border-slate-200 bg-white px-2 py-1 text-[10px] font-semibold text-slate-600 shadow-sm hover:border-teal-300 hover:text-teal-700" onclick={() => (properties_open = !properties_open)}>Layers</button>
		</div>
	</div>
	{#if animation_timeline_open}
		<div class="absolute left-3 top-14 z-50 w-80 rounded-2xl border border-slate-200 bg-white/95 p-3 shadow-xl backdrop-blur"><div class="flex items-center justify-between"><div><p class="text-[10px] font-bold uppercase tracking-[0.16em] text-teal-600">Animation timeline</p><p class="mt-1 text-xs text-slate-500">Drag to reorder the reveal sequence.</p></div><button type="button" class="rounded-lg p-1 text-slate-400 hover:bg-slate-100" aria-label="Close animation timeline" onclick={() => (animation_timeline_open = false)}>×</button></div><div class="mt-3 space-y-1.5">{#each timeline_items as shape, index}<button type="button" draggable="true" class="flex w-full items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-2.5 py-2 text-left hover:border-teal-300 hover:bg-teal-50/40 {animation_drag_index === index ? 'opacity-40' : ''}" ondragstart={() => (animation_drag_index = index)} ondragover={(event) => event.preventDefault()} ondrop={() => animation_drag_index !== null && reorder_animation(animation_drag_index, index)} onclick={() => shape.select?.()}><span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-white text-[10px] font-bold text-slate-500">{index + 1}</span><span class="min-w-0 flex-1 truncate text-xs font-semibold text-slate-700">{timeline_label(shape)}</span><select aria-label="Animation trigger" class="rounded border border-slate-200 bg-white px-1 py-1 text-[10px]" value={shape.node?.attrs?.animationTrigger ?? 'auto'} onchange={(event) => { event.stopPropagation(); shape.update({ animationTrigger: event.currentTarget.value } as any); record_history(); }}><option value="auto">Auto</option><option value="click">Click</option></select><select aria-label="Animation type" class="w-20 rounded border border-slate-200 bg-white px-1 py-1 text-[10px]" value={timeline_animation(shape)} onchange={(event) => { event.stopPropagation(); shape.update({ animation: event.currentTarget.value } as any); record_history(); }}><option value="none">None</option><option value="fade">Fade</option><option value="rise">Rise</option><option value="zoom">Zoom</option><option value="slide-left">Slide</option></select></button>{:else}<p class="rounded-lg bg-slate-50 p-3 text-xs text-slate-500">Add animations from the formatting toolbar to build a sequence.</p>{/each}</div></div>
	{/if}
	{#if properties_open && !selected_el && layer_models.length}
		<div class="absolute right-3 top-14 z-40 w-64 rounded-2xl border border-slate-200 bg-white/95 p-3 shadow-xl backdrop-blur"><p class="text-[10px] font-bold uppercase tracking-[0.16em] text-teal-600">Layer panel</p><div class="mt-2 max-h-64 space-y-1 overflow-y-auto">{#each layer_models as shape, index}<button type="button" class="flex w-full items-center justify-between rounded-lg border border-slate-100 px-3 py-2 text-left text-xs hover:bg-slate-50" onclick={() => select_layer(shape)}><span class="truncate">{shape.type === 'label' ? 'Text' : shape.type} {layer_models.length - index}</span><span class="text-[10px] text-slate-400">{shape.group ? 'Group' : ''}</span></button>{/each}</div></div>
	{/if}
	{#if selected_el}
		<div class="absolute right-3 top-14 z-40 w-64 rounded-2xl border border-slate-200 bg-white/95 p-4 shadow-xl shadow-slate-900/10 backdrop-blur" class:hidden={!properties_open}>
			<div class="flex items-start justify-between gap-3"><div><p class="text-[10px] font-bold uppercase tracking-[0.16em] text-teal-600">Selected element</p><h3 class="mt-1 text-sm font-bold text-slate-900">{selected_el.type === 'label' ? 'Text box' : selected_el.type}</h3></div><button type="button" class="rounded-lg p-1 text-slate-400 hover:bg-slate-100" aria-label="Close properties" onclick={() => (properties_open = false)}>×</button></div>
			<div class="mt-4 grid grid-cols-2 gap-2">
				<label class="text-[11px] font-semibold text-slate-500">X<input class="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-xs" type="number" value={selected_attrs?.x ?? 0} onchange={(e) => update_geometry('x', e.currentTarget.value)} /></label>
				<label class="text-[11px] font-semibold text-slate-500">Y<input class="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-xs" type="number" value={selected_attrs?.y ?? 0} onchange={(e) => update_geometry('y', e.currentTarget.value)} /></label>
				<label class="text-[11px] font-semibold text-slate-500">Width<input class="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-xs" type="number" min="1" value={selected_attrs?.width ?? ''} onchange={(e) => update_geometry('width', e.currentTarget.value)} /></label>
				<label class="text-[11px] font-semibold text-slate-500">Height<input class="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-xs" type="number" min="1" value={selected_attrs?.height ?? ''} onchange={(e) => update_geometry('height', e.currentTarget.value)} /></label>
				<label class="text-[11px] font-semibold text-slate-500">Rotation<input class="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-xs" type="number" min="-360" max="360" value={selected_attrs?.rotation ?? 0} onchange={(e) => update_geometry('rotation', e.currentTarget.value)} /></label>
				<label class="text-[11px] font-semibold text-slate-500">Opacity<input class="mt-2 w-full" type="range" min="0.1" max="1" step="0.05" value={selected_attrs?.opacity ?? 1} oninput={(e) => update_geometry('opacity', e.currentTarget.value)} /></label>
			</div>
			<label class="mt-3 block text-[11px] font-semibold text-slate-500">Fill / text colour<input class="mt-1 h-9 w-full rounded-lg border border-slate-200 p-1" type="color" value={selected_attrs?.fill ?? '#0f766e'} onchange={update_selected_fill} /></label>
			<div class="mt-3 grid grid-cols-2 gap-2"><button type="button" class="rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-[11px] font-semibold text-slate-600 hover:border-teal-300" onclick={duplicate_selected}>Duplicate</button><button type="button" class="rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-[11px] font-semibold text-slate-600 hover:border-teal-300" onclick={toggle_lock}>{locked_elements.has(selected_el.node) ? 'Unlock' : 'Lock'}</button><button type="button" class="rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-[11px] font-semibold text-slate-600 hover:border-teal-300" onclick={group_selected}>Group selected</button><button type="button" class="rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-[11px] font-semibold text-slate-600 hover:border-teal-300" onclick={ungroup_selected} disabled={!selected_el.group}>Ungroup</button></div>
			<div class="mt-3 border-t border-slate-100 pt-3"><p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Layout tools · multi-select with Shift</p><div class="mt-2 grid grid-cols-3 gap-1"><button type="button" class="rounded border border-slate-200 px-1 py-1 text-[10px] text-slate-600 hover:border-teal-300" onclick={() => align_selected('left')}>Align left</button><button type="button" class="rounded border border-slate-200 px-1 py-1 text-[10px] text-slate-600 hover:border-teal-300" onclick={() => align_selected('center')}>Centre</button><button type="button" class="rounded border border-slate-200 px-1 py-1 text-[10px] text-slate-600 hover:border-teal-300" onclick={() => align_selected('top')}>Align top</button><button type="button" class="rounded border border-slate-200 px-1 py-1 text-[10px] text-slate-600 hover:border-teal-300" onclick={() => distribute_selected('x')}>Space X</button><button type="button" class="rounded border border-slate-200 px-1 py-1 text-[10px] text-slate-600 hover:border-teal-300" onclick={() => distribute_selected('y')}>Space Y</button><button type="button" class="rounded border border-slate-200 px-1 py-1 text-[10px] text-slate-600 hover:border-teal-300" onclick={copy_format}>Copy style</button></div><button type="button" class="mt-1 w-full rounded border border-slate-200 px-1 py-1 text-[10px] text-slate-600 hover:border-teal-300 disabled:opacity-40" onclick={paste_format} disabled={!format_clipboard}>Paste style</button></div>
			{#if selected_el.type === 'label'}<div class="mt-3 grid grid-cols-2 gap-2"><label class="text-[11px] font-semibold text-slate-500">Line spacing<input class="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-xs" type="number" min="0.5" max="3" step="0.1" value={selected_attrs?.lineHeight ?? 1.2} onchange={(e) => selected_el?.updateText({ lineHeight: Number(e.currentTarget.value) || 1.2 } as any)} /></label><label class="text-[11px] font-semibold text-slate-500">Text padding<input class="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-xs" type="number" min="0" max="80" value={selected_attrs?.padding ?? 0} onchange={(e) => selected_el?.updateText({ padding: Number(e.currentTarget.value) || 0 } as any)} /></label></div>{/if}
			<div class="mt-3 grid grid-cols-2 gap-2"><label class="text-[11px] font-semibold text-slate-500">Border<input class="mt-1 h-8 w-full rounded-lg border border-slate-200 p-1" type="color" value={selected_attrs?.stroke ?? '#cbd5e1'} onchange={(e) => selected_el?.update({ stroke: e.currentTarget.value, strokeWidth: selected_attrs?.strokeWidth ?? 1 } as any)} /></label><label class="text-[11px] font-semibold text-slate-500">Border px<input class="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-xs" type="number" min="0" max="20" value={selected_attrs?.strokeWidth ?? 0} onchange={(e) => selected_el?.update({ strokeWidth: Number(e.currentTarget.value) || 0 } as any)} /></label></div>
			<label class="mt-3 flex items-center gap-2 text-[11px] font-semibold text-slate-500"><input type="checkbox" checked={Boolean(selected_attrs?.shadowBlur)} onchange={(e) => selected_el?.update({ shadowBlur: e.currentTarget.checked ? 12 : 0, shadowColor: '#0f172a', shadowOpacity: 0.18 } as any)} /> Soft shadow</label>
			<p class="mt-3 rounded-lg bg-slate-50 px-3 py-2 text-[11px] leading-5 text-slate-500">Drag the selected element on the canvas for quick positioning. Use these fields for precise layout.</p>
		</div>
		{#if !properties_open}<button type="button" class="absolute right-3 top-14 z-30 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 shadow-lg hover:border-teal-300 hover:text-teal-700" onclick={() => (properties_open = true)}>Properties</button>{/if}
	{/if}
	<div bind:this={canvas_el} class="w-full h-full block" ondragover={(event) => event.preventDefault()} ondrop={drop_svg}></div>
</div>
