<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { socket } from '$lib/socket';
	import SocketDiagnostics from '$lib/socket_diagnostics.svelte';
	import { onDestroy, onMount } from 'svelte';
	import { browser } from '$app/environment';
	import * as Sentry from '@sentry/browser';
	import { getLocalization } from '$lib/i18n';
	import Cookies from 'js-cookie';
	import BrownButton from '$lib/components/buttons/brown.svelte';

	const { t } = getLocalization();

	interface Props {
		game_pin: string;
		game_mode: any;
		username: any;
	}

	let {
		game_pin = $bindable(),
		game_mode = $bindable(),
		username = $bindable()
	}: Props = $props();
	let custom_field = $state();
	let custom_field_value = $state();
	let captcha_enabled = $state();
	let joinAttempted = $state(false);
	let joinStatus = $state('idle');
	let lastJoinPayload = $state<Record<string, unknown> | null>(null);
	let captchaCheckStatus = $state('idle');
	let usernameLength = $state(0);
	let submitCount = $state(0);

	let hcaptchaSitekey = import.meta.env.VITE_HCAPTCHA;

	let hcaptcha = {
		execute: async (_a, _b) => ({ response: '' }), // eslint-disable-line @typescript-eslint/no-unused-vars
		// eslint-disable-next-line @typescript-eslint/no-empty-function
		render: (_a, _b) => {} // eslint-disable-line @typescript-eslint/no-unused-vars
	};
	let hcaptchaWidgetID;

	onMount(() => {
		if (browser) {
			hcaptcha = window.hcaptcha;
			if (hcaptcha.render) {
				hcaptchaWidgetID = hcaptcha.render('hcaptcha', {
					sitekey: hcaptchaSitekey,
					size: 'invisible',
					theme: 'dark'
				});
			}
		}
	});

	onDestroy(() => {
		if (browser) {
			hcaptcha = {
				execute: async () => ({ response: '' }),
				// eslint-disable-next-line @typescript-eslint/no-empty-function
				render: () => {}
			};
		}
	});

	const set_game_pin = async () => {
		let process_var;
		try {
			process_var = process;
		} catch {
			process_var = { env: { API_URL: undefined } };
		}

		const res = await fetch(
			`${process_var.env.API_URL ?? ''}/api/v1/quiz/play/check_captcha/${game_pin}`
		);
		captchaCheckStatus = `status:${res.status}`;
		const json = await res.json();
		game_mode = json.game_mode;
		if (res.status === 200) {
			captcha_enabled = json.enabled;
			custom_field = json.custom_field;
		}
		if (res.status === 404) {
			/*			alertModal.set({
                open: true,
                title: 'Game not found',
                body: 'The game pin you entered seems invalid.'
            });*/
			if (browser) {
				alert('Game not found');
			}
			game_pin = '';
			return;
		}
		if (res.status !== 200) {
			/*			alertModal.set({
                open: true,
                body: `Unknown error with response-code ${res.status}`,
                title: 'Unknown Error'
            });*/
			alert('Unknown error');
			return;
		}
	};

	$effect(() => {
		if (game_pin.length > 5) {
			set_game_pin();
		}
	});

	socket.on('connect_error', (error) => {
		joinStatus = `connect_error:${error.message}`;
		console.error('Socket connection failed', error.message);
		if (browser) {
			alert('Live connection to the quiz server failed. Please reload and try again.');
		}
	});

	const setUsername = async (e: Event) => {
		e.preventDefault();
		submitCount += 1;
		usernameLength = username?.length ?? 0;
		if (username.length <= 3) {
			joinStatus = 'blocked:username_too_short';
			return;
		}
		joinAttempted = true;
		joinStatus = 'submitting';
		let captcha_resp: string;
		if (Cookies.get('kicked')) {
			joinStatus = 'blocked:kicked';
			console.log("%cYou're Banned!", 'font-size:6rem');
			return;
		}

		if (captcha_enabled) {
			if (hcaptchaSitekey) {
				try {
					const { response } = await hcaptcha.execute(hcaptchaWidgetID, {
						async: true
					});
					captcha_resp = response;
					lastJoinPayload = {
						username,
						game_pin,
						hasCaptcha: true,
						hasCustomField: custom_field ? custom_field_value !== undefined : false
					};
					joinStatus = 'emit:join_game';
					socket.emit('join_game', {
						username: username,
						game_pin: game_pin,
						captcha: captcha_resp,
						custom_field: custom_field ? custom_field_value : undefined
					});
				} catch (e) {
					joinStatus = 'captcha_failed';
					if (import.meta.env.VITE_SENTRY !== null) {
						Sentry.captureException(e);
					}
					/*					alertModal.set({
                        open: true,
                        body: "The captcha failed, which is normal, but most of the time it's fixed by reloading!",
                        title: 'Captcha failed'
                    });*/
					alert('Captcha failed!');
					window.location.reload();
				}
			} else if (import.meta.env.VITE_RECAPTCHA) {
				// eslint-disable-next-line no-undef
				grecaptcha.ready(() => {
					// eslint-disable-next-line no-undef
					grecaptcha
						.execute(import.meta.env.VITE_RECAPTCHA, { action: 'submit' })
						.then(function (token) {
							lastJoinPayload = {
								username,
								game_pin,
								hasCaptcha: true,
								hasCustomField: custom_field ? custom_field_value !== undefined : false
							};
							joinStatus = 'emit:join_game';
							socket.emit('join_game', {
								username: username,
								game_pin: game_pin,
								captcha: token,
								custom_field: custom_field ? custom_field_value : undefined
							});
						});
				});
			}
		} else {
			lastJoinPayload = {
				username,
				game_pin,
				hasCaptcha: false,
				hasCustomField: custom_field ? custom_field_value !== undefined : false
			};
			joinStatus = 'emit:join_game';
			socket.emit('join_game', {
				username: username,
				game_pin: game_pin,
				captcha: undefined,
				custom_field: custom_field ? custom_field_value : undefined
			});
		}
	};
	socket.on('joined_game', () => {
		joinStatus = 'joined_game';
	});
	socket.on('rejoined_game', () => {
		joinStatus = 'rejoined_game';
	});
	socket.on('username_already_exists', () => {
		joinStatus = 'username_already_exists';
	});
	socket.on('game_already_started', () => {
		joinStatus = 'game_already_started';
	});
	socket.on('game_not_found', () => {
		joinStatus = 'game_not_found';
		game_pin = '';
		if (browser) {
			alert('Game not found');
		}
	});
	socket.on('error', () => {
		joinStatus = 'socket_error';
	});
	$effect(() => {
		const cleaned = game_pin.replace(/\D/g, '');
		if (game_pin.replace(/\D/g, '') === game_pin) {
			return;
		}
		game_pin = cleaned;
	});

	const stepTitle = $derived(game_pin === '' || game_pin.length < 6 ? 'Enter Game PIN' : 'Choose Display Name');
	const stepDescription = $derived(
		game_pin === '' || game_pin.length < 6
			? 'Use the six-digit code provided by your host.'
			: 'This name will appear on the live leaderboard.'
	);
