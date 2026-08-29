<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';
	import type { Player } from '$lib/admin';
	import { buildScenarioGraph } from '$lib/scenarioGraph';

	interface Props {
		quiz_data: QuizData;
		game_pin: string;
		game_token: string;
		host_token: string;
		players: Player[];
		selected_question: number;
		answer_count: number;
		timer_res: string;
		player_roles?: Record<string, string>;
		socket: any;
		onopenconsole: (tab?: 'situation' | 'injects' | 'hands' | 'roles' | 'timeline') => void;
	}
	let { quiz_data, game_pin, game_token, host_token, players, selected_question, answer_count, timer_res, player_roles = {}, socket, onopenconsole }: Props = $props();
	let expanded = $state(false);
	let manual_target = $state('');
	let reset_target = $state<string | null>(null);
	const graph = $derived(buildScenarioGraph(quiz_data.questions ?? []));
	const current = $derived(quiz_data.questions?.[selected_question]);
	const completion = $derived(players.length ? Math.min(100, Math.round((answer_count / players.length) * 100)) : 0);
	const connected = $derived(players.length);
	const route = $derived(selected_question < 0 ? 'Lobby' : Array.from({ length: selected_question + 1 }, (_, index) => index + 1).join('  →  '));

	const rewind = () => {
		if (selected_question > 0) socket.emit('set_question_number', String(selected_question - 1));
	};
	const pause = () => socket.emit('pause_question_timer', {});
	const resume = () => socket.emit('resume_question_timer', {});
	const advance = () => socket.emit('advance_tabletop', {});
	const manual_branch = () => {
		if (!manual_target) return;
		socket.emit('force_next_question', { question_id: manual_target });
		manual_target = '';
	};
	const reset_participant = (username: string) => {
		if (reset_target === username) {
			socket.emit('kick_player', { username });
			reset_target = null;
		} else reset_target = username;
	};
	const open_handover_console = () => {
		if (!game_pin || !game_token || !host_token) return;
		window.open(`/remote?game_pin=${encodeURIComponent(game_pin)}&game_id=${encodeURIComponent(game_token)}&host_token=${encodeURIComponent(host_token)}`, '_blank', 'noopener,noreferrer');
	};
</script>

