// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

export enum ElementTypes {
	Text = 'TEXT', // eslint-disable-line no-unused-vars
	Headline = 'HEADLINE', // eslint-disable-line no-unused-vars
	Image = 'IMAGE', // eslint-disable-line no-unused-vars
	Rectangle = 'RECTANGLE', // eslint-disable-line no-unused-vars
	Circle = 'CIRCLE' // eslint-disable-line no-unused-vars
}

export interface QuizData {
	id?: string;
	title: string;
	description: string;
	quiz_id: string;
	questions: Question[];
	game_id: string;
	game_pin: string;
	started: boolean;
	cover_image?: string;
	background_color?: string;
	background_image?: string;
	likes: number;
	dislikes: number;
	plays: number;
	views: number;
	scenario_type?: string;
	roles?: string[];
	role_descriptions?: Record<string, string>;
	injects?: Inject[];
	master_theme?: MasterTheme;
	teams?: Record<string, string[]>;
}

export interface Inject {
	id: string;
	title: string;
	content: string;
	image?: string;
	severity: 'info' | 'warning' | 'critical';
	trigger_after_question_id?: string;
}

export interface SituationStatus {
	severity: string;
	phase: string;
	affected_systems: string[];
	summary: string;
	context_notes?: string;
}

export type TimelineEventType =
	| 'game_started'
	| 'question_asked'
	| 'answer_results'
	| 'inject'
	| 'situation_update'
	| 'role_assigned'
	| 'branch_resolved'
	| 'decision_made'
	| 'scenario_complete';

export interface TimelineEvent {
	id: string;
	type: TimelineEventType;
	timestamp: string;
	title: string;
	detail?: string;
	data?: Record<string, unknown>;
}

export enum QuizQuestionType {
	ABCD = 'ABCD', // eslint-disable-line no-unused-vars
	RANGE = 'RANGE', // eslint-disable-line no-unused-vars
	VOTING = 'VOTING', // eslint-disable-line no-unused-vars
	SLIDE = 'SLIDE', // eslint-disable-line no-unused-vars
	INFORMATION = 'INFORMATION', // eslint-disable-line no-unused-vars
	FILE = 'FILE', // eslint-disable-line no-unused-vars
	TEXT = 'TEXT', // eslint-disable-line no-unused-vars
	ORDER = 'ORDER', // eslint-disable-line no-unused-vars
	CHECK = 'CHECK', // eslint-disable-line no-unused-vars
	SCOREBOARD = 'SCOREBOARD' // eslint-disable-line no-unused-vars
}

export type QuestionCategory = 'INTERACTIVE' | 'CONTENT' | 'EVIDENCE';

export interface FileAttachment {
	id?: string;
	filename: string;
	mime_type: string;
	url: string;
	description?: string;
}

export interface QuestionTimer {
	enabled: boolean;
	duration_seconds?: number;
}

export type SlideAnimation = 'none' | 'fade' | 'rise' | 'zoom' | 'slide-left' | 'reveal';
export type ElementAnimation = 'none' | 'fade' | 'rise' | 'zoom' | 'slide-left';

export interface SlideThemeOverride {
	enabled?: boolean;
	background_color?: string;
	text_color?: string;
	accent_color?: string;
	background_image?: string;
	font_family?: string;
}

export interface MasterTheme {
	background_color?: string;
	text_color?: string;
	accent_color?: string;
	background_image?: string;
	font_family?: string;
}

export interface RangeQuizAnswer {
	min: number;
	max: number;
	min_correct: number;
	max_correct: number;
}

export interface TextQuizAnswer {
	answer: string;
	case_sensitive: boolean;
}

export interface OrderQuizAnswer {
	answer: string;
	color?: string;
	id?: number;
}

export interface Question {
	time: string;
	question: string;
	type?: QuizQuestionType;
	image?: string;
	answers: Answers;
	hide_results?: boolean;
	id?: string;
	category?: QuestionCategory;
	allowed_roles?: string[];
	default_next_question_id?: string;
	decision_mode?: string;
	facilitator_notes?: string;
	discussion_time?: number;
	information_body?: string;
	file_attachments?: FileAttachment[];
	timer?: QuestionTimer;
	theme_override?: SlideThemeOverride;
	animation?: SlideAnimation;
	objective?: string; // Detection | Containment | Recovery | Communication
	sla_checkpoints?: SLACheckpoint[];
}

export interface SLACheckpoint {
	deadline_seconds: number;
	bonus_points: number;
	penalty_points: number;
	description: string;
}

/**
 * Answers are intentionally modelled as a flexible wire value. The API uses
 * arrays for choice/order/text questions, an object for range questions, and
 * a string for free-text questions. Consumers should narrow by question.type.
 * Keeping the wire shape flexible prevents unsafe casts at every socket and
 * editor boundary while the API evolves.
 */
export type Answers = any;

export interface Answer {
	right: boolean;
	answer: string;
	color?: string;
	next_question_id?: string;
	username?: string;
	tike_taken?: number;
	time_taken?: number;
	score?: number;
}

export interface VotingAnswer {
	answer: string;
	image?: string;
	color?: string;
}

export interface EditorData {
	public: boolean;
	title: string;
	description: string;
	questions: Question[];
	cover_image?: string;
	background_color?: string;
	background_image?: string;
	scenario_type?: string;
	roles?: string[];
	role_descriptions?: Record<string, string>;
	injects?: Inject[];
	master_theme?: MasterTheme;
	teams?: Record<string, string[]>;
	tags?: string[];
	difficulty?: string;
	duration_minutes?: number;
	framework_mappings?: Record<string, string[]>;
	reusable_roles?: Record<string, unknown>[];
	reusable_injects?: Record<string, unknown>[];
	evidence_packs?: Record<string, unknown>[];
}

export interface PrivateImageData {
	id: string;
	uploaded_at: string;
	mime_type: string;
	hash?: string;
	size?: number;
	deleted_at?: string;
	alt_text?: string;
	filename?: string;
	thumbhash?: string;
	server?: string;
	imported: boolean;
	quizzes: { id: string }[];
	quiztivities: { id: string }[];
}
