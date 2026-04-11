// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { Handle } from '@sveltejs/kit';
import * as jose from 'jose';

const adminOnlyPrefixes = [
	'/admin',
	'/account/controllers',
	'/account/register',
	'/account/settings',
	'/controller',
	'/create',
	'/dashboard',
	'/docs',
	'/edit',
	'/explore',
	'/import',
	'/moderation',
	'/practice',
	'/quiztivity',
	'/remote',
	'/results',
	'/search',
	'/user',
	'/view'
];

const matchesPrefix = (pathname: string, prefixes: string[]) =>
	prefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));

const getApiUrl = (path: string) => `${process.env.API_URL}${path}`;

const getAdminStatus = async (cookieHeader: string) => {
	if (!process.env.API_URL) {
		return false;
	}
	const response = await fetch(getApiUrl('/api/v1/users/admin-status'), {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Cookie: cookieHeader
		}
	});
	if (!response.ok) {
		return false;
	}
	const data = await response.json();
	return data.is_admin === true;
};

/** @type {import('@sveltejs/kit').Handle} */
export const handle: Handle = async ({ event, resolve }) => {
	const access_token = event.cookies.get('access_token');
	event.locals.isAdmin = false;
	if (!access_token) {
		event.locals.email = null;
		const pathname = event.url.pathname;
		if (matchesPrefix(pathname, adminOnlyPrefixes)) {
			const loginUrl = new URL('/account/login', event.url);
			loginUrl.searchParams.set('returnTo', `${pathname}${event.url.search}`);
			return Response.redirect(loginUrl, 302);
		}
		return resolve(event);
	}
	const jwt = jose.decodeJwt(access_token.replace('Bearer ', ''));
	if (!jwt) {
		event.locals.email = null;
		event.locals.isAdmin = false;
		return resolve(event);
	}
	const cookieHeader = event.request.headers.get('cookie') || '';
	let setCookieHeader: string | null = null;
	// if token expires, do a request to get a new one and set the response-cookies on the response
	if (jwt.exp && Date.now() >= jwt.exp * 1000 && process.env.API_URL) {
		const res = await fetch(getApiUrl('/api/v1/users/check'), {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				Cookie: cookieHeader
			}
		});
		if (res.ok) {
			const data = await res.json();
			event.locals.email = data.email ?? null;
			setCookieHeader = res.headers.get('set-cookie');
		}
	}
	if (!event.locals.email) {
		event.locals.email = typeof jwt.sub === 'string' ? jwt.sub : null;
	}
	if (event.locals.email) {
		event.locals.isAdmin = await getAdminStatus(cookieHeader);
	}

	const pathname = event.url.pathname;
	if (matchesPrefix(pathname, adminOnlyPrefixes) && !event.locals.isAdmin) {
		const redirectUrl = event.locals.email
			? new URL('/', event.url)
			: new URL('/account/login', event.url);
		if (!event.locals.email) {
			redirectUrl.searchParams.set('returnTo', `${pathname}${event.url.search}`);
		}
		const response = Response.redirect(redirectUrl, 302);
		if (setCookieHeader) {
			response.headers.set('set-cookie', setCookieHeader);
		}
		return response;
	}

	const response = await resolve(event);
	if (setCookieHeader) {
		response.headers.set('set-cookie', setCookieHeader);
	}
	return response;
};
