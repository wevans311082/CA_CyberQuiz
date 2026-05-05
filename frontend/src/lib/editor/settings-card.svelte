<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData, Inject } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import Spinner from '$lib/Spinner.svelte';
	import { createTippy } from 'svelte-tippy';

	const { t } = getLocalization();

	let uppyOpen = $state(false);
	let bg_uppy_open = $state(false);

	interface Props {
		edit_id: string;
		data: EditorData;
	}

	let { edit_id = $bindable(), data = $bindable() }: Props = $props();

	let custom_bg_color = $state(Boolean(data.background_color));
	let new_role_input = $state('');
	let new_role_desc_input = $state('');
	let expanded_role_desc: string | null = $state(null);

	const ROLE_TEMPLATES: Array<{ name: string; description: string }> = [
		{ name: 'CISO', description: 'Chief Information Security Officer — owns cybersecurity strategy and makes final security decisions.' },
		{ name: 'Incident Commander', description: 'Leads the incident response effort and coordinates all team activities.' },
		{ name: 'SOC Analyst', description: 'Monitors security events and performs initial triage and analysis.' },
		{ name: 'Network Engineer', description: 'Manages network infrastructure and implements firewall and routing changes.' },
		{ name: 'Legal Representative', description: 'Advises on legal obligations including breach notification and regulatory requirements.' },
		{ name: 'PR / Communications', description: 'Manages internal and external messaging and media relations during the incident.' },
		{ name: 'IT Manager', description: 'Oversees IT systems operations and coordinates technical remediation efforts.' },
		{ name: 'Digital Forensics', description: 'Conducts evidence collection, forensic investigation and root-cause analysis.' },
		{ name: 'Business Continuity', description: 'Ensures critical business functions remain operational during the incident.' },
		{ name: 'Executive / CEO', description: 'Makes final escalation and go/no-go decisions on major response actions.' },
	];
	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle'
	});

	$effect(() => {
		data.background_color = custom_bg_color ? data.background_color : undefined;
	});
</script>

