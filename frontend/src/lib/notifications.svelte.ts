export type NoticeKind = 'success' | 'error' | 'info';

export type Notice = {
	id: number;
	kind: NoticeKind;
	message: string;
};

export type Confirmation = {
	title: string;
	message: string;
	confirmLabel: string;
	resolve: (value: boolean) => void;
};

let nextId = 1;
let notices = $state<Notice[]>([]);
let confirmation = $state<Confirmation | null>(null);

export const notificationState = {
	get notices() {
		return notices;
	},
	get confirmation() {
		return confirmation;
	}
};

export function notify(message: string, kind: NoticeKind = 'info', duration = 4500) {
	const id = nextId++;
	notices = [...notices, { id, kind, message }];
	if (duration > 0) {
		setTimeout(() => dismissNotice(id), duration);
	}
}

export function dismissNotice(id: number) {
	notices = notices.filter((notice) => notice.id !== id);
}

export function confirmAction(
	message: string,
	options: { title?: string; confirmLabel?: string } = {}
): Promise<boolean> {
	if (confirmation) {
		confirmation.resolve(false);
	}
	return new Promise((resolve) => {
		confirmation = {
			title: options.title ?? 'Please confirm',
			message,
			confirmLabel: options.confirmLabel ?? 'Continue',
			resolve
		};
	});
}

export function resolveConfirmation(value: boolean) {
	const current = confirmation;
	confirmation = null;
	current?.resolve(value);
}
