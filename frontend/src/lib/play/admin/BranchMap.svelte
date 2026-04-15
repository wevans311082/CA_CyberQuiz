<!--
SPDX-FileCopyrightText: 2025

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question, Answer } from '$lib/quiz_types';
	import { fly } from 'svelte/transition';

	interface Props {
		questions: Question[];
		selected_question: number;
	}

	let { questions, selected_question }: Props = $props();

	let panel_open = $state(false);

	// Build a map of id -> index for quick lookup
	const id_to_index = $derived(
		new Map(questions.map((q, i) => [q.id, i]))
	);

	// Truncate question text to a short label
	const truncate = (text: string, max: number = 28) => {
		const clean = text.replace(/<[^>]*>/g, '').trim();
		return clean.length > max ? clean.slice(0, max) + '…' : clean;
	};

	interface MapNode {
		index: number;
		id: string | undefined;
		label: string;
		x: number;
		y: number;
	}

	interface MapEdge {
		from_index: number;
		to_index: number;
		label: string;
		color: string;
		is_default: boolean;
	}

	// Layout: compute nodes and edges
	const NODE_W = 180;
	const NODE_H = 48;
	const GAP_X = 60;
	const GAP_Y = 28;

	// Compute graph layout. Questions placed top-to-bottom with branching
	// targets shown as edges. Layout uses a simple column-based approach.
	const layout = $derived.by(() => {
		const nodes: MapNode[] = [];
		const edges: MapEdge[] = [];
		const edge_colors = ['#0d9488', '#6366f1', '#e11d48', '#f59e0b', '#8b5cf6', '#06b6d4', '#22c55e', '#f43f5e'];

		// Assign column per question (try to keep branching targets right)
		// Simple layout: sequential column 0, targets that branch reuse index
		const col = new Map<number, number>();
		const row = new Map<number, number>();
		let max_col = 0;

		// First pass: sequential placement
		for (let i = 0; i < questions.length; i++) {
			col.set(i, 0);
			row.set(i, i);
		}

		// Second pass: move branch targets into offset columns if they break sequence
		for (let i = 0; i < questions.length; i++) {
			const q = questions[i];
			const answers = Array.isArray(q.answers) ? q.answers as Answer[] : [];
			for (const a of answers) {
				if (a.next_question_id) {
					const ti = id_to_index.get(a.next_question_id);
					if (ti !== undefined && ti !== i + 1) {
						// Non-sequential branch — put branch source in col 0
						// If target is backwards (loop), keep it at col 0
						if (ti > i && col.get(ti) === 0) {
							col.set(ti, 1);
							max_col = Math.max(max_col, 1);
						}
					}
				}
			}
			if (q.default_next_question_id) {
				const ti = id_to_index.get(q.default_next_question_id);
				if (ti !== undefined && ti !== i + 1) {
					if (ti > i && col.get(ti) === 0) {
						col.set(ti, 1);
						max_col = Math.max(max_col, 1);
					}
				}
			}
		}

		// Build map nodes
		for (let i = 0; i < questions.length; i++) {
			const c = col.get(i) ?? 0;
			const r = row.get(i) ?? i;
			nodes.push({
				index: i,
				id: questions[i].id,
				label: truncate(questions[i].question),
				x: 20 + c * (NODE_W + GAP_X),
				y: 20 + r * (NODE_H + GAP_Y)
			});
		}

		// Build edges
		for (let i = 0; i < questions.length; i++) {
			const q = questions[i];
			const answers = Array.isArray(q.answers) ? q.answers as Answer[] : [];
			let has_branch = false;

			for (let ai = 0; ai < answers.length; ai++) {
				const a = answers[ai];
				if (a.next_question_id) {
					const ti = id_to_index.get(a.next_question_id);
					if (ti !== undefined) {
						edges.push({
							from_index: i,
							to_index: ti,
							label: truncate(a.answer, 18),
							color: edge_colors[ai % edge_colors.length],
							is_default: false
						});
						has_branch = true;
					}
				}
			}

			if (q.default_next_question_id) {
				const ti = id_to_index.get(q.default_next_question_id);
				if (ti !== undefined) {
					edges.push({
						from_index: i,
						to_index: ti,
						label: 'default',
						color: '#6b7280',
						is_default: true
					});
					has_branch = true;
				}
			}

			// Implicit sequential link (no branch = goes to next question)
			if (!has_branch && i < questions.length - 1) {
				edges.push({
					from_index: i,
					to_index: i + 1,
					label: '',
					color: '#d1d5db',
					is_default: true
				});
			}
		}

		return { nodes, edges, max_col };
	});

	const svg_width = $derived(20 + (layout.max_col + 1) * (NODE_W + GAP_X) + 40);
	const svg_height = $derived(20 + questions.length * (NODE_H + GAP_Y) + 20);

	// Edge path from node bottom-center to target node top-center
	const edgePath = (fromNode: MapNode, toNode: MapNode) => {
		const x1 = fromNode.x + NODE_W / 2;
		const y1 = fromNode.y + NODE_H;
		const x2 = toNode.x + NODE_W / 2;
		const y2 = toNode.y;

		// Backwards link (loop) — curve to the left
		if (toNode.index <= fromNode.index) {
			const leftX = Math.min(fromNode.x, toNode.x) - 40;
			return `M ${x1} ${y1} C ${leftX} ${y1 + 30}, ${leftX} ${y2 - 30}, ${x2} ${y2}`;
		}

		// Forward link — gentle S-curve
		const midY = (y1 + y2) / 2;
		return `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`;
	};

	// Arrow marker placement: point at which the path ends
	const edgeLabelPos = (fromNode: MapNode, toNode: MapNode) => {
		return {
			x: (fromNode.x + NODE_W / 2 + toNode.x + NODE_W / 2) / 2,
			y: (fromNode.y + NODE_H + toNode.y) / 2
		};
	};
