<!--
SPDX-FileCopyrightText: 2025 CyberAsk

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { browser } from '$app/environment';
	import DOMPurify from 'dompurify';
	import { marked } from 'marked';
	import type { Inject } from '$lib/quiz_types';

	export type InjectPreviewPayload = {
		title: string;
		content: string;
		severity: Inject['severity'];
		inject_id?: string;
	};

	interface Props {
		open?: boolean;
		payload?: InjectPreviewPayload | null;
		onconfirm?: () => void;
		oncancel?: () => void;
	}

	let { open = $bindable(false), payload = null, onconfirm, oncancel }: Props = $props();

	const rendered = $derived(
		browser && payload?.content
			? DOMPurify.sanitize(marked.parse(payload.content) as string)
			: ''
	);

	const severityLabel: Record<string, string> = {
		info: 'Info',
		warning: 'Warning',
		critical: 'Critical'
	};

	const close = () => {
		open = false;
		oncancel?.();
	};

	const confirm = () => {
		onconfirm?.();
		open = false;
	};
</script>

{#if open && payload}
	<div class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
		<div class="host-panel w-full max-w-lg border-orange-500/40">
			<div class="mb-3 flex items-start justify-between gap-3">
				<div>
					<p class="host-label">Inject preview</p>
					<h3 class="text-lg font-semibold text-slate-100">{payload.title}</h3>
					<span class="mt-1 inline-block rounded-full border border-orange-500/40 bg-orange-500/15 px-2 py-0.5 text-[10px] font-semibold uppercase text-orange-200">
						{severityLabel[payload.severity] ?? payload.severity}
					</span>
				</div>
				<button type="button" class="host-btn px-2.5" onclick={close} aria-label="Cancel">✕</button>
			</div>

			<div class="max-h-[40vh] overflow-y-auto rounded-lg border border-slate-700/60 bg-slate-950/60 p-4 text-sm text-slate-200 prose prose-invert prose-sm max-w-none">
				{#if rendered}
					{@html rendered}
				{:else}
					<p class="italic text-slate-500">No content — title-only inject.</p>
				{/if}
			</div>

			<p class="mt-3 text-xs text-slate-500">This will be pushed to all participants immediately.</p>

			<div class="mt-4 flex justify-end gap-2">
				<button type="button" class="host-btn" onclick={close}>Cancel</button>
				<button type="button" class="host-btn-warn" onclick={confirm}>Push to players</button>
			</div>
		</div>
	</div>
{/if}