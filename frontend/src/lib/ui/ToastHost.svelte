<script lang="ts">
	import Button from '$lib/ui/Button.svelte';
	import Icon from '$lib/ui/Icon.svelte';
	import {
		dismissNotice,
		notificationState,
		resolveConfirmation
	} from '$lib/notifications.svelte';

	const tone = {
		success: 'border-emerald-200 bg-emerald-50 text-emerald-900',
		error: 'border-rose-200 bg-rose-50 text-rose-900',
		info: 'border-sky-200 bg-sky-50 text-sky-900'
	};
	const icon = { success: 'check', error: 'x', info: 'info' } as const;
</script>

<div class="pointer-events-none fixed inset-x-4 top-4 z-[100] flex flex-col items-end gap-3 sm:left-auto sm:w-[min(420px,calc(100vw-2rem))]">
	{#each notificationState.notices as notice (notice.id)}
		<div class={`pointer-events-auto flex w-full items-start gap-3 rounded-2xl border px-4 py-3 text-sm font-medium shadow-xl ${tone[notice.kind]}`} role="status">
			<Icon name={icon[notice.kind]} size={18} />
			<p class="min-w-0 flex-1 whitespace-pre-line">{notice.message}</p>
			<Button variant="ghost" size="sm" ariaLabel="Dismiss notification" onclick={() => dismissNotice(notice.id)}>
				<Icon name="x" size={16} />
			</Button>
		</div>
	{/each}
</div>

{#if notificationState.confirmation}
	<div class="fixed inset-0 z-[110] flex items-center justify-center bg-slate-950/35 p-4 backdrop-blur-sm" role="presentation">
		<div class="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-6 text-slate-900 shadow-2xl" role="alertdialog" aria-modal="true" aria-labelledby="confirmation-title">
			<div class="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl bg-amber-100 text-amber-700"><Icon name="alert-triangle" size={22} /></div>
			<h2 id="confirmation-title" class="text-lg font-bold">{notificationState.confirmation.title}</h2>
			<p class="mt-2 whitespace-pre-line text-sm leading-6 text-slate-600">{notificationState.confirmation.message}</p>
			<div class="mt-6 flex justify-end gap-2">
				<Button variant="secondary" onclick={() => resolveConfirmation(false)}>Cancel</Button>
				<Button variant="danger" onclick={() => resolveConfirmation(true)}>{notificationState.confirmation.confirmLabel}</Button>
			</div>
		</div>
	</div>
{/if}
