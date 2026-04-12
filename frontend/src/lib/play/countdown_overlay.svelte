<!--
SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { browser } from '$app/environment';
	import CircularProgress from '$lib/play/circular_progress.svelte';
	import { onDestroy } from 'svelte';

	interface Props {
		active: boolean;
		remaining_seconds: number;
		total_seconds: number;
		label?: string;
	}

	let { active, remaining_seconds, total_seconds, label = 'Starting in' }: Props = $props();
	let sound_on = $state(true);
	let last_beep_second = $state<number | null>(null);
	let number_pop = $state(false);
	let flare_pulse = $state(false);
	let orbit_angle = $state(0);
	let raf_id: number | null = null;
	let progress_glow = $state(0);
	let go_burst_active = $state(false);
	let go_particles = $state<Array<{ id: number; x: number; y: number; size: number; delay: number }>>([]);
	let go_burst_timeout: ReturnType<typeof setTimeout> | null = null;

	const progress = $derived(total_seconds > 0 ? Math.max(0, Math.min(1, remaining_seconds / total_seconds)) : 0);
	const display_seconds = $derived(Math.max(0, Math.ceil(remaining_seconds)));
	const urgency_color = $derived(display_seconds <= 2 ? '#ef4444' : display_seconds <= 3 ? '#f59e0b' : '#14b8a6');
	const progress_percent = $derived(Math.round(progress * 100));

	const beep = () => {
		if (!browser || !sound_on || display_seconds <= 0) {
			return;
		}
		const Ctx = window.AudioContext || (window as any).webkitAudioContext;
		if (!Ctx) {
			return;
		}
		const ctx = new Ctx();
		const oscillator = ctx.createOscillator();
		const gain = ctx.createGain();
		oscillator.type = 'square';
		oscillator.frequency.value = 880;
		gain.gain.value = 0.05;
		oscillator.connect(gain);
		gain.connect(ctx.destination);
		oscillator.start();
		oscillator.stop(ctx.currentTime + 0.07);
	};

	const trigger_tick_animation = () => {
		number_pop = true;
		flare_pulse = true;
		progress_glow = progress_percent;
		setTimeout(() => {
			number_pop = false;
		}, 180);
		setTimeout(() => {
			flare_pulse = false;
		}, 280);
	};

	const trigger_go_burst = () => {
		if (go_burst_active) {
			return;
		}
		go_particles = Array.from({ length: 18 }, (_, idx) => ({
			id: idx,
			x: Math.round((Math.random() - 0.5) * 180),
			y: Math.round((Math.random() - 0.5) * 120),
			size: Math.round(6 + Math.random() * 10),
			delay: Number((Math.random() * 0.12).toFixed(2))
		}));
		go_burst_active = true;
		if (go_burst_timeout) {
			clearTimeout(go_burst_timeout);
		}
		go_burst_timeout = setTimeout(() => {
			go_burst_active = false;
			go_particles = [];
		}, 700);
	};

	const start_orbit_animation = () => {
		if (!browser || raf_id !== null) {
			return;
		}
		const animate = () => {
			orbit_angle = (orbit_angle + 1.8) % 360;
			raf_id = requestAnimationFrame(animate);
		};
		raf_id = requestAnimationFrame(animate);
	};

	const stop_orbit_animation = () => {
		if (raf_id !== null && browser) {
			cancelAnimationFrame(raf_id);
			raf_id = null;
		}
	};

	$effect(() => {
		if (active) {
			start_orbit_animation();
		} else {
			stop_orbit_animation();
		}
	});

	$effect(() => {
		if (!active || !sound_on) {
			last_beep_second = null;
			return;
		}
		if (display_seconds !== last_beep_second) {
			last_beep_second = display_seconds;
			beep();
			trigger_tick_animation();
			if (display_seconds === 0) {
				trigger_go_burst();
			}
		}
	});

	onDestroy(() => {
		stop_orbit_animation();
		if (go_burst_timeout) {
			clearTimeout(go_burst_timeout);
			go_burst_timeout = null;
		}
	});
</script>

