// SPDX-FileCopyrightText: 2025 CyberAsk
//
// SPDX-License-Identifier: MPL-2.0

export const PRODUCT_NAME = 'CyberAsk Quiz';
export const PRODUCT_SHORT = 'CyberAsk';

export function pageTitle(segment: string): string {
	return `${segment} — ${PRODUCT_NAME}`;
}