import type { EditorData, Question, Answer, Inject } from '$lib/quiz_types';

export type ScenarioIssueLevel = 'error' | 'warning' | 'info';

export interface ScenarioIssue {
	level: ScenarioIssueLevel;
	code: string;
	message: string;
	questionIndex?: number;
	questionId?: string;
	fix?: string;
}

export interface ScenarioEdge {
	from: number;
	to: number;
	label: string;
	type: 'branch' | 'default' | 'sequential';
}

export interface ScenarioGraph {
	nodes: Question[];
	edges: ScenarioEdge[];
	idToIndex: Map<string, number>;
}

const clean = (value: unknown) => String(value ?? '').replace(/<[^>]*>/g, '').trim();

export function buildScenarioGraph(questions: Question[]): ScenarioGraph {
	const idToIndex = new Map<string, number>();
	questions.forEach((question, index) => {
		if (question.id) idToIndex.set(question.id, index);
	});

	const edges: ScenarioEdge[] = [];
	questions.forEach((question, from) => {
		let hasExplicitDestination = false;
		const answers = Array.isArray(question.answers) ? (question.answers as Answer[]) : [];
		answers.forEach((answer) => {
			if (!answer.next_question_id) return;
			const to = idToIndex.get(answer.next_question_id);
			if (to !== undefined) {
				edges.push({ from, to, label: clean(answer.answer).slice(0, 26), type: 'branch' });
				hasExplicitDestination = true;
			}
		});
		if (question.default_next_question_id) {
			const to = idToIndex.get(question.default_next_question_id);
			if (to !== undefined) {
				edges.push({ from, to, label: 'Default path', type: 'default' });
				hasExplicitDestination = true;
			}
		}
		// This mirrors the runtime resolver: a question with no configured route moves forward.
		if (!hasExplicitDestination && from < questions.length - 1) {
			edges.push({ from, to: from + 1, label: 'Continue', type: 'sequential' });
		}
	});
	return { nodes: questions, edges, idToIndex };
}

export function validateScenario(data: Pick<EditorData, 'questions' | 'roles' | 'injects'>): ScenarioIssue[] {
	const questions = data.questions ?? [];
	const issues: ScenarioIssue[] = [];
	if (!questions.length) {
		return [{ level: 'error', code: 'empty_scenario', message: 'Add at least one question or information slide.' }];
	}

	const ids = new Map<string, number[]>();
	questions.forEach((question, index) => {
		const id = question.id?.trim();
		if (!id) {
			issues.push({ level: 'warning', code: 'missing_id', message: `Step ${index + 1} will receive a stable ID when saved.`, questionIndex: index, fix: 'Save the exercise to generate IDs.' });
			return;
		}
		ids.set(id, [...(ids.get(id) ?? []), index]);
	});
	ids.forEach((indexes, id) => {
		if (indexes.length > 1) indexes.forEach((index) => issues.push({ level: 'error', code: 'duplicate_id', message: `Step ${index + 1} reuses the ID “${id}”.`, questionIndex: index, questionId: id, fix: 'Give each step a unique ID.' }));
	});

	const graph = buildScenarioGraph(questions);
	const checkTarget = (target: string | undefined, index: number, label: string) => {
		if (target && !graph.idToIndex.has(target)) {
			issues.push({ level: 'error', code: 'missing_target', message: `${label} points to “${target}”, which does not exist.`, questionIndex: index, fix: 'Choose an existing step or clear the route.' });
		}
	};
	questions.forEach((question, index) => {
		checkTarget(question.default_next_question_id, index, 'The default route');
		if (Array.isArray(question.answers)) {
			(question.answers as Answer[]).forEach((answer) => checkTarget(answer.next_question_id, index, `“${clean(answer.answer) || `Answer ${index + 1}`}”`));
		}
		(question.allowed_roles ?? []).forEach((role) => {
			if (data.roles?.length && !data.roles.includes(role)) issues.push({ level: 'warning', code: 'unknown_role', message: `Step ${index + 1} references the role “${role}”, but it is not in the role list.`, questionIndex: index, fix: 'Add the role or remove it from this step.' });
		});
	});

	const reachable = new Set<number>();
	const queue = [0];
	while (queue.length) {
		const current = queue.shift()!;
		if (reachable.has(current)) continue;
		reachable.add(current);
		graph.edges.filter((edge) => edge.from === current).forEach((edge) => {
			if (!reachable.has(edge.to)) queue.push(edge.to);
		});
	}
	questions.forEach((question, index) => {
		if (!reachable.has(index)) issues.push({ level: 'warning', code: 'unreachable', message: `Step ${index + 1} cannot be reached from the start.`, questionIndex: index, questionId: question.id, fix: 'Connect it from another step or remove it.' });
	});

	const hasTerminal = questions.some((_, index) => !graph.edges.some((edge) => edge.from === index));
	if (!hasTerminal) issues.push({ level: 'warning', code: 'no_terminal', message: 'No route ends the exercise; participants may be trapped in a loop.', fix: 'Leave at least one route without a destination.' });

	(data.injects ?? []).forEach((inject: Inject, index) => {
		if (inject.trigger_after_question_id && !graph.idToIndex.has(inject.trigger_after_question_id)) issues.push({ level: 'error', code: 'missing_inject_target', message: `Inject ${index + 1} triggers after a step that does not exist.`, fix: 'Choose an existing step or clear the trigger.' });
	});
	return issues;
}
