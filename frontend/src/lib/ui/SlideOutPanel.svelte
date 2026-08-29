<script lang="ts">
	interface Props {
		open?: boolean;
		title: string;
		description?: string;
		width?: string;
		onclose?: () => void;
		children?: import('svelte').Snippet;
	}

	let { open = $bindable(false), title, description = '', width = 'max-w-xl', onclose, children }: Props = $props();
</script>

{#if open}
	<div class="fixed inset-0 z-[80] flex justify-end bg-slate-950/30 backdrop-blur-[2px]" role="presentation" onclick={(event) => event.target === event.currentTarget && onclose?.()}>
		<div class={`h-full w-full ${width} overflow-y-auto border-l border-slate-200 bg-white p-5 text-slate-900 shadow-2xl sm:p-7`} role="dialog" aria-modal="true" aria-label={title}>
			<header class="flex items-start justify-between gap-4 border-b border-slate-100 pb-5">
				<div>
					<h2 class="text-lg font-bold tracking-tight">{title}</h2>
					{#if description}<p class="mt-1 text-sm text-slate-500">{description}</p>{/if}
				</div>
				<button type="button" class="rounded-xl p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500" aria-label="Close panel" onclick={() => onclose?.()}>
					<span aria-hidden="true">×</span>
				</button>
			</header>
			<div class="py-6">{@render children?.()}</div>
		</div>
	</div>
{/if}
