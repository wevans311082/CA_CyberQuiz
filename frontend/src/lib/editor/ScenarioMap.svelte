<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { buildScenarioGraph, type ScenarioIssue } from '$lib/scenarioGraph';

	interface Props { questions: Question[]; selected_question: number; issues?: ScenarioIssue[]; onselect: (index: number) => void; }
	let { questions, selected_question, issues = [], onselect }: Props = $props();
	const graph = $derived(buildScenarioGraph(questions));
	const nodeWidth = 220;
	const nodeHeight = 58;
	const gapY = 34;
	const laneWidth = 275;
	const positions = $derived.by(() => {
		const lanes = new Array(questions.length).fill(0);
		graph.edges.forEach((edge) => { if (edge.type === 'branch' && edge.to > edge.from) lanes[edge.to] = Math.max(lanes[edge.to], lanes[edge.from] + 1); });
		return questions.map((_, index) => ({ x: 24 + lanes[index] * laneWidth, y: 24 + index * (nodeHeight + gapY) }));
	});
	const issueIndexes = $derived(new Set(issues.filter((issue) => issue.questionIndex !== undefined).map((issue) => issue.questionIndex)));
	const width = $derived(Math.max(560, Math.max(...positions.map((position) => position.x + nodeWidth), 0) + 34));
	const height = $derived(Math.max(220, positions.length * (nodeHeight + gapY) + 28));
	const label = (value: string, max = 28) => { const text = value.replace(/<[^>]+>/g, '').trim(); return text.length > max ? `${text.slice(0, max)}…` : text || 'Untitled step'; };
	const edgePath = (from: number, to: number) => {
		const a = positions[from], b = positions[to];
		return `M ${a.x + nodeWidth / 2} ${a.y + nodeHeight} C ${a.x + nodeWidth / 2} ${(a.y + nodeHeight + b.y) / 2}, ${b.x + nodeWidth / 2} ${(a.y + nodeHeight + b.y) / 2}, ${b.x + nodeWidth / 2} ${b.y}`;
	};
</script>

<section class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
	<div class="flex items-center justify-between border-b border-slate-100 px-5 py-4">
		<div><p class="text-[10px] font-bold uppercase tracking-[0.18em] text-teal-600">Scenario canvas</p><h2 class="mt-1 text-base font-bold text-slate-900">Decision flow</h2></div>
		<div class="flex items-center gap-2 text-xs text-slate-500"><span class="rounded-full bg-slate-100 px-2.5 py-1 font-semibold">{questions.length} steps</span><span class:error={issues.some((issue) => issue.level === 'error')} class="rounded-full bg-amber-50 px-2.5 py-1 font-semibold text-amber-700">{issues.length} checks</span></div>
	</div>
	<div class="overflow-auto bg-[radial-gradient(#dbe5ef_1px,transparent_1px)] [background-size:18px_18px] p-3">
		<svg width={width} height={height} role="img" aria-label="Scenario decision flow">
			<defs><marker id="scenario-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 z" fill="#94a3b8" /></marker></defs>
			{#each graph.edges as edge}
				<path d={edgePath(edge.from, edge.to)} fill="none" stroke={edge.type === 'branch' ? '#14b8a6' : '#94a3b8'} stroke-width={edge.type === 'branch' ? 2.5 : 1.5} stroke-dasharray={edge.type === 'sequential' ? '5 4' : undefined} marker-end="url(#scenario-arrow)" />
				{#if edge.label}<text x={(positions[edge.from].x + positions[edge.to].x + nodeWidth) / 2} y={(positions[edge.from].y + positions[edge.to].y + nodeHeight) / 2 - 4} text-anchor="middle" font-size="9" fill="#64748b">{label(edge.label, 20)}</text>{/if}
			{/each}
			{#each questions as question, index}
				{@const position = positions[index]}
				<g role="button" tabindex="0" aria-label={`Edit step ${index + 1}`} onclick={() => onselect(index)} onkeydown={(event) => (event.key === 'Enter' || event.key === ' ') && onselect(index)} class="cursor-pointer">
					<rect x={position.x} y={position.y} width={nodeWidth} height={nodeHeight} rx="12" fill={selected_question === index ? '#ecfdf5' : 'white'} stroke={issueIndexes.has(index) ? '#f59e0b' : selected_question === index ? '#0d9488' : '#cbd5e1'} stroke-width={selected_question === index || issueIndexes.has(index) ? 2.5 : 1.2} />
					<circle cx={position.x + 22} cy={position.y + 29} r="13" fill={selected_question === index ? '#0d9488' : '#e2e8f0'} /><text x={position.x + 22} y={position.y + 33} text-anchor="middle" font-size="10" font-weight="700" fill={selected_question === index ? 'white' : '#475569'}>{index + 1}</text>
					<text x={position.x + 44} y={position.y + 25} font-size="11" font-weight="700" fill="#0f172a">{label(question.question, 25)}</text><text x={position.x + 44} y={position.y + 43} font-size="9" fill="#64748b">{question.type ?? 'Question'}{issueIndexes.has(index) ? ' · Needs review' : ''}</text>
				</g>
			{/each}
		</svg>
	</div>
</section>