</script>

<svelte:head>
	{#if captcha_enabled && hcaptchaSitekey}
		<script src="https://js.hcaptcha.com/1/api.js" async defer></script>
	{/if}
	{#if import.meta.env.VITE_RECAPTCHA && captcha_enabled}
		<script
			src="https://www.google.com/recaptcha/api.js?render={import.meta.env.VITE_RECAPTCHA}"
		></script>
	{/if}
</svelte:head>

{#if game_pin === '' || game_pin.length < 6}
	<div class="flex min-h-[70vh] w-full flex-col justify-center px-6 py-10 sm:px-10">
		<form class="mx-auto flex w-full max-w-md flex-col justify-center">
			<p class="mb-3 text-center text-xs font-semibold uppercase tracking-[0.3em] text-teal-700 dark:text-cyan-300">
				{stepTitle}
			</p>
			<h2 class="text-center text-3xl font-semibold text-slate-950 dark:text-white">Join your quiz</h2>
			<p class="mt-3 text-center text-sm leading-6 text-slate-600 dark:text-slate-300">
				{stepDescription}
			</p>
			<input
				class="mt-6 self-center rounded-2xl border border-slate-300 bg-white px-4 py-4 text-center text-3xl font-semibold tracking-[0.4em] text-slate-950 shadow-sm outline-hidden transition-all focus:border-teal-600 focus:shadow-xl dark:border-slate-700 dark:bg-slate-950 dark:text-white"
				bind:value={game_pin}
				maxlength="6"
				inputmode="numeric"
			/>
			<div class="mt-5">
				<BrownButton disabled={game_pin.length < 6}>Continue</BrownButton>
			</div>
		</form>
	</div>
{:else}
	<div class="flex min-h-[70vh] w-full flex-col justify-center px-6 py-10 sm:px-10">
		<form onsubmit={setUsername} class="mx-auto flex w-full max-w-md flex-col justify-center">
			<p class="mb-3 text-center text-xs font-semibold uppercase tracking-[0.3em] text-teal-700 dark:text-cyan-300">
				{stepTitle}
			</p>
			<h2 class="text-center text-3xl font-semibold text-slate-950 dark:text-white">Almost there</h2>
			<p class="mt-3 text-center text-sm leading-6 text-slate-600 dark:text-slate-300">
				{stepDescription}
			</p>
			<input
				class="mt-6 self-center rounded-2xl border border-slate-300 bg-white p-4 text-center text-lg text-slate-950 shadow-sm outline-hidden transition-all focus:border-teal-600 focus:shadow-xl dark:border-slate-700 dark:bg-slate-950 dark:text-white"
				bind:value={username}
				oninput={() => {
					usernameLength = username?.length ?? 0;
					joinStatus = 'editing_username';
				}}
				maxlength="17"
			/>
			{#if custom_field}
				<h1 class="mt-4 text-center text-sm font-medium text-slate-700 dark:text-slate-300">{custom_field}</h1>
				<input
					class="mt-2 self-center rounded-2xl border border-slate-300 bg-white p-4 text-center text-lg text-slate-950 shadow-sm outline-hidden transition-all focus:border-teal-600 focus:shadow-xl dark:border-slate-700 dark:bg-slate-950 dark:text-white"
					bind:value={custom_field_value}
				/>
			{/if}

			<div class="mt-5">
				<BrownButton disabled={username.length <= 3} type="submit">Join Quiz</BrownButton>
			</div>
		</form>
	</div>
{/if}
<div
	id="hcaptcha"
	class="h-captcha"
	data-sitekey={hcaptchaSitekey}
	data-size="invisible"
	data-theme="dark"
></div>

<SocketDiagnostics
	socket={socket}
	label="join"
	details={{
		gamePin: game_pin,
		username,
		usernameLength,
		submitCount,
		joinAttempted,
		joinStatus,
		captchaEnabled: captcha_enabled,
		captchaCheckStatus,
		customField: custom_field ?? null,
		lastJoinPayload
	}}
/>
