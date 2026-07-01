// SPDX-FileCopyrightText: 2025 CyberAsk
//
// SPDX-License-Identifier: MPL-2.0

import { redirect } from '@sveltejs/kit';

export async function load({ parent }) {
	const { email } = await parent();
	if (!email) {
		redirect(302, '/account/login?redirect=/seed');
	}
	return {};
}