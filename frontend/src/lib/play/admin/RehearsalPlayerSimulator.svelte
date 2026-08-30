<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';
	import type { Socket } from 'socket.io-client';
	interface Props { active: boolean; quiz_data: QuizData; question: number; answers: Record<string, string>; socket: Socket; }
	let { active, quiz_data, question, answers, socket }: Props = $props();
	const current = $derived(quiz_data.questions[question]);
	const submit = (answer: string) => socket.emit('submit_rehearsal_answer', { question, answer });
</script>
{#if active && current && Array.isArray(current.answers)}
	<div class="fixed bottom-4 left-4 z-[60] w-[min(92vw,24rem)] rounded-2xl border border-violet-300/50 bg-slate-950/95 p-4 text-white shadow-2xl backdrop-blur-xl">
		<div class="flex items-center justify-between"><p class="text-[10px] font-bold uppercase tracking-[0.2em] text-violet-300">Simulated player</p><span class="text-[10px] text-slate-400">Private rehearsal</span></div>
		<p class="mt-2 text-sm font-semibold">{current.question?.replace(/<[^>]*>/g, '')}</p>
		<div class="mt-3 grid gap-1.5">{#each current.answers as answer, index}{#if typeof answer === 'object'}<button type="button" class={`rounded-lg border px-3 py-2 text-left text-xs transition ${answers[String(question)] === answer.answer ? 'border-violet-300 bg-violet-500/30 text-white' : 'border-slate-700 text-slate-300 hover:bg-slate-800'}`} onclick={() => submit(answer.answer)}>{index + 1}. {answer.answer}</button>{/if}{/each}</div>
	</div>
{/if}
