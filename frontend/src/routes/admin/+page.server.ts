// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { redirect } from '@sveltejs/kit';

export async function load({ parent, url }) {
	const { email } = await parent();
	if (!email) {
		redirect(302, '/account/login');
	}
	const host_token = url.searchParams.get('token');
	const game_id = url.searchParams.get('game_id');
	const pin = url.searchParams.get('pin');
	let auto_connect = url.searchParams.get('connect') !== null;
	if (host_token === null || game_id === null || pin === null) {
		auto_connect = false;
	}
	return {
		game_pin: pin === null ? '' : pin,
		game_token: game_id === null ? '' : game_id,
		host_token: host_token === null ? '' : host_token,
		auto_connect
	};
}
