<!--
SPDX-FileCopyrightText: 2025

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question, Answer } from '$lib/quiz_types';
	import { onMount } from 'svelte';

	interface Props {
		questions: Question[];
		selected_question: number;
	}

	let { questions, selected_question }: Props = $props();

	let panel_open = $state(false);

	// â”€â”€ Persisted geometry â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	const STORAGE_KEY = 'branchmap_geometry';
	interface Geometry { x: number; y: number; w: number; h: number }

	const load_geometry = (): Geometry => {
		if (typeof localStorage === 'undefined') return { x: 40, y: 80, w: 420, h: 540 };
		try {
			const v = localStorage.getItem(STORAGE_KEY);
			if (v) return JSON.parse(v);
		} catch { /* ignore */ }
		return { x: 40, y: 80, w: 420, h: 540 };
	};
	const save_geometry = () => localStorage.setItem(STORAGE_KEY, JSON.stringify(geo));

	let geo = $state<Geometry>(load_geometry());

	onMount(() => {
		// Clamp initial geometry inside viewport
		const W = window.innerWidth;
		const H = window.innerHeight;
		geo.w = Math.min(geo.w, W - 16);
		geo.h = Math.min(geo.h, H - 40);
		geo.x = Math.max(0, Math.min(geo.x, W - geo.w - 4));
		geo.y = Math.max(0, Math.min(geo.y, H - 60));
	});

	// â”€â”€ Dragging (header) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	let drag_off = { ox: 0, oy: 0 };

	function drag_start(e: MouseEvent) {
		if ((e.target as HTMLElement).closest('button')) return;
		e.preventDefault();
		drag_off = { ox: e.clientX - geo.x, oy: e.clientY - geo.y };
		window.addEventListener('mousemove', drag_move);
		window.addEventListener('mouseup', drag_end, { once: true });
	}
	function drag_move(e: MouseEvent) {
		const W = window.innerWidth;
		const H = window.innerHeight;
		geo.x = Math.max(0, Math.min(e.clientX - drag_off.ox, W - geo.w - 4));
		geo.y = Math.max(0, Math.min(e.clientY - drag_off.oy, H - 40));
	}
	function drag_end() {
		save_geometry();
		window.removeEventListener('mousemove', drag_move);
	}

	// â”€â”€ Resizing (SE corner handle) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	let rs = { mx: 0, my: 0, w: 0, h: 0 };

	function resize_start(e: MouseEvent) {
		e.preventDefault();
		e.stopPropagation();
		rs = { mx: e.clientX, my: e.clientY, w: geo.w, h: geo.h };
		window.addEventListener('mousemove', resize_move);
		window.addEventListener('mouseup', resize_end, { once: true });
	}
	function resize_move(e: MouseEvent) {
		geo.w = Math.max(280, rs.w + (e.clientX - rs.mx));
		geo.h = Math.max(200, rs.h + (e.clientY - rs.my));
	}
	function resize_end() {
		save_geometry();
		window.removeEventListener('mousemove', resize_move);
	}

	// â”€â”€ Graph data model â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	const id_to_index = $derived(new Map(questions.map((q, i) => [q.id, i])));

	const truncate = (text: string, max = 28) => {
		const clean = text.replace(/<[^>]*>/g, '').trim();
		return clean.length > max ? clean.slice(0, max) + 'â€¦' : clean;
	};

	interface MapNode { index: number; label: string; x: number; y: number }
	interface MapEdge { from: number; to: number; label: string; color: string; dashed: boolean }

	const NODE_W = 200;
	const NODE_H = 50;
	const GAP_Y = 30;
	const GAP_X = 70;

	const COLORS = ['#0d9488','#6366f1','#e11d48','#f59e0b','#8b5cf6','#06b6d4','#22c55e','#f43f5e'];

	const layout = $derived.by(() => {
		if (!questions.length) return { nodes: [], edges: [], cols: 0 };

		// col[i] = layout column (0 = main, 1 = branch lane etc.)
		const col = new Array(questions.length).fill(0);

		for (let i = 0; i < questions.length; i++) {
			const q = questions[i];
			const answers = Array.isArray(q.answers) ? q.answers as Answer[] : [];
			for (const a of answers) {
				if (a.next_question_id) {
					const ti = id_to_index.get(a.next_question_id);
					if (ti !== undefined && ti > i + 1 && col[ti] === 0) col[ti] = 1;
				}
			}
			if (q.default_next_question_id) {
				const ti = id_to_index.get(q.default_next_question_id);
				if (ti !== undefined && ti > i + 1 && col[ti] === 0) col[ti] = 1;
			}
		}

		const max_col = Math.max(...col);
		const nodes: MapNode[] = questions.map((q, i) => ({
			index: i,
			label: truncate(q.question),
			x: 20 + col[i] * (NODE_W + GAP_X),
			y: 20 + i * (NODE_H + GAP_Y)
		}));

		const edges: MapEdge[] = [];
		for (let i = 0; i < questions.length; i++) {
			const q = questions[i];
			const answers = Array.isArray(q.answers) ? q.answers as Answer[] : [];
			let has_explicit = false;

			answers.forEach((a, ai) => {
				if (a.next_question_id) {
					const ti = id_to_index.get(a.next_question_id);
					if (ti !== undefined) {
						edges.push({ from: i, to: ti, label: truncate(a.answer, 16), color: COLORS[ai % COLORS.length], dashed: false });
						has_explicit = true;
					}
				}
			});

			if (q.default_next_question_id) {
				const ti = id_to_index.get(q.default_next_question_id);
				if (ti !== undefined) {
					edges.push({ from: i, to: ti, label: 'default', color: '#6b7280', dashed: false });
					has_explicit = true;
				}
			}

			if (!has_explicit && i < questions.length - 1) {
				edges.push({ from: i, to: i + 1, label: '', color: '#d1d5db', dashed: true });
			}
		}

		return { nodes, edges, cols: max_col };
	});

	const SVG_W = $derived(20 + (layout.cols + 1) * (NODE_W + GAP_X) + 30);
	const SVG_H = $derived(20 + questions.length * (NODE_H + GAP_Y) + 20);

	function edge_path(from: MapNode, to: MapNode) {
		const x1 = from.x + NODE_W / 2;
		const y1 = from.y + NODE_H;
		const x2 = to.x + NODE_W / 2;
		const y2 = to.y;
		if (to.index <= from.index) {
			const lx = Math.min(from.x, to.x) - 40;
			return `M ${x1} ${y1} C ${lx} ${y1 + 30}, ${lx} ${y2 - 30}, ${x2} ${y2}`;
		}
		const my = (y1 + y2) / 2;
		return `M ${x1} ${y1} C ${x1} ${my}, ${x2} ${my}, ${x2} ${y2}`;
	}

	function label_pos(from: MapNode, to: MapNode) {
		return {
			x: (from.x + NODE_W / 2 + to.x + NODE_W / 2) / 2,
			y: (from.y + NODE_H + to.y) / 2
		};
	}
