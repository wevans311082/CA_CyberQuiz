<!--
SPDX-FileCopyrightText: 2025

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { fade } from 'svelte/transition';

	interface AvatarParams {
		skin_color: number;
		hair_color: number;
		facial_hair_type: number;
		facial_hair_color: number;
		top_type: number;
		hat_color: number;
		mouth_type: number;
		eyebrow_type: number;
		nose_type: number;
		accessories_type: number;
		clothe_type: number;
		clothe_color: number;
		clothe_graphic_type: number;
	}

	interface Props {
		avatar_params: AvatarParams;
		onconfirm: () => void;
		confirmed: boolean;
	}

	let { avatar_params = $bindable(), onconfirm, confirmed = $bindable() }: Props = $props();

	// -- Category definitions --
	type Category = {
		key: string;
		label: string;
		icon: string;
		options: { value: number; label: string; preview?: string }[];
		paramKey: keyof AvatarParams;
	};

	const skinTones: { value: number; label: string; color: string }[] = [
		{ value: 0, label: 'Dark', color: '#614335' },
		{ value: 1, label: 'Tanned', color: '#D08B5B' },
		{ value: 2, label: 'Yellow', color: '#F8D25C' },
		{ value: 3, label: 'Pale', color: '#FFDBB4' },
		{ value: 4, label: 'Light', color: '#EDB98A' },
		{ value: 5, label: 'Brown', color: '#AE5D29' },
		{ value: 6, label: 'Dark Brown', color: '#4A312C' }
	];

	const hairColors: { value: number; label: string; color: string }[] = [
		{ value: 0, label: 'Black', color: '#2C1B18' },
		{ value: 1, label: 'Auburn', color: '#A55728' },
		{ value: 2, label: 'Blonde', color: '#B58143' },
		{ value: 3, label: 'Golden', color: '#D6B370' },
		{ value: 4, label: 'Brown', color: '#724133' },
		{ value: 5, label: 'Dark Brown', color: '#4A312C' },
		{ value: 6, label: 'Pink', color: '#F59797' },
		{ value: 7, label: 'Platinum', color: '#ECDCBF' },
		{ value: 8, label: 'Red', color: '#C93305' },
		{ value: 9, label: 'Silver', color: '#B1B1B1' }
	];

	const clotheColors: { value: number; label: string; color: string }[] = [
		{ value: 0, label: 'Black', color: '#262E33' },
		{ value: 1, label: 'Blue', color: '#65C9FF' },
		{ value: 2, label: 'Navy', color: '#5199E4' },
		{ value: 3, label: 'Royal', color: '#25557C' },
		{ value: 4, label: 'Grey', color: '#929598' },
		{ value: 5, label: 'Dark Grey', color: '#3C4F5C' },
		{ value: 6, label: 'Heather', color: '#B1E2FF' },
		{ value: 7, label: 'Pastel Blue', color: '#A7DBD8' },
		{ value: 8, label: 'Pastel Green', color: '#E0E4CC' },
		{ value: 9, label: 'Pastel Orange', color: '#FF6B35' },
		{ value: 10, label: 'Pastel Red', color: '#FF5C5C' },
		{ value: 11, label: 'Pastel Yellow', color: '#FCDA79' },
		{ value: 12, label: 'Pink', color: '#FF488E' },
		{ value: 13, label: 'Red', color: '#FF5C5C' },
		{ value: 14, label: 'White', color: '#FFFFFF' }
	];

	// Hair styles grouped by type
	const femaleHairStyles = [
		{ value: 9, label: 'Big Hair' },
		{ value: 10, label: 'Bob' },
		{ value: 11, label: 'Bun' },
		{ value: 12, label: 'Curly' },
		{ value: 13, label: 'Curvy' },
		{ value: 15, label: 'Frida' },
		{ value: 16, label: 'Fro' },
		{ value: 17, label: 'Fro Band' },
		{ value: 18, label: 'Medium' },
		{ value: 19, label: 'Mia Wallace' },
		{ value: 21, label: 'Straight' },
		{ value: 22, label: 'Straight 2' },
		{ value: 23, label: 'Strand' }
	];

	const maleHairStyles = [
		{ value: 0, label: 'Bald' },
		{ value: 14, label: 'Dreads (Long)' },
		{ value: 20, label: 'Shaved Sides' },
		{ value: 24, label: 'Dreads 1' },
		{ value: 25, label: 'Dreads 2' },
		{ value: 26, label: 'Frizzle' },
		{ value: 27, label: 'Shaggy' },
		{ value: 28, label: 'Short Curly' },
		{ value: 29, label: 'Short Flat' },
		{ value: 30, label: 'Short Round' },
		{ value: 31, label: 'Short Waved' },
		{ value: 32, label: 'Sides' },
		{ value: 33, label: 'Caesar' },
		{ value: 34, label: 'Caesar Side' }
	];

	const headwearStyles = [
		{ value: 1, label: 'Eye Patch' },
		{ value: 2, label: 'Hat' },
		{ value: 3, label: 'Hijab' },
		{ value: 4, label: 'Turban' },
		{ value: 5, label: 'Winter Hat 1' },
		{ value: 6, label: 'Winter Hat 2' },
		{ value: 7, label: 'Winter Hat 3' },
		{ value: 8, label: 'Winter Hat 4' }
	];

	const facialHairOptions = [
		{ value: 0, label: 'None' },
		{ value: 1, label: 'Medium Beard' },
		{ value: 2, label: 'Light Beard' },
		{ value: 3, label: 'Majestic Beard' },
		{ value: 4, label: 'Fancy Moustache' },
		{ value: 5, label: 'Magnum Moustache' }
	];

	const mouthOptions = [
		{ value: 0, label: 'Default' },
		{ value: 8, label: 'Smile' },
		{ value: 10, label: 'Twinkle' },
		{ value: 9, label: 'Tongue' },
		{ value: 7, label: 'Serious' },
		{ value: 1, label: 'Concerned' },
		{ value: 5, label: 'Sad' },
		{ value: 4, label: 'Grimace' },
		{ value: 3, label: 'Eating' },
		{ value: 2, label: 'Disbelief' },
		{ value: 6, label: 'Scream' },
		{ value: 11, label: 'Vomit' }
	];

	const eyebrowOptions = [
		{ value: 0, label: 'Default' },
		{ value: 1, label: 'Natural' },
		{ value: 5, label: 'Raised' },
		{ value: 6, label: 'Raised Natural' },
		{ value: 4, label: 'Flat' },
		{ value: 2, label: 'Angry' },
		{ value: 3, label: 'Angry Natural' },
		{ value: 7, label: 'Sad' },
		{ value: 8, label: 'Sad Natural' },
		{ value: 9, label: 'Unibrow' },
		{ value: 10, label: 'Up Down' },
		{ value: 11, label: 'Up Down Natural' },
		{ value: 12, label: 'Frown' }
	];

	const accessoryOptions = [
		{ value: 0, label: 'None' },
		{ value: 1, label: 'Kurt' },
		{ value: 2, label: 'Glasses 1' },
		{ value: 3, label: 'Glasses 2' },
		{ value: 4, label: 'Round' },
		{ value: 5, label: 'Sunglasses' },
		{ value: 6, label: 'Wayfarers' }
	];

	const clotheOptions = [
		{ value: 0, label: 'Blazer + Shirt' },
		{ value: 1, label: 'Blazer + Sweater' },
		{ value: 2, label: 'Collar Sweater' },
		{ value: 3, label: 'Graphic Shirt' },
		{ value: 4, label: 'Hoodie' },
		{ value: 5, label: 'Overall' },
		{ value: 6, label: 'Crew Neck' },
		{ value: 7, label: 'Scoop Neck' },
		{ value: 8, label: 'V-Neck' }
	];

	const graphicOptions = [
		{ value: 0, label: 'Bat' },
		{ value: 1, label: 'Cumbia' },
		{ value: 2, label: 'Deer' },
		{ value: 3, label: 'Diamond' },
		{ value: 4, label: 'Hola' },
		{ value: 5, label: 'Pizza' },
		{ value: 6, label: 'Resist' },
		{ value: 7, label: 'Selena' },
		{ value: 8, label: 'Bear' },
		{ value: 9, label: 'Skull Outline' },
		{ value: 10, label: 'Skull' }
	];

	// Tabs
	const tabs = [
		{ id: 'style', label: 'Style', icon: '✂️' },
		{ id: 'face', label: 'Face', icon: '😊' },
		{ id: 'outfit', label: 'Outfit', icon: '👕' }
	];

	let activeTab = $state('style');
	let hairGender = $state<'female' | 'male' | 'headwear'>('female');

	const getPreviewUrl = (params: Record<string, number>) => {
		const merged = { ...avatar_params, ...params };
		return `/api/v1/avatar/custom?${new URLSearchParams(
			Object.fromEntries(Object.entries(merged).map(([k, v]) => [k, String(v)]))
		).toString()}`;
	};

	const avatarPreviewUrl = $derived(
		`/api/v1/avatar/custom?${new URLSearchParams(
			Object.fromEntries(Object.entries(avatar_params).map(([k, v]) => [k, String(v)]))
		).toString()}`
	);

	const setParam = (key: keyof AvatarParams, value: number) => {
		avatar_params = { ...avatar_params, [key]: value };
		confirmed = false;
	};

	const randomize = () => {
		avatar_params = {
			skin_color: Math.floor(Math.random() * 7),
			hair_color: Math.floor(Math.random() * 10),
			facial_hair_type: Math.floor(Math.random() * 6),
			facial_hair_color: Math.floor(Math.random() * 10),
			top_type: Math.floor(Math.random() * 35),
			hat_color: Math.floor(Math.random() * 15),
			mouth_type: Math.floor(Math.random() * 12),
			eyebrow_type: Math.floor(Math.random() * 13),
			nose_type: 0,
			accessories_type: Math.floor(Math.random() * 7),
			clothe_type: Math.floor(Math.random() * 9),
			clothe_color: Math.floor(Math.random() * 15),
			clothe_graphic_type: Math.floor(Math.random() * 11)
		};
		confirmed = false;
	};
