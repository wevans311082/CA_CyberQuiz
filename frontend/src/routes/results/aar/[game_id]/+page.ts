// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	const res = await fetch(`/api/v1/results/aar/${params.game_id}`);
	if (!res.ok) {
		return { aar: null, error: res.status === 404 ? 'Report not found.' : 'Failed to load report.' };
	}
	const aar = await res.json();
	return { aar };
};