</script>

<!-- â”€â”€ Toggle button (fixed bottom-right) â”€â”€ -->
<button
	class="fixed right-4 bottom-4 z-50 flex items-center gap-2 rounded-full bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg hover:bg-indigo-700 transition select-none"
	onclick={() => { panel_open = !panel_open; }}
	title="Toggle branch map"
>
	<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
		<path stroke-linecap="round" stroke-linejoin="round" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
	</svg>
	{panel_open ? 'Hide Map' : 'Branch Map'}
</button>

{#if panel_open}
	<!-- â”€â”€ Floating window â”€â”€ -->
	<div
		class="fixed z-[60] flex flex-col rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 shadow-2xl overflow-hidden select-none"
		style="left:{geo.x}px; top:{geo.y}px; width:{geo.w}px; height:{geo.h}px"
	>
		<!-- Header (drag handle) -->
		<div
			class="flex items-center justify-between px-4 py-2.5 bg-indigo-600 text-white cursor-move shrink-0"
			role="toolbar"
			tabindex="-1"
			onmousedown={drag_start}
		>
			<span class="text-sm font-bold uppercase tracking-wide pointer-events-none">Branch Map</span>
			<div class="flex items-center gap-2">
				<span class="text-[10px] text-white/60 pointer-events-none">{questions.length} questions</span>
				<button
					class="text-white/80 hover:text-white text-xl leading-none cursor-pointer"
					onclick={() => { panel_open = false; }}
				>&times;</button>
			</div>
		</div>

		<!-- Legend -->
		<div class="flex flex-wrap gap-x-4 gap-y-1 px-4 py-1.5 border-b border-gray-100 dark:border-gray-700 text-[10px] text-gray-500 dark:text-gray-400 shrink-0">
			<span class="flex items-center gap-1">
				<span class="inline-block w-3 h-3 rounded bg-teal-100 border-2 border-teal-600"></span>Current
			</span>
			<span class="flex items-center gap-1">
				<span class="inline-block w-3 h-3 rounded bg-gray-100 dark:bg-gray-700 border border-gray-400"></span>Question
			</span>
			<span class="flex items-center gap-1">
				<span class="inline-block w-4 h-0.5 bg-teal-500"></span>Branch
			</span>
			<span class="flex items-center gap-1">
				<span class="inline-block w-4 h-px border-t border-dashed border-gray-400"></span>Sequential
			</span>
		</div>

		<!-- Scrollable SVG area -->
		<div class="flex-1 overflow-auto p-1">
			<svg width={SVG_W} height={SVG_H}>
				<defs>
					<marker id="bm-arr" markerWidth="7" markerHeight="5" refX="7" refY="2.5" orient="auto">
						<polygon points="0 0,7 2.5,0 5" fill="#9ca3af" />
					</marker>
					<marker id="bm-arr-b" markerWidth="7" markerHeight="5" refX="7" refY="2.5" orient="auto">
						<polygon points="0 0,7 2.5,0 5" fill="#0d9488" />
					</marker>
				</defs>

				<!-- Edges -->
				{#each layout.edges as edge}
					{@const fn = layout.nodes[edge.from]}
					{@const tn = layout.nodes[edge.to]}
					<path
						d={edge_path(fn, tn)}
						fill="none"
						stroke={edge.color}
						stroke-width={edge.dashed ? 1.5 : 2}
						stroke-dasharray={edge.dashed ? '5 3' : 'none'}
						marker-end={edge.dashed ? 'url(#bm-arr)' : 'url(#bm-arr-b)'}
						opacity="0.75"
					/>
					{#if edge.label}
						{@const lp = label_pos(fn, tn)}
						<rect x={lp.x - 32} y={lp.y - 7} width="64" height="14" rx="3"
							fill="white" stroke={edge.color} stroke-width="0.5" opacity="0.95"
						/>
						<text x={lp.x} y={lp.y + 4} text-anchor="middle" font-size="8"
							fill={edge.color} font-weight="600">{edge.label}</text>
					{/if}
				{/each}

				<!-- Nodes -->
				{#each layout.nodes as node}
					{@const is_curr = node.index === selected_question}
					{@const is_past = node.index < selected_question}
					<rect x={node.x} y={node.y} width={NODE_W} height={NODE_H} rx="8"
						fill={is_curr ? '#ccfbf1' : is_past ? '#f3f4f6' : 'white'}
						stroke={is_curr ? '#0d9488' : is_past ? '#9ca3af' : '#d1d5db'}
						stroke-width={is_curr ? 2.5 : 1}
					/>
					<!-- Badge -->
					<circle cx={node.x + 18} cy={node.y + NODE_H / 2} r="11"
						fill={is_curr ? '#0d9488' : is_past ? '#9ca3af' : '#e5e7eb'}
					/>
					<text x={node.x + 18} y={node.y + NODE_H / 2 + 4}
						text-anchor="middle" font-size="10" font-weight="bold"
						fill={is_curr || is_past ? 'white' : '#374151'}
					>{node.index + 1}</text>
					<!-- Label -->
					<text x={node.x + 36} y={node.y + NODE_H / 2 + 4}
						font-size="10" fill={is_past ? '#9ca3af' : '#1f2937'}
						font-weight={is_curr ? '600' : '400'}
					>{node.label}</text>
					<!-- Pulse on current -->
					{#if is_curr}
						<circle cx={node.x + NODE_W - 12} cy={node.y + NODE_H / 2} r="4" fill="#0d9488">
							<animate attributeName="r" values="4;7;4" dur="1.6s" repeatCount="indefinite"/>
							<animate attributeName="opacity" values="1;0.4;1" dur="1.6s" repeatCount="indefinite"/>
						</circle>
					{/if}
				{/each}
			</svg>
		</div>

		<!-- SE resize handle -->
		<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
		<div
			class="absolute bottom-0 right-0 w-5 h-5 cursor-se-resize"
			role="separator"
			tabindex="-1"
			onmousedown={resize_start}
		>
			<svg viewBox="0 0 12 12" class="w-full h-full text-gray-400 dark:text-gray-500">
				<path d="M10 2 L10 10 L2 10" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
				<path d="M6 6 L10 10" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
			</svg>
		</div>
	</div>
{/if}
