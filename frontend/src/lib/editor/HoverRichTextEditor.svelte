<!--
SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount } from 'svelte';
	import {
		ClassicEditor,
		Essentials,
		Autoformat,
		Bold,
		Italic,
		Underline,
		Paragraph,
		TextTransformation,
		Superscript,
		Subscript,
		Strikethrough,
		FontFamily,
		FontSize,
		FontColor,
		FontBackgroundColor
	} from 'ckeditor5';
	import 'ckeditor5/ckeditor5.css';

	interface Props {
		text?: string;
		placeholder?: string;
		minHeightClass?: string;
		toolbarLabel?: string;
	}

	let {
		text = $bindable(''),
		placeholder = 'Type here',
		minHeightClass = 'min-h-[3rem]',
		toolbarLabel = 'Formatting tools'
	}: Props = $props();

	let host = $state<HTMLDivElement>();
	let editor: Awaited<ReturnType<typeof ClassicEditor.create>> | undefined;

	const normalize_text = (value: string) => value.replace(/^<p>(.*)<\/p>$/s, '$1');

	$effect(() => {
		text = normalize_text(text ?? '');
	});

	onMount(() => {
		class Editor extends ClassicEditor {
			static builtinPlugins = [
				Essentials,
				Autoformat,
				Bold,
				Italic,
				Underline,
				Paragraph,
				TextTransformation,
				Strikethrough,
				Superscript,
				Subscript,
				FontFamily,
				FontSize,
				FontColor,
				FontBackgroundColor
			];

			static defaultConfig = {
				language: 'en'
			};
		}

		Editor.create(host, {
			licenseKey: 'GPL',
			placeholder,
			toolbar: [
				'fontFamily',
				'fontSize',
				'fontColor',
				'fontBackgroundColor',
				'|',
				'bold',
				'italic',
				'underline',
				'strikethrough',
				'superscript',
				'subscript',
				'|',
				'undo',
				'redo'
			]
		})
			.then((newEditor) => {
				editor = newEditor;
				editor.setData(text);
				editor.model.document.on('change:data', () => {
					text = normalize_text(editor?.getData() ?? '');
				});
			})
			.catch((error) => {
				console.error('There was a problem initializing the rich text editor.', error);
			});

		return () => {
			editor?.destroy();
		};
	});
</script>

<div class="hover-rich-editor group rounded-xl border border-gray-300 bg-white/80 p-2 transition focus-within:border-[#B07156] hover:border-[#B07156] dark:border-gray-500 dark:bg-gray-700/80">
	<div class="sr-only">{toolbarLabel}</div>
	<div
		bind:this={host}
		class={`hover-rich-editor__host ${minHeightClass} rounded-lg bg-transparent text-sm dark:text-white`}
	></div>
</div>

<style>
	:global(.ck-powered-by) {
		display: none;
	}

	.hover-rich-editor :global(.ck-editor__top) {
		max-height: 0;
		overflow: hidden;
		opacity: 0;
		transform: translateY(-0.25rem);
		transition: max-height 120ms ease, opacity 120ms ease, transform 120ms ease;
	}

	.hover-rich-editor:hover :global(.ck-editor__top),
	.hover-rich-editor:focus-within :global(.ck-editor__top) {
		max-height: 4rem;
		opacity: 1;
		transform: translateY(0);
	}

	.hover-rich-editor :global(.ck-toolbar) {
		border: 0;
		background: transparent;
		padding: 0 0 0.5rem;
		flex-wrap: wrap;
	}

	.hover-rich-editor :global(.ck-editor__editable_inline) {
		min-height: inherit;
		border: 0;
		box-shadow: none;
		background: transparent;
		padding: 0.35rem 0.5rem;
	}

	.hover-rich-editor :global(.ck.ck-content) {
		color: inherit;
	}

	.hover-rich-editor :global(.ck.ck-editor__main > .ck-editor__editable:not(.ck-focused)) {
		border: 0;
	}

	.hover-rich-editor :global(.ck.ck-editor__main > .ck-editor__editable.ck-focused) {
		border: 0;
		box-shadow: none;
	}
</style>