{#if active || go_burst_active}
	<div class="pointer-events-none fixed inset-x-0 top-0 z-[70] p-4 sm:p-6">
		<div class="countdown-shell mx-auto w-full max-w-3xl rounded-2xl border border-white/40 bg-black/55 px-4 py-3 text-white shadow-2xl backdrop-blur">
			<div
				class="countdown-track"
				style="width: {progress_percent}%; box-shadow: 0 0 20px color-mix(in oklab, {urgency_color} 65%, transparent);"
			></div>
			<div class="relative flex items-center gap-4">
				<div class="pointer-events-auto relative">
					<div
						class="countdown-orbit"
						style="--orbit-angle:{orbit_angle}deg; --orbit-color:{urgency_color};"
					></div>
					<div class:tick-pop={number_pop} class:flare-ring={flare_pulse} class="relative z-10">
						<CircularProgress progress={progress} text={String(display_seconds)} color={urgency_color} />
					</div>
				</div>
				<div class="min-w-0 flex-1">
					<p class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-200">{label}</p>
					<p class="mt-1 text-2xl font-semibold" style="color: {urgency_color};">{display_seconds}</p>
					<p class="mt-1 text-xs text-white/80">Get ready, first question unlocks right after zero.</p>
				</div>
				<button
					type="button"
					class="pointer-events-auto rounded-lg border border-white/40 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em]"
					onclick={() => {
						sound_on = !sound_on;
					}}
				>
					{sound_on ? 'Tick on' : 'Tick off'}
				</button>
			</div>
		</div>
		{#if go_burst_active}
			<div class="go-burst-layer">
				<p class="go-burst-text">GO!</p>
				{#each go_particles as particle}
					<span
						class="go-particle"
						style="--x:{particle.x}px; --y:{particle.y}px; --s:{particle.size}px; --d:{particle.delay}s;"
					></span>
				{/each}
			</div>
		{/if}
	</div>
{/if}

<style>
	.countdown-shell {
		position: relative;
		overflow: hidden;
	}

	.countdown-track {
		position: absolute;
		left: 0;
		top: 0;
		height: 3px;
		background: linear-gradient(90deg, rgba(20, 184, 166, 0.2), rgba(20, 184, 166, 0.9));
		transition: width 120ms linear;
	}

	.countdown-orbit {
		position: absolute;
		inset: -10px;
		border-radius: 9999px;
		background:
			radial-gradient(circle at 50% 0%, var(--orbit-color), transparent 28%),
			radial-gradient(circle at 100% 50%, color-mix(in oklab, var(--orbit-color) 75%, white 20%), transparent 30%),
			radial-gradient(circle at 50% 100%, var(--orbit-color), transparent 28%),
			radial-gradient(circle at 0% 50%, color-mix(in oklab, var(--orbit-color) 75%, white 20%), transparent 30%);
		opacity: 0.45;
		transform: rotate(var(--orbit-angle));
		filter: blur(1px);
	}

	.tick-pop {
		animation: tickPop 180ms ease-out;
	}

	.flare-ring::after {
		content: '';
		position: absolute;
		inset: -10px;
		border-radius: 9999px;
		border: 2px solid rgba(255, 255, 255, 0.7);
		animation: flarePulse 260ms ease-out;
	}

	@keyframes tickPop {
		0% {
			transform: scale(1);
		}
		45% {
			transform: scale(1.14);
		}
		100% {
			transform: scale(1);
		}
	}

	@keyframes flarePulse {
		0% {
			opacity: 0.9;
			transform: scale(0.8);
		}
		100% {
			opacity: 0;
			transform: scale(1.25);
		}
	}

	.go-burst-layer {
		position: absolute;
		inset: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		pointer-events: none;
	}

	.go-burst-text {
		font-size: clamp(2.2rem, 5.4vw, 3.8rem);
		font-weight: 800;
		letter-spacing: 0.12em;
		color: #ffffff;
		text-shadow:
			0 0 22px rgba(20, 184, 166, 0.85),
			0 0 40px rgba(14, 165, 233, 0.55);
		animation: goBurstText 620ms cubic-bezier(0.2, 0.9, 0.18, 1) forwards;
	}

	.go-particle {
		position: absolute;
		width: var(--s);
		height: var(--s);
		border-radius: 9999px;
		background: radial-gradient(circle at 30% 30%, #ffffff, #14b8a6 62%, #0ea5e9 100%);
		opacity: 0;
		animation: goParticle 620ms ease-out forwards;
		animation-delay: var(--d);
	}

	@keyframes goBurstText {
		0% {
			opacity: 0;
			transform: scale(0.4) translateY(8px);
		}
		30% {
			opacity: 1;
			transform: scale(1.08) translateY(0);
		}
		100% {
			opacity: 0;
			transform: scale(1.22) translateY(-8px);
		}
	}

	@keyframes goParticle {
		0% {
			opacity: 0;
			transform: translate(0, 0) scale(0.4);
		}
		20% {
			opacity: 0.9;
		}
		100% {
			opacity: 0;
			transform: translate(var(--x), var(--y)) scale(1.05);
		}
	}
</style>
