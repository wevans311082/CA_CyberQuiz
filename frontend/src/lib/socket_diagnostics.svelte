<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { browser } from '$app/environment';
	import { onDestroy, onMount } from 'svelte';

	interface DebugEntry {
		name: string;
		at: string;
		payload?: unknown;
	}

	interface Props {
		socket: any;
		label: string;
		details?: Record<string, unknown>;
		enabled?: boolean;
	}

	let { socket, label, details = {}, enabled = false }: Props = $props();

	let expanded = $state(false);
	let clientStatus = $state('idle');
	let transport = $state('unknown');
	let entries: DebugEntry[] = $state([]);
	let serverState = $state<Record<string, unknown> | null>(null);

	const pushEntry = (name: string, payload?: unknown) => {
		entries = [{ name, at: new Date().toISOString(), payload }, ...entries].slice(0, 18);
	};

	const syncTransport = () => {
		transport = socket?.io?.engine?.transport?.name ?? 'unknown';
	};

	const refreshServerState = () => {
		socket.emit('debug_status');
	};

	const sendEcho = () => {
		socket.emit('debug_echo', {
			label,
			clientTime: new Date().toISOString(),
			socketId: socket.id ?? null
		});
	};

	const reconnect = () => {
		socket.disconnect();
		socket.connect();
	};

	onMount(() => {
		if (!browser) {
			return;
		}

		const onAny = (eventName: string, ...args: unknown[]) => {
			if (eventName.startsWith('debug_')) {
				return;
			}
			pushEntry(eventName, args[0]);
			if (['registered_as_admin', 'joined_game', 'rejoined_game', 'lobby_state', 'start_game', 'set_question_number', 'player_joined'].includes(eventName)) {
				refreshServerState();
			}
		};

		const onConnect = () => {
			clientStatus = 'connected';
			syncTransport();
			pushEntry('connect', { socketId: socket.id });
			refreshServerState();
		};

		const onDisconnect = (reason: string) => {
			clientStatus = `disconnected: ${reason}`;
			syncTransport();
			pushEntry('disconnect', { reason });
		};

		const onConnectError = (error: Error) => {
			clientStatus = `connect_error: ${error.message}`;
			pushEntry('connect_error', { message: error.message });
		};

		const onDebugState = (payload: Record<string, unknown>) => {
			serverState = payload;
			pushEntry('debug_status', payload);
		};

		const onDebugEcho = (payload: Record<string, unknown>) => {
			pushEntry('debug_echo', payload);
		};

		clientStatus = socket.connected ? 'connected' : 'connecting';
		syncTransport();

		socket.onAny(onAny);
		socket.on('connect', onConnect);
		socket.on('disconnect', onDisconnect);
		socket.on('connect_error', onConnectError);
		socket.on('debug_status', onDebugState);
		socket.on('debug_echo', onDebugEcho);

		refreshServerState();

		onDestroy(() => {
			socket.offAny(onAny);
			socket.off('connect', onConnect);
			socket.off('disconnect', onDisconnect);
			socket.off('connect_error', onConnectError);
			socket.off('debug_status', onDebugState);
			socket.off('debug_echo', onDebugEcho);
		});
	});
</script>

{#if enabled}
	<div class="fixed bottom-4 left-4 right-4 z-50 mx-auto max-w-5xl rounded-2xl border border-slate-300/80 bg-white/90 p-3 shadow-2xl backdrop-blur dark:border-slate-700/80 dark:bg-slate-950/90">
		<div class="flex flex-wrap items-center justify-between gap-3">
			<div class="min-w-0">
				<p class="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
					Socket Diagnostics · {label}
				</p>
				<p class="mt-1 text-sm text-slate-800 dark:text-slate-100">
					Status: {clientStatus} · Socket: {socket.id ?? 'none'} · Transport: {transport}
				</p>
			</div>
			<div class="flex flex-wrap gap-2">
				<button class="rounded-lg border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700" onclick={refreshServerState}>Refresh</button>
				<button class="rounded-lg border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700" onclick={sendEcho}>Echo</button>
				<button class="rounded-lg border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700" onclick={reconnect}>Reconnect</button>
				<button class="rounded-lg border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700" onclick={() => (expanded = !expanded)}>
					{expanded ? 'Hide details' : 'Show details'}
				</button>
			</div>
		</div>

		{#if expanded}
			<div class="mt-3 grid gap-3 lg:grid-cols-3">
				<div class="rounded-xl bg-slate-100/80 p-3 text-xs dark:bg-slate-900/80">
					<p class="mb-2 font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Local state</p>
					<pre class="overflow-auto whitespace-pre-wrap break-words">{JSON.stringify(details, null, 2)}</pre>
				</div>
				<div class="rounded-xl bg-slate-100/80 p-3 text-xs dark:bg-slate-900/80">
					<p class="mb-2 font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Server state</p>
					<pre class="overflow-auto whitespace-pre-wrap break-words">{JSON.stringify(serverState, null, 2)}</pre>
				</div>
				<div class="rounded-xl bg-slate-100/80 p-3 text-xs dark:bg-slate-900/80">
					<p class="mb-2 font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Recent events</p>
					<div class="max-h-48 overflow-auto space-y-2">
						{#each entries as entry}
							<div class="rounded-lg border border-slate-200/80 p-2 dark:border-slate-800">
								<p class="font-semibold text-slate-700 dark:text-slate-200">{entry.name}</p>
								<p class="text-[10px] text-slate-500 dark:text-slate-400">{entry.at}</p>
								{#if entry.payload !== undefined}
									<pre class="mt-1 overflow-auto whitespace-pre-wrap break-words">{JSON.stringify(entry.payload, null, 2)}</pre>
								{/if}
							</div>
						{/each}
					</div>
				</div>
			</div>
		{/if}
	</div>
{/if}