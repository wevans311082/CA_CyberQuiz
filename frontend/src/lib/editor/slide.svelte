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
	let selected_el: null | ShapeModel<Konva.Shape | Konva.Group, Konva.ShapeConfig> = $state(null);
	let properties_open = $state(false);

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
			<EditMenu bind:selected_el />
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
		</div>
	</div>
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
			<p class="mt-3 rounded-lg bg-slate-50 px-3 py-2 text-[11px] leading-5 text-slate-500">Drag the selected element on the canvas for quick positioning. Use these fields for precise layout.</p>
		</div>
		{#if !properties_open}<button type="button" class="absolute right-3 top-14 z-30 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 shadow-lg hover:border-teal-300 hover:text-teal-700" onclick={() => (properties_open = true)}>Properties</button>{/if}
	{/if}
	<div bind:this={canvas_el} class="w-full h-full block" ondragover={(event) => event.preventDefault()} ondrop={drop_svg}></div>
</div>