</script>

<!-- Toggle button -->
<button
	class="fixed right-4 bottom-4 z-50 flex items-center gap-2 rounded-full bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg hover:bg-indigo-700 transition"
	onclick={() => { panel_open = !panel_open; }}
	title="Toggle branch map"
>
	<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
		<path stroke-linecap="round" stroke-linejoin="round" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
	</svg>
	{panel_open ? 'Hide Map' : 'Branch Map'}
</button>

{#if panel_open}
	<div
		class="fixed right-0 top-0 z-40 h-full w-80 bg-white shadow-2xl dark:bg-gray-900 flex flex-col border-l border-gray-200 dark:border-gray-700"
		transition:fly={{ x: 320, duration: 200 }}
	>
		<!-- Header -->
		<div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-indigo-600 text-white">
			<h2 class="text-sm font-bold uppercase tracking-wider">Branch Map</h2>
			<button
				onclick={() => { panel_open = false; }}
				class="text-white/80 hover:text-white text-xl leading-none"
			>&times;</button>
		</div>

		<!-- Legend -->
		<div class="px-4 py-2 border-b border-gray-100 dark:border-gray-800 text-[10px] flex flex-wrap gap-3 text-gray-500 dark:text-gray-400">
			<span class="flex items-center gap-1">
				<span class="inline-block w-3 h-3 rounded bg-teal-100 border-2 border-teal-600"></span> Current
			</span>
			<span class="flex items-center gap-1">
				<span class="inline-block w-3 h-3 rounded bg-gray-100 border border-gray-400"></span> Question
			</span>
			<span class="flex items-center gap-1">
				<span class="inline-block w-2 h-0.5 bg-teal-500"></span> Branch
			</span>
			<span class="flex items-center gap-1">
				<span class="inline-block w-2 h-0.5 bg-gray-300"></span> Sequential
			</span>
		</div>

		<!-- Scrollable SVG -->
		<div class="flex-1 overflow-auto p-2">
			<svg width={svg_width} height={svg_height} class="min-w-full">
				<defs>
					<marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
						<polygon points="0 0, 8 3, 0 6" fill="#9ca3af" />
					</marker>
					<marker id="arrowhead-branch" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
						<polygon points="0 0, 8 3, 0 6" fill="#0d9488" />
					</marker>
				</defs>

				<!-- Edges -->
				{#each layout.edges as edge}
					{@const fromNode = layout.nodes[edge.from_index]}
					{@const toNode = layout.nodes[edge.to_index]}
					<path
						d={edgePath(fromNode, toNode)}
						fill="none"
						stroke={edge.color}
						stroke-width={edge.is_default ? 1.5 : 2.5}
						stroke-dasharray={edge.is_default && !edge.label ? '4 3' : 'none'}
						marker-end={edge.is_default ? 'url(#arrowhead)' : 'url(#arrowhead-branch)'}
						opacity={0.7}
					/>
					{#if edge.label}
						{@const lp = edgeLabelPos(fromNode, toNode)}
						<rect
							x={lp.x - 30}
							y={lp.y - 7}
							width="60"
							height="14"
							rx="3"
							fill="white"
							stroke={edge.color}
							stroke-width="0.5"
							opacity="0.95"
						/>
						<text
							x={lp.x}
							y={lp.y + 3}
							text-anchor="middle"
							font-size="8"
							fill={edge.color}
							font-weight="600"
						>{edge.label}</text>
					{/if}
				{/each}

				<!-- Nodes -->
				{#each layout.nodes as node}
					{@const is_current = node.index === selected_question}
					{@const is_past = node.index < selected_question}
					<g>
						<rect
							x={node.x}
							y={node.y}
							width={NODE_W}
							height={NODE_H}
							rx="8"
							fill={is_current ? '#ccfbf1' : is_past ? '#f3f4f6' : 'white'}
							stroke={is_current ? '#0d9488' : is_past ? '#9ca3af' : '#d1d5db'}
							stroke-width={is_current ? 2.5 : 1}
						/>
						<!-- Question number badge -->
						<circle
							cx={node.x + 16}
							cy={node.y + NODE_H / 2}
							r="10"
							fill={is_current ? '#0d9488' : is_past ? '#9ca3af' : '#e5e7eb'}
						/>
						<text
							x={node.x + 16}
							y={node.y + NODE_H / 2 + 3.5}
							text-anchor="middle"
							font-size="10"
							font-weight="bold"
							fill={is_current || is_past ? 'white' : '#374151'}
						>{node.index + 1}</text>

						<!-- Question label -->
						<text
							x={node.x + 34}
							y={node.y + NODE_H / 2 + 4}
							font-size="10"
							fill={is_past ? '#9ca3af' : '#1f2937'}
							font-weight={is_current ? '600' : '400'}
						>{node.label}</text>

						<!-- Current indicator -->
						{#if is_current}
							<circle
								cx={node.x + NODE_W - 12}
								cy={node.y + NODE_H / 2}
								r="4"
								fill="#0d9488"
							>
								<animate attributeName="r" values="4;6;4" dur="1.5s" repeatCount="indefinite" />
								<animate attributeName="opacity" values="1;0.5;1" dur="1.5s" repeatCount="indefinite" />
							</circle>
						{/if}
					</g>
				{/each}
			</svg>
		</div>
	</div>
{/if}