</script>

<div class="rounded-2xl border border-slate-300 bg-white/90 shadow-md dark:border-slate-700 dark:bg-slate-950/80 overflow-hidden" transition:fade>
	<!-- Header with preview -->
	<div class="flex items-center gap-4 border-b border-slate-200 px-4 py-3 dark:border-slate-700">
		<img
			src={avatarPreviewUrl}
			alt="Avatar preview"
			class="h-20 w-20 rounded-full border-2 border-teal-500 bg-white shadow dark:bg-slate-900"
		/>
		<div class="flex-1">
			<p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">Your Avatar</p>
			<div class="mt-2 flex gap-2">
				<button
					class="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
					onclick={randomize}
				>
					🎲 Randomize
				</button>
				<button
					class="rounded-lg px-3 py-1.5 text-xs font-semibold transition {confirmed
						? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400'
						: 'bg-teal-600 text-white hover:bg-teal-700'}"
					onclick={onconfirm}
				>
					{confirmed ? '✓ Confirmed' : 'Confirm Avatar'}
				</button>
			</div>
		</div>
	</div>

	<!-- Tab bar -->
	<div class="flex border-b border-slate-200 dark:border-slate-700">
		{#each tabs as tab}
			<button
				class="flex-1 px-3 py-2 text-center text-xs font-semibold transition
					{activeTab === tab.id
						? 'border-b-2 border-teal-600 text-teal-700 dark:text-teal-400'
						: 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'}"
				onclick={() => (activeTab = tab.id)}
			>
				<span class="mr-1">{tab.icon}</span>{tab.label}
			</button>
		{/each}
	</div>

	<!-- Tab content -->
	<div class="max-h-72 overflow-y-auto p-3">
		{#if activeTab === 'style'}
			<!-- Skin Tone -->
			<div class="mb-4">
				<p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Skin Tone</p>
				<div class="flex flex-wrap gap-2">
					{#each skinTones as tone}
						<button
							class="h-8 w-8 rounded-full border-2 transition-transform hover:scale-110
								{avatar_params.skin_color === tone.value ? 'border-teal-500 ring-2 ring-teal-300 scale-110' : 'border-slate-300 dark:border-slate-600'}"
							style="background-color: {tone.color}"
							title={tone.label}
							onclick={() => setParam('skin_color', tone.value)}
						></button>
					{/each}
				</div>
			</div>

			<!-- Hair Style -->
			<div class="mb-4">
				<p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Hair Style</p>
				<div class="mb-2 flex gap-1">
					{#each [
						{ id: 'female' as const, label: '♀ Long' },
						{ id: 'male' as const, label: '♂ Short' },
						{ id: 'headwear' as const, label: '🎩 Headwear' }
					] as g}
						<button
							class="rounded-md px-2.5 py-1 text-xs font-medium transition
								{hairGender === g.id
									? 'bg-teal-600 text-white'
									: 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'}"
							onclick={() => (hairGender = g.id)}
						>
							{g.label}
						</button>
					{/each}
				</div>
				<div class="grid grid-cols-4 gap-1.5">
					{#each hairGender === 'female' ? femaleHairStyles : hairGender === 'male' ? maleHairStyles : headwearStyles as style}
						<button
							class="flex items-center justify-center rounded-lg border p-1 transition
								{avatar_params.top_type === style.value
									? 'border-teal-500 bg-teal-50 dark:bg-teal-900/30'
									: 'border-slate-200 hover:border-slate-400 dark:border-slate-700 dark:hover:border-slate-500'}"
							onclick={() => setParam('top_type', style.value)}
						>
							<img
								src={getPreviewUrl({ top_type: style.value })}
								alt={style.label}
								class="h-12 w-12"
								loading="lazy"
							/>
						</button>
					{/each}
				</div>
			</div>

			<!-- Hair Color -->
			<div class="mb-4">
				<p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Hair Colour</p>
				<div class="flex flex-wrap gap-2">
					{#each hairColors as hc}
						<button
							class="h-7 w-7 rounded-full border-2 transition-transform hover:scale-110
								{avatar_params.hair_color === hc.value ? 'border-teal-500 ring-2 ring-teal-300 scale-110' : 'border-slate-300 dark:border-slate-600'}"
							style="background-color: {hc.color}"
							title={hc.label}
							onclick={() => setParam('hair_color', hc.value)}
						></button>
					{/each}
				</div>
			</div>

		{:else if activeTab === 'face'}
			<!-- Facial Hair -->
			<div class="mb-4">
				<p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Facial Hair</p>
				<div class="grid grid-cols-3 gap-1.5">
					{#each facialHairOptions as opt}
						<button
							class="rounded-lg border px-2 py-1.5 text-xs font-medium transition
								{avatar_params.facial_hair_type === opt.value
									? 'border-teal-500 bg-teal-50 text-teal-700 dark:bg-teal-900/30 dark:text-teal-300'
									: 'border-slate-200 text-slate-600 hover:border-slate-400 dark:border-slate-700 dark:text-slate-300'}"
							onclick={() => setParam('facial_hair_type', opt.value)}
						>
							{opt.label}
						</button>
					{/each}
				</div>
			</div>

			<!-- Mouth -->
			<div class="mb-4">
				<p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Expression</p>
				<div class="grid grid-cols-4 gap-1.5">
					{#each mouthOptions as opt}
						<button
							class="rounded-lg border px-2 py-1.5 text-xs font-medium transition
								{avatar_params.mouth_type === opt.value
									? 'border-teal-500 bg-teal-50 text-teal-700 dark:bg-teal-900/30 dark:text-teal-300'
									: 'border-slate-200 text-slate-600 hover:border-slate-400 dark:border-slate-700 dark:text-slate-300'}"
							onclick={() => setParam('mouth_type', opt.value)}
						>
							{opt.label}
						</button>
					{/each}
				</div>
			</div>

			<!-- Eyebrows -->
			<div class="mb-4">
				<p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Eyebrows</p>
				<div class="grid grid-cols-3 gap-1.5">
					{#each eyebrowOptions as opt}
						<button
							class="rounded-lg border px-2 py-1.5 text-xs font-medium transition
								{avatar_params.eyebrow_type === opt.value
									? 'border-teal-500 bg-teal-50 text-teal-700 dark:bg-teal-900/30 dark:text-teal-300'
									: 'border-slate-200 text-slate-600 hover:border-slate-400 dark:border-slate-700 dark:text-slate-300'}"
							onclick={() => setParam('eyebrow_type', opt.value)}
						>
							{opt.label}
						</button>
					{/each}
				</div>
			</div>

			<!-- Accessories -->
			<div class="mb-4">
				<p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Eyewear</p>
				<div class="grid grid-cols-4 gap-1.5">
					{#each accessoryOptions as opt}
						<button
							class="rounded-lg border px-2 py-1.5 text-xs font-medium transition
								{avatar_params.accessories_type === opt.value
									? 'border-teal-500 bg-teal-50 text-teal-700 dark:bg-teal-900/30 dark:text-teal-300'
									: 'border-slate-200 text-slate-600 hover:border-slate-400 dark:border-slate-700 dark:text-slate-300'}"
							onclick={() => setParam('accessories_type', opt.value)}
						>
							{opt.label}
						</button>
					{/each}
				</div>
			</div>

		{:else if activeTab === 'outfit'}
			<!-- Clothing Type -->
			<div class="mb-4">
				<p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Clothing</p>
				<div class="grid grid-cols-3 gap-1.5">
					{#each clotheOptions as opt}
						<button
							class="rounded-lg border px-2 py-1.5 text-xs font-medium transition
								{avatar_params.clothe_type === opt.value
									? 'border-teal-500 bg-teal-50 text-teal-700 dark:bg-teal-900/30 dark:text-teal-300'
									: 'border-slate-200 text-slate-600 hover:border-slate-400 dark:border-slate-700 dark:text-slate-300'}"
							onclick={() => setParam('clothe_type', opt.value)}
						>
							{opt.label}
						</button>
					{/each}
				</div>
			</div>

			<!-- Clothing Color -->
			<div class="mb-4">
				<p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Clothing Colour</p>
				<div class="flex flex-wrap gap-2">
					{#each clotheColors as cc}
						<button
							class="h-7 w-7 rounded-full border-2 transition-transform hover:scale-110
								{avatar_params.clothe_color === cc.value ? 'border-teal-500 ring-2 ring-teal-300 scale-110' : 'border-slate-300 dark:border-slate-600'}"
							style="background-color: {cc.color}"
							title={cc.label}
							onclick={() => setParam('clothe_color', cc.value)}
						></button>
					{/each}
				</div>
			</div>

			<!-- Graphic (only visible for Graphic Shirt) -->
			{#if avatar_params.clothe_type === 3}
				<div class="mb-4">
					<p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Shirt Graphic</p>
					<div class="grid grid-cols-4 gap-1.5">
						{#each graphicOptions as opt}
							<button
								class="rounded-lg border px-2 py-1.5 text-xs font-medium transition
									{avatar_params.clothe_graphic_type === opt.value
										? 'border-teal-500 bg-teal-50 text-teal-700 dark:bg-teal-900/30 dark:text-teal-300'
										: 'border-slate-200 text-slate-600 hover:border-slate-400 dark:border-slate-700 dark:text-slate-300'}"
								onclick={() => setParam('clothe_graphic_type', opt.value)}
							>
								{opt.label}
							</button>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Hat Color (only visible for hat/headwear top_types) -->
			{#if [2, 5, 6, 7, 8].includes(avatar_params.top_type)}
				<div class="mb-4">
					<p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Hat Colour</p>
					<div class="flex flex-wrap gap-2">
						{#each clotheColors as cc}
							<button
								class="h-7 w-7 rounded-full border-2 transition-transform hover:scale-110
									{avatar_params.hat_color === cc.value ? 'border-teal-500 ring-2 ring-teal-300 scale-110' : 'border-slate-300 dark:border-slate-600'}"
								style="background-color: {cc.color}"
								title={cc.label}
								onclick={() => setParam('hat_color', cc.value)}
							></button>
						{/each}
					</div>
				</div>
			{/if}
		{/if}
	</div>
</div>
