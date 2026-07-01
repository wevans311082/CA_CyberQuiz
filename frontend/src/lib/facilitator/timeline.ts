// SPDX-FileCopyrightText: 2025 CyberAsk
//
// SPDX-License-Identifier: MPL-2.0

import type { Inject, TimelineEvent } from '$lib/quiz_types';

const new_id = () =>
	typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
		? crypto.randomUUID()
		: `id-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

export type InjectLogEntry = {
	inject?: Inject;
	inject_id?: string;
	title?: string;
	severity?: string;
	content?: string;
	triggered_by?: string;
	timestamp?: string;
};

export type SituationLogEntry = {
	severity?: string;
	phase?: string;
	affected_systems?: string[];
	summary?: string;
	context_notes?: string;
	timestamp?: string;
};

const fmt_time = (ts?: string) => {
	if (!ts) return new Date().toISOString();
	return ts;
};

export function buildFacilitatorTimeline(
	injectsLog: InjectLogEntry[],
	situationLog: SituationLogEntry[]
): TimelineEvent[] {
	const events: TimelineEvent[] = [];

	for (const entry of injectsLog) {
		const inject = entry.inject ?? {
			id: entry.inject_id ?? new_id(),
			title: entry.title ?? 'Inject',
			content: entry.content ?? '',
			severity: (entry.severity as Inject['severity']) ?? 'info'
		};
		events.push({
			id: `inj-${inject.id}-${entry.timestamp ?? ''}`,
			type: 'inject',
			timestamp: fmt_time(entry.timestamp),
			title: inject.title ?? 'Inject pushed',
			detail: inject.content?.slice(0, 120),
			data: { severity: inject.severity, triggered_by: entry.triggered_by }
		});
	}

	for (const entry of situationLog) {
		events.push({
			id: `sit-${entry.timestamp ?? new_id()}`,
			type: 'situation_update',
			timestamp: fmt_time(entry.timestamp),
			title: `Situation: ${entry.severity ?? 'unknown'} / ${entry.phase ?? 'N/A'}`,
			detail: entry.summary?.slice(0, 120),
			data: {
				severity: entry.severity,
				phase: entry.phase,
				systems: entry.affected_systems
			}
		});
	}

	return events.sort(
		(a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
	);
}

export function normalizeInjectsLog(raw: InjectLogEntry[]): InjectLogEntry[] {
	return raw.map((entry) => {
		if (entry.inject) return entry;
		return {
			...entry,
			inject: {
				id: entry.inject_id ?? new_id(),
				title: entry.title ?? 'Inject',
				content: entry.content ?? '',
				severity: (entry.severity as Inject['severity']) ?? 'info'
			}
		};
	});
}