<div class="w-full h-full pb-20 px-20">
	<div class="rounded-lg bg-white w-full h-full border-gray-500 dark:bg-gray-700">
		<div class="h-fit bg-gray-300 rounded-t-lg dark:bg-gray-500">
			<div class="flex align-middle p-4 gap-3">
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-red-400 transition"
				></span>
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-yellow-400 transition"
				></span>
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-green-400 transition"
				></span>
			</div>
		</div>
		<div
			class="dark:bg-gray-700 h-full"
			style="background-repeat: no-repeat;background-size: 100% 100%;background-image: {data.background_image
				? `url("/api/v1/storage/download/${data.background_image}")`
				: `unset`}"
		>
			<div class="flex justify-center pt-10 w-full">
				{#await import('$lib/inline-editor.svelte')}
					<Spinner my_20={false} />
				{:then c}
					<c.default bind:text={data.title} />
				{/await}
			</div>
			<div class="flex justify-center pt-10 w-full max-h-32">
				<textarea
					placeholder="Description"
					bind:value={data.description}
					class="p-3 rounded-lg border-gray-500 border text-center w-1/3 h-20 resize-none dark:bg-gray-500 outline-hidden focus:shadow-2xl transition-all"
				></textarea>
			</div>

			{#if data.cover_image != undefined && data.cover_image !== ''}
				<div class="flex justify-center pt-10 w-full max-h-72">
					<img
						src="/api/v1/storage/download/{data.cover_image}"
						alt="not available"
						class="max-h-72 h-auto w-auto"
						oncontextmenu={(e: Event) => {
							e.preventDefault();
							data.cover_image = null;
						}}
					/>
				</div>
			{:else}
				{#await import('$lib/editor/uploader.svelte')}
					<Spinner my_20={false} />
				{:then c}
					<c.default bind:modalOpen={uppyOpen} {data} video_upload={false} />
				{/await}
			{/if}
			<div class="pt-10 w-full flex justify-center">
				<button
					type="button"
					onclick={() => {
						data.public = !data.public;
					}}
					class="text-center w-fit"
				>
					{#if data.public}
						<svg
							class="w-8 h-8 inline-block"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						<span>{$t('words.public')}</span>
					{:else}
						<svg
							class="w-8 h-8 inline-block"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
							/>
						</svg>
						<span>{$t('words.private')}</span>
					{/if}
				</button>
			</div>
			<div class="pt-10 w-full flex justify-center">
				<div class="grid grid-cols-3 w-fit h-fit gap-4">
					<div
						class="max-w-full transition-all"
						class:opacity-50={custom_bg_color}
						use:tippy={{ content: 'use the standard background', placement: 'left' }}
					>
						<div
							class="bg-gray-200 rounded-lg w-full h-full p-1"
							class:pointer-events-none={custom_bg_color}
						>
							<span class="inline-block w-full h-full bg-[#d6edc9] dark:bg-[#4e6e58]"
							></span>
						</div>
					</div>
					<div>
						<label
							for="large-toggle"
							class="inline-flex relative items-center cursor-pointer"
						>
							<input
								type="checkbox"
								bind:checked={custom_bg_color}
								id="large-toggle"
								class="sr-only peer"
							/>
							<span
								class="w-14 h-7 bg-gray-200 peer-focus:outline-hidden peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-800 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"
							></span>
						</label>
					</div>
					<div
						class:opacity-50={!custom_bg_color}
						class="transition-all"
						use:tippy={{ content: 'Use your own background color', placement: 'right' }}
					>
						<input
							class:pointer-events-none={!custom_bg_color}
							type="color"
							class="rounded-lg p-1 min-h-full hover:cursor-pointer border-black border"
							bind:value={data.background_color}
						/>
					</div>
				</div>
			</div>
			<div class="flex justify-center pt-10">
				<h3>{$t('editor.bg_image')}</h3>
			</div>
			<div class="w-full flex justify-center -mt-8">
				{#if data.background_image}
					<button
						onclick={() => {
							data.background_image = undefined;
						}}
						class="mt-10 bg-red-500 p-2 rounded-lg border-2 border-black transition hover:bg-red-400"
						>Remove Background-Image
					</button>
				{:else}
					{#await import('$lib/editor/uploader.svelte')}
						<div class="pt-10">
							<Spinner my_20={false} />
						</div>
					{:then c}
						<c.default
							bind:modalOpen={bg_uppy_open}
							{data}
							selected_question={-1}
							video_upload={false}
						/>
					{/await}
				{/if}
			</div>
			<!-- Scenario Type & Roles (Tabletop) -->
			<div class="flex justify-center pt-10">
				<h3>Scenario Type</h3>
			</div>
			<div class="pt-4 w-full flex justify-center">
				<div class="flex items-center gap-4">
					<span class="text-sm" class:font-semibold={data.scenario_type !== 'tabletop'}>Classic Quiz</span>
					<label for="scenario-toggle" class="inline-flex relative items-center cursor-pointer">
						<input
							type="checkbox"
							checked={data.scenario_type === 'tabletop'}
							onchange={() => {
								data.scenario_type = data.scenario_type === 'tabletop' ? undefined : 'tabletop';
								if (data.scenario_type === 'tabletop' && !data.roles) {
									data.roles = [];
								}
							}}
							id="scenario-toggle"
							class="sr-only peer"
						/>
						<span class="w-14 h-7 bg-gray-200 peer-focus:outline-hidden peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-800 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all dark:border-gray-600 peer-checked:bg-teal-600"></span>
					</label>
					<span class="text-sm" class:font-semibold={data.scenario_type === 'tabletop'}>Tabletop Exercise</span>
				</div>
			</div>
			{#if data.scenario_type === 'tabletop'}
				<div class="flex justify-center pt-6">
					<h3>Roles</h3>
				</div>
				<!-- Predefined templates -->
				<div class="pt-2 w-full flex flex-col items-center gap-2">
					<p class="text-xs text-gray-500 dark:text-gray-400">Quick-add from templates:</p>
					<div class="flex flex-wrap gap-1.5 justify-center max-w-lg">
						{#each ROLE_TEMPLATES as tpl}
							{@const already = (data.roles ?? []).includes(tpl.name)}
							<button
								type="button"
								disabled={already}
								onclick={() => {
									if (!already) {
										data.roles = [...(data.roles ?? []), tpl.name];
										data.role_descriptions = { ...(data.role_descriptions ?? {}), [tpl.name]: tpl.description };
									}
								}}
								class="rounded-full px-2.5 py-1 text-xs border transition"
								class:bg-teal-600={already}
								class:text-white={already}
								class:border-teal-600={already}
								class:opacity-50={already}
								class:cursor-not-allowed={already}
								class:border-gray-400={!already}
								class:hover:bg-teal-50={!already}
								title={tpl.description}
							>
								{tpl.name}
							</button>
						{/each}
					</div>
				</div>
				<!-- Current roles list with description expand -->
				<div class="pt-4 w-full flex justify-center">
					<div class="flex flex-col items-center gap-2 w-full max-w-lg">
						{#each data.roles ?? [] as role, i}
							<div class="w-full rounded-lg border border-gray-300 dark:border-gray-600 p-2 flex flex-col gap-1">
								<div class="flex items-center gap-2">
									<span class="flex-1 px-2 py-0.5 rounded-full bg-teal-600 text-white text-sm">{role}</span>
									<button
										type="button"
										class="text-xs text-gray-500 hover:text-teal-600 px-1"
										onclick={() => { expanded_role_desc = expanded_role_desc === role ? null : role; }}
									>{expanded_role_desc === role ? '▲ desc' : '▼ desc'}</button>
									<button
										type="button"
										class="text-red-400 hover:text-red-600 text-base leading-none"
										onclick={() => {
											data.roles = (data.roles ?? []).filter((_, idx) => idx !== i);
											const descs = { ...(data.role_descriptions ?? {}) };
											delete descs[role];
											data.role_descriptions = descs;
										}}
									>&times;</button>
								</div>
								{#if expanded_role_desc === role}
									<textarea
										rows="2"
										placeholder="Role description (shown to participants)"
										value={(data.role_descriptions ?? {})[role] ?? ''}
										oninput={(e) => {
											data.role_descriptions = { ...(data.role_descriptions ?? {}), [role]: e.currentTarget.value };
										}}
										class="w-full rounded border border-gray-300 dark:border-gray-600 p-1.5 text-xs dark:bg-gray-700 outline-none resize-y"
									></textarea>
								{/if}
							</div>
						{/each}
						<!-- Add custom role -->
						<div class="flex gap-2 w-full mt-1">
							<input
								type="text"
								bind:value={new_role_input}
								placeholder="Custom role name"
								class="flex-1 rounded-lg border border-gray-400 p-1.5 text-sm dark:bg-gray-600 outline-hidden"
								onkeydown={(e) => {
									if (e.key === 'Enter') {
										e.preventDefault();
										const v = new_role_input.trim();
										if (v && !(data.roles ?? []).includes(v)) {
											data.roles = [...(data.roles ?? []), v];
											if (new_role_desc_input.trim()) {
												data.role_descriptions = { ...(data.role_descriptions ?? {}), [v]: new_role_desc_input.trim() };
												new_role_desc_input = '';
											}
											new_role_input = '';
											expanded_role_desc = v;
										}
									}
								}}
							/>
							<input
								type="text"
								bind:value={new_role_desc_input}
								placeholder="Optional description"
								class="flex-1 rounded-lg border border-gray-400 p-1.5 text-sm dark:bg-gray-600 outline-hidden"
							/>
							<button
								type="button"
								class="rounded-lg bg-teal-600 px-3 py-1.5 text-sm text-white hover:bg-teal-700"
								onclick={() => {
									const v = new_role_input.trim();
									if (v && !(data.roles ?? []).includes(v)) {
										data.roles = [...(data.roles ?? []), v];
										if (new_role_desc_input.trim()) {
											data.role_descriptions = { ...(data.role_descriptions ?? {}), [v]: new_role_desc_input.trim() };
											new_role_desc_input = '';
										}
										new_role_input = '';
										expanded_role_desc = v;
									}
								}}
							>Add</button>
						</div>
					</div>
				</div>
				<!-- Injects Editor -->
				<div class="flex justify-center pt-6">
					<h3>Injects</h3>
				</div>
				<div class="pt-2 w-full flex justify-center">
					<div class="flex flex-col items-center gap-3 w-2/3">
						{#each data.injects ?? [] as inject, i}
							<div class="w-full rounded-lg border p-3 dark:border-gray-500 flex flex-col gap-2"
								class:border-blue-400={inject.severity === 'info'}
								class:border-yellow-400={inject.severity === 'warning'}
								class:border-red-400={inject.severity === 'critical'}
							>
								<div class="flex gap-2 items-center">
									<input
										type="text"
										bind:value={inject.title}
										placeholder="Inject title"
										class="flex-1 rounded-lg border border-gray-400 p-1.5 text-sm dark:bg-gray-600 outline-hidden"
									/>
									<select
										bind:value={inject.severity}
										class="rounded-lg border border-gray-400 p-1.5 text-sm dark:bg-gray-600 outline-hidden"
									>
										<option value="info">Info</option>
										<option value="warning">Warning</option>
										<option value="critical">Critical</option>
									</select>
									<button
										type="button"
										class="text-red-500 hover:text-red-700 text-lg"
										onclick={() => {
											data.injects = (data.injects ?? []).filter((_, idx) => idx !== i);
										}}
									>&times;</button>
								</div>
								<textarea
									bind:value={inject.content}
									placeholder="Inject content (markdown)"
									class="w-full rounded-lg border border-gray-400 p-1.5 text-sm dark:bg-gray-600 outline-hidden resize-y min-h-[60px]"
								></textarea>
								<div class="flex gap-2 items-center">
									<span class="text-xs text-gray-500">Auto-trigger after:</span>
									<select
										class="rounded-lg border border-gray-400 p-1.5 text-xs dark:bg-gray-600 outline-hidden"
										value={inject.trigger_after_question_id ?? ''}
										onchange={(e) => {
											inject.trigger_after_question_id = e.currentTarget.value || undefined;
											data = data;
										}}
									>
										<option value="">Manual only</option>
										{#each data.questions as q, qi}
											<option value={q.id ?? ''}>{qi + 1}. {q.question?.replace(/<[^>]*>/g, '').slice(0, 30) || 'Untitled'}</option>
										{/each}
									</select>
								</div>
							</div>
						{/each}
						<button
							type="button"
							class="rounded-lg bg-teal-600 px-4 py-2 text-sm text-white hover:bg-teal-700"
							onclick={() => {
								const newInject: Inject = {
									id: crypto.randomUUID(),
									title: '',
									content: '',
									severity: 'info'
								};
								data.injects = [...(data.injects ?? []), newInject];
							}}
						>+ Add Inject</button>
					</div>
				</div>
			{/if}			<!-- Master Slide Theme -->
			<div class="flex justify-center pt-8">
				<h3>Master Slide Theme</h3>
			</div>
			<div class="pt-4 w-full flex justify-center">
				<div class="flex flex-col gap-3 w-full max-w-lg">
					<p class="text-xs text-gray-500 dark:text-gray-400">Define default colours applied to all slides. Per-slide overrides take precedence.</p>
					<div class="grid grid-cols-2 gap-3">
						<label class="flex flex-col gap-1 text-xs">
							<span>Background colour</span>
							<div class="flex items-center gap-2">
								<input
									type="color"
									class="h-8 w-12 rounded border border-gray-400 cursor-pointer p-0.5"
									value={data.master_theme?.background_color ?? '#ffffff'}
									oninput={(e) => { data.master_theme = { ...(data.master_theme ?? {}), background_color: e.currentTarget.value }; }}
								/>
								<button
									type="button"
									class="text-xs text-gray-400 hover:text-red-500"
									onclick={() => {
										if (data.master_theme) {
											data.master_theme = { ...data.master_theme, background_color: undefined };
										}
									}}
								>clear</button>
							</div>
						</label>
						<label class="flex flex-col gap-1 text-xs">
							<span>Text colour</span>
							<div class="flex items-center gap-2">
								<input
									type="color"
									class="h-8 w-12 rounded border border-gray-400 cursor-pointer p-0.5"
									value={data.master_theme?.text_color ?? '#111111'}
									oninput={(e) => { data.master_theme = { ...(data.master_theme ?? {}), text_color: e.currentTarget.value }; }}
								/>
								<button
									type="button"
									class="text-xs text-gray-400 hover:text-red-500"
									onclick={() => {
										if (data.master_theme) {
											data.master_theme = { ...data.master_theme, text_color: undefined };
										}
									}}
								>clear</button>
							</div>
						</label>
						<label class="flex flex-col gap-1 text-xs">
							<span>Accent colour</span>
							<div class="flex items-center gap-2">
								<input
									type="color"
									class="h-8 w-12 rounded border border-gray-400 cursor-pointer p-0.5"
									value={data.master_theme?.accent_color ?? '#B07156'}
									oninput={(e) => { data.master_theme = { ...(data.master_theme ?? {}), accent_color: e.currentTarget.value }; }}
								/>
								<button
									type="button"
									class="text-xs text-gray-400 hover:text-red-500"
									onclick={() => {
										if (data.master_theme) {
											data.master_theme = { ...data.master_theme, accent_color: undefined };
										}
									}}
								>clear</button>
							</div>
						</label>
						<label class="flex flex-col gap-1 text-xs">
							<span>Font family</span>
							<select
								class="rounded-lg border border-gray-400 p-1.5 text-sm dark:bg-gray-600 outline-hidden"
								value={data.master_theme?.font_family ?? ''}
								onchange={(e) => { data.master_theme = { ...(data.master_theme ?? {}), font_family: e.currentTarget.value || undefined }; }}
							>
								<option value="">Default</option>
								<option value="serif">Serif</option>
								<option value="monospace">Monospace</option>
								<option value="'Inter', sans-serif">Inter</option>
								<option value="'Georgia', serif">Georgia</option>
							</select>
						</label>
					</div>
					{#if Object.values(data.master_theme ?? {}).some(Boolean)}
						<button
							type="button"
							class="mt-1 rounded-lg border border-gray-300 px-3 py-1 text-xs text-gray-500 hover:text-red-500 hover:border-red-300 w-fit"
							onclick={() => { data.master_theme = undefined; }}
						>Clear master theme</button>
					{/if}
				</div>
			</div>		</div>
	</div>
</div>
