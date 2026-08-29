<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { slide } from 'svelte/transition';
	import Icon from '$lib/ui/Icon.svelte';

	interface Props { children?: import('svelte').Snippet }
	let { children }: Props = $props();
	let panelOpen = $state(false);
	let collapsed = $state(false);
	let query = $state('');
	const primary = [
		{ href: '/dashboard', label: 'Overview', icon: 'home' },
		{ href: '/scenarios', label: 'Scenario library', icon: 'library' },
		{ href: '/create', label: 'Create exercise', icon: 'plus' },
		{ href: '/results', label: 'Results & analytics', icon: 'chart' },
		{ href: '/edit/files', label: 'Evidence library', icon: 'file' }
	] as const;
	const manage = [
		{ href: '/account/settings', label: 'Settings', icon: 'settings' },
		{ href: '/docs', label: 'Documentation', icon: 'help' }
	] as const;
	const runCommand = () => {
		const value = query.trim().toLowerCase();
		const match = [...primary, ...manage].find((item) => item.label.toLowerCase().includes(value));
		if (match) { query = ''; goto(match.href); }
	};
</script>

<div class="portal-shell min-h-screen bg-[#f7f9fc] text-slate-900">
	<aside class="portal-rail fixed inset-y-0 left-0 z-40 hidden w-20 flex-col border-r border-slate-200 bg-white lg:flex">
		<div class="flex h-16 items-center justify-center border-b border-slate-200"><a href="/dashboard" class="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-950 text-xs font-black text-teal-300 shadow-lg shadow-slate-900/10">CA</a></div>
		<nav class="flex flex-1 flex-col items-center gap-2 px-2 py-5" aria-label="Workspace navigation">
			{#each primary as item}
				<a href={item.href} class="rail-link" class:active={page.url.pathname === item.href || page.url.pathname.startsWith(`${item.href}/`)} title={item.label} aria-label={item.label}><Icon name={item.icon} /></a>
			{/each}
			<div class="my-3 h-px w-8 bg-slate-200"></div>
			{#each manage as item}<a href={item.href} class="rail-link" class:active={page.url.pathname.startsWith(item.href)} title={item.label} aria-label={item.label}><Icon name={item.icon} /></a>{/each}
		</nav>
		<div class="p-3"><a href="/api/v1/users/logout" class="flex h-10 w-10 items-center justify-center rounded-xl text-slate-500 hover:bg-red-50 hover:text-red-600" aria-label="Log out"><Icon name="logout" /></a></div>
	</aside>

	<header class="fixed inset-x-0 top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur-xl lg:left-20 lg:px-8">
		<div class="flex min-w-0 items-center gap-4"><button class="hidden rounded-lg border border-slate-200 p-2 text-slate-500 hover:bg-slate-50 lg:inline-flex" aria-label="Toggle navigation" onclick={() => (collapsed = !collapsed)}>☰</button><div class="hidden min-w-0 text-sm sm:block"><p class="font-semibold text-slate-900">Facilitator workspace</p><p class="truncate text-xs text-slate-400">CyberAsk · Security operations training</p></div><div class="relative hidden w-72 md:block"><input bind:value={query} onkeydown={(event) => event.key === 'Enter' && runCommand()} placeholder="Search workspace or press /" aria-label="Search workspace" class="h-9 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm outline-none transition focus:border-teal-500 focus:bg-white focus:ring-2 focus:ring-teal-100" /><kbd class="pointer-events-none absolute right-2 top-2 rounded border border-slate-200 bg-white px-1.5 text-[10px] text-slate-400">/</kbd></div></div>
		<div class="flex items-center gap-2"><button class="rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:border-teal-300 hover:text-teal-700" onclick={() => (panelOpen = !panelOpen)}>Quick actions</button><button class="flex h-9 w-9 items-center justify-center rounded-full bg-teal-100 text-xs font-bold text-teal-800" aria-label="Open account">AD</button></div>
	</header>

	{#if panelOpen}<div class="fixed right-0 top-16 z-50 w-full max-w-sm border-l border-b border-slate-200 bg-white p-5 shadow-2xl shadow-slate-900/10" transition:slide={{ axis: 'x', duration: 180 }}><div class="flex items-start justify-between"><div><p class="eyebrow">Quick actions</p><h2 class="mt-1 text-lg font-bold">What do you want to do?</h2></div><button class="text-slate-400 hover:text-slate-900" onclick={() => (panelOpen = false)} aria-label="Close quick actions"><Icon name="close" /></button></div><div class="mt-5 grid gap-2"><a class="action-tile" href="/seed"><span class="tile-icon bg-teal-50 text-teal-700"><Icon name="library" size={16} /></span><span><strong>Use a scenario template</strong><small>Start a deep branched exercise</small></span><Icon name="arrow-right" size={16} /></a><a class="action-tile" href="/create"><span class="tile-icon bg-sky-50 text-sky-700"><Icon name="plus" size={16} /></span><span><strong>Create from scratch</strong><small>Build a quiz or tabletop</small></span><Icon name="arrow-right" size={16} /></a><a class="action-tile" href="/results"><span class="tile-icon bg-violet-50 text-violet-700"><Icon name="chart" size={16} /></span><span><strong>Review performance</strong><small>Open results and insights</small></span><Icon name="arrow-right" size={16} /></a></div></div>{/if}

	<main class="min-h-screen pt-16 lg:pl-20">{@render children?.()}</main>
</div>

<style>
	:global(.rail-link) { display:flex; height:2.75rem; width:2.75rem; align-items:center; justify-content:center; border-radius:.75rem; color:#94a3b8; font-size:1.2rem; transition:all .15s; }
	:global(.rail-link:hover) { background:#f0fdfa; color:#0f766e; }
	:global(.rail-link.active) { background:#ccfbf1; color:#0f766e; box-shadow:inset 3px 0 0 #0f766e; }
	:global(.action-tile) { display:flex; align-items:center; gap:.75rem; border:1px solid #e2e8f0; border-radius:.75rem; padding:.75rem; color:#475569; transition:all .15s; }
	:global(.action-tile:hover) { border-color:#5eead4; background:#f0fdfa; }
	:global(.action-tile strong) { display:block; font-size:.875rem; color:#0f172a; }
	:global(.action-tile small) { display:block; margin-top:.15rem; font-size:.75rem; color:#94a3b8; }
	:global(.tile-icon) { display:flex; height:2rem; width:2rem; align-items:center; justify-content:center; border-radius:.6rem; font-weight:700; }
</style>
