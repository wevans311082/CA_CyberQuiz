// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { io } from 'socket.io-client';

export const socket = io();

const debugSocket = socket as typeof socket & { __verboseDebugAttached?: boolean };

if (typeof window !== 'undefined' && !debugSocket.__verboseDebugAttached) {
	debugSocket.__verboseDebugAttached = true;

	const now = () => new Date().toISOString();

	const log = (scope: string, message: string, payload?: unknown) => {
		if (payload === undefined) {
			console.log(`[SOCKET][${scope}] ${now()} ${message}`);
			return;
		}
		console.log(`[SOCKET][${scope}] ${now()} ${message}`, payload);
	};

	log('BOOT', 'Attaching verbose Socket.IO diagnostics');

	socket.onAny((eventName: string, ...args: unknown[]) => {
		log('IN', eventName, args.length > 1 ? args : args[0]);
	});

	socket.onAnyOutgoing((eventName: string, ...args: unknown[]) => {
		log('OUT', eventName, args.length > 1 ? args : args[0]);
	});

	socket.on('connect', () => {
		log('STATE', 'connect', {
			socketId: socket.id,
			transport: socket.io.engine.transport.name
		});
	});

	socket.on('disconnect', (reason: string) => {
		log('STATE', 'disconnect', { reason });
	});

	socket.on('connect_error', (error: Error) => {
		log('STATE', 'connect_error', { message: error.message });
	});

	socket.io.on('reconnect_attempt', (attempt: number) => {
		log('RECONNECT', 'reconnect_attempt', { attempt });
	});

	socket.io.on('reconnect', (attempt: number) => {
		log('RECONNECT', 'reconnect', { attempt });
	});

	socket.io.on('reconnect_error', (error: Error) => {
		log('RECONNECT', 'reconnect_error', { message: error.message });
	});

	socket.io.on('reconnect_failed', () => {
		log('RECONNECT', 'reconnect_failed');
	});

	socket.io.on('error', (error: Error) => {
		log('MANAGER', 'error', { message: error.message });
	});

	socket.io.engine.on('upgrade', (transport) => {
		log('ENGINE', 'upgrade', { transport: transport.name });
	});

	socket.io.engine.on('upgradeError', (error: Error) => {
		log('ENGINE', 'upgradeError', { message: error.message });
	});

	socket.io.engine.on('close', (reason: string) => {
		log('ENGINE', 'close', { reason });
	});

	socket.io.engine.on('packet', (packet) => {
		log('PACKET', 'incoming', {
			type: packet.type,
			data: packet.data ?? null
		});
	});

	socket.io.engine.on('packetCreate', (packet) => {
		log('PACKET', 'outgoing', {
			type: packet.type,
			data: packet.data ?? null
		});
	});

	socket.io.engine.on('drain', () => {
		log('ENGINE', 'drain');
	});

	socket.io.engine.on('ping', () => {
		log('ENGINE', 'ping');
	});

	socket.io.engine.on('pong', () => {
		log('ENGINE', 'pong');
	});

	socket.io.engine.transport.on('poll', () => {
		log('POLLING', 'poll');
	});

	socket.io.engine.transport.on('pollComplete', () => {
		log('POLLING', 'pollComplete');
	});

	socket.io.engine.transport.on('pollError', (error: Error) => {
		log('POLLING', 'pollError', { message: error.message });
	});
}
