// SPDX-FileCopyrightText: 2025 CyberAsk
//
// SPDX-License-Identifier: MPL-2.0

import type { Inject } from '$lib/quiz_types';

export interface QuickInjectPreset {
	id: string;
	title: string;
	content: string;
	severity: Inject['severity'];
	hint: string;
}

export const QUICK_INJECT_PRESETS: QuickInjectPreset[] = [
	{
		id: 'preset-media',
		title: 'Media inquiry',
		content:
			'**Breaking:** A journalist has emailed asking whether you are aware of a cyber incident affecting customer data. They want a statement within the hour.',
		severity: 'warning',
		hint: 'External pressure'
	},
	{
		id: 'preset-ransom',
		title: 'Ransom note detected',
		content:
			'**Alert:** A ransom note was found on several file servers. The threat actor claims exfiltration occurred 72 hours ago and demands payment within 24 hours.',
		severity: 'critical',
		hint: 'Escalation'
	},
	{
		id: 'preset-legal',
		title: 'Regulator contact',
		content:
			'**Legal:** Data protection authority has requested initial notification details. You must confirm scope, affected records, and containment status.',
		severity: 'warning',
		hint: 'Compliance'
	},
	{
		id: 'preset-phish',
		title: 'Phishing campaign',
		content:
			'**SOC:** Multiple users reported suspicious emails impersonating IT support. At least three employees clicked the link before reporting.',
		severity: 'info',
		hint: 'User reports'
	},
	{
		id: 'preset-outage',
		title: 'Service degradation',
		content:
			'**Operations:** Customer-facing portal latency has increased 400%. Monitoring shows database connection pool exhaustion on the primary cluster.',
		severity: 'high',
		hint: 'Business impact'
	},
	{
		id: 'preset-intel',
		title: 'Threat intel feed',
		content:
			'**Intel:** Industry ISAC published an advisory matching TTPs observed in your environment. Recommended immediate password resets for privileged accounts.',
		severity: 'info',
		hint: 'External intel'
	}
];