<section class="fixed left-3 right-3 top-[7.25rem] z-20 mx-auto max-w-[1500px] rounded-2xl border border-slate-200 bg-white/95 shadow-[0_12px_35px_rgba(15,23,42,0.12)] backdrop-blur-xl">
	<div class="flex min-h-14 flex-wrap items-center gap-2 px-3 py-2 sm:px-4">
		<div class="mr-2 flex min-w-[155px] items-center gap-2 border-r border-slate-100 pr-3"><span class="flex h-8 w-8 items-center justify-center rounded-xl bg-teal-50 text-sm text-teal-700">⌁</span><div><p class="text-[9px] font-bold uppercase tracking-[0.18em] text-slate-400">Live control centre</p><p class="max-w-[170px] truncate text-xs font-bold text-slate-900">{quiz_data.title}</p></div></div>
		<div class="rounded-xl bg-slate-50 px-3 py-1.5"><p class="text-[9px] font-bold uppercase tracking-wider text-slate-400">Phase</p><p class="text-xs font-bold text-slate-800">{current?.objective ?? (selected_question < 0 ? 'Briefing' : 'In progress')}</p></div>
		<div class="rounded-xl bg-slate-50 px-3 py-1.5"><p class="text-[9px] font-bold uppercase tracking-wider text-slate-400">Current node</p><p class="text-xs font-bold text-slate-800">{selected_question < 0 ? 'Lobby' : `${selected_question + 1} / ${quiz_data.questions.length}`}</p></div>
		<div class="hidden rounded-xl bg-slate-50 px-3 py-1.5 lg:block"><p class="text-[9px] font-bold uppercase tracking-wider text-slate-400">Path</p><p class="max-w-[220px] truncate text-xs font-bold text-slate-800">{route}</p></div>
		<div class="rounded-xl bg-slate-50 px-3 py-1.5"><p class="text-[9px] font-bold uppercase tracking-wider text-slate-400">Responses</p><p class="text-xs font-bold text-slate-800">{answer_count} / {players.length} <span class="font-medium text-teal-600">({completion}%)</span></p></div>
		<div class="rounded-xl bg-slate-50 px-3 py-1.5"><p class="text-[9px] font-bold uppercase tracking-wider text-slate-400">Participants</p><p class="text-xs font-bold text-emerald-700"><span class="mr-1 inline-block h-1.5 w-1.5 rounded-full bg-emerald-500"></span>{connected} connected</p></div>
		<div class="ml-auto flex items-center gap-1.5"><button type="button" class="rounded-lg border border-slate-200 px-2.5 py-2 text-xs font-bold text-slate-600 hover:border-teal-300 hover:text-teal-700" title="Previous node" onclick={rewind} disabled={selected_question <= 0}>←</button><button type="button" class="rounded-lg border border-slate-200 px-2.5 py-2 text-xs font-bold text-slate-600 hover:border-teal-300 hover:text-teal-700" title="Pause timer" onclick={pause} disabled={timer_res === '0'}>Ⅱ</button><button type="button" class="rounded-lg border border-slate-200 px-2.5 py-2 text-xs font-bold text-slate-600 hover:border-teal-300 hover:text-teal-700" title="Resume timer" onclick={resume} disabled={timer_res !== '0'}>▶</button><button type="button" class="rounded-lg bg-slate-950 px-3 py-2 text-xs font-bold text-white hover:bg-slate-800" onclick={() => (expanded = !expanded)}>{expanded ? 'Close centre' : 'Open centre'}</button></div>
	</div>
	{#if expanded}
		<div class="grid gap-3 border-t border-slate-100 p-4 md:grid-cols-4">
			<div class="rounded-xl border border-slate-200 bg-slate-50 p-3"><div class="flex items-center justify-between"><p class="text-xs font-bold text-slate-800">Response completion</p><span class="text-xs font-bold text-teal-700">{completion}%</span></div><div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-200"><div class="h-full rounded-full bg-teal-500 transition-all" style={`width:${completion}%`}></div></div><p class="mt-2 text-[11px] text-slate-500">{answer_count} of {players.length} participants responded to this node.</p></div>
			<div class="rounded-xl border border-slate-200 bg-slate-50 p-3"><p class="text-xs font-bold text-slate-800">Exercise path</p><p class="mt-2 break-words text-xs leading-5 text-slate-500">{route}</p><p class="mt-2 text-[11px] text-slate-400">{graph.edges.length} configured transitions · {quiz_data.questions.length} nodes</p></div>
			<div class="rounded-xl border border-slate-200 bg-slate-50 p-3"><p class="text-xs font-bold text-slate-800">Manual navigation</p><div class="mt-2 flex gap-2"><select bind:value={manual_target} class="min-w-0 flex-1 rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-[11px] text-slate-700"><option value="">Choose branch…</option>{#each quiz_data.questions as question, index}{#if index !== selected_question}<option value={question.id ?? ''}>{index + 1}. {question.question?.replace(/<[^>]*>/g, '').slice(0, 24) || `Step ${index + 1}`}</option>{/if}{/each}</select><button type="button" class="rounded-lg bg-teal-600 px-2.5 py-1.5 text-[11px] font-bold text-white disabled:opacity-40" onclick={manual_branch} disabled={!manual_target}>Go</button></div><button type="button" class="mt-2 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[11px] font-bold text-slate-600 hover:border-teal-300 hover:text-teal-700" onclick={advance}>Advance recommended branch</button></div>
			<div class="rounded-xl border border-slate-200 bg-slate-50 p-3"><p class="text-xs font-bold text-slate-800">Operator actions</p><div class="mt-2 flex flex-wrap gap-2"><button type="button" class="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[11px] font-bold text-slate-600 hover:border-teal-300 hover:text-teal-700" onclick={() => onopenconsole('injects')}>Inject queue · {quiz_data.injects?.length ?? 0}</button><button type="button" class="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[11px] font-bold text-slate-600 hover:border-teal-300 hover:text-teal-700" onclick={() => onopenconsole('roles')}>Roles & teams</button><button type="button" class="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[11px] font-bold text-slate-600 hover:border-teal-300 hover:text-teal-700" onclick={() => onopenconsole('timeline')}>Notes & timeline</button></div></div>
			<div class="rounded-xl border border-slate-200 bg-slate-50 p-3"><div class="flex items-center justify-between"><p class="text-xs font-bold text-slate-800">Host continuity</p><span class="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700">Protected</span></div><p class="mt-2 text-[11px] leading-4 text-slate-500">Live state is server-backed. A remote host can take over with the protected handover console.</p><button type="button" class="mt-3 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[11px] font-bold text-slate-600 hover:border-teal-300 hover:text-teal-700" onclick={open_handover_console}>Open handover console</button></div>
		</div>
		<div class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3"><div class="flex items-center justify-between"><p class="text-xs font-bold text-slate-800">Participant connection health</p><span class="text-[11px] font-semibold text-emerald-700">{players.length} active</span></div><div class="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">{#each players as player}<div class="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2"><div class="min-w-0"><p class="truncate text-xs font-bold text-slate-800">{player.username}</p><p class="truncate text-[10px] text-slate-400">{player_roles[player.username] ?? 'Role pending'}</p>{#if reset_target === player.username}<p class="text-[10px] font-semibold text-rose-600">Click again to reset connection</p>{/if}</div><div class="ml-2 flex shrink-0 items-center gap-2"><span class="h-2 w-2 rounded-full bg-emerald-500" title="Connected"></span><button type="button" class="text-[10px] font-semibold text-slate-400 hover:text-rose-600" title="Reset participant connection" onclick={() => reset_participant(player.username)}>Reset</button></div></div>{:else}<p class="text-xs text-slate-500">No participants connected yet.</p>{/each}</div></div>
		{#if current?.facilitator_notes}<div class="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3"><p class="text-xs font-bold text-amber-900">Current facilitator note</p><p class="mt-1 text-xs leading-5 text-amber-900/80">{current.facilitator_notes}</p></div>{/if}
	{/if}
</section>
