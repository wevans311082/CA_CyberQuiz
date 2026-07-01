<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { run } from 'svelte/legacy';

	import {
		BalloonEditor,
		Essentials,
		Autoformat,
		Bold,
		Italic,
		Underline,
		Heading,
		Alignment,
		BlockQuote,
		Code,
		CodeBlock,
		HorizontalLine,
		Link,
		List,
		Indent,
		IndentBlock,
		Highlight,
		RemoveFormat,
		FontFamily,
		FontSize,
		FontColor,
		FontBackgroundColor,
		Paragraph,
		TextTransformation,
		Superscript,
		Subscript,
		Strikethrough
	} from 'ckeditor5';
	import 'ckeditor5/ckeditor5.css';

	const triggerChange = () => {
		text = editor.getData();
	};

	import { onMount } from 'svelte';
	interface Props {
		// import Autoformat from "@ckeditor/ckeditor5-autoformat/src/autoformat"
		text?: string;
	}

	let { text = $bindable('') }: Props = $props();

	let html_el = $state();

	run(() => {
		text = text.replace('<p>', '').replace('</p>', '');
	});
	let editor;
	onMount(() => {
		class Editor extends BalloonEditor {
			static builtinPlugins = [
				Essentials,
				Autoformat,
				Bold,
				Italic,
				Underline,
				Heading,
				Alignment,
				BlockQuote,
				Code,
				CodeBlock,
				HorizontalLine,
				Link,
				List,
				Indent,
				IndentBlock,
				Highlight,
				RemoveFormat,
				FontFamily,
				FontSize,
				FontColor,
				FontBackgroundColor,
				Paragraph,
				TextTransformation,
				Strikethrough,
				Subscript,
				Superscript
			];

			static defaultConfig = {
				language: 'en'
			};
		}
		// BalloonEditor.builtinPlugins = [Strikethrough]
		Editor.create(html_el, {
			licenseKey: 'GPL',
			link: {
				addTargetToExternalLinks: true,
				defaultProtocol: 'https://'
			},
			heading: {
				options: [
					{ model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph' },
					{ model: 'heading1', view: 'h1', title: 'Heading 1', class: 'ck-heading_heading1' },
					{ model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2' },
					{ model: 'heading3', view: 'h3', title: 'Heading 3', class: 'ck-heading_heading3' }
				]
			},
			// plugins: [Strikethrough],
			config: {
				enterMode: BalloonEditor.ENTER_DIV,
				shiftEnterMode: BalloonEditor.ENTER_BR
			},
			toolbar: [
				'heading',
				'|',
				'fontFamily',
				'fontSize',
				'fontColor',
				'fontBackgroundColor',
				'|',
				'bold',
				'italic',
				'underline',
				'strikethrough',
				'removeFormat',
				'superscript',
				'subscript',
				'|',
				'link',
				'bulletedList',
				'numberedList',
				'|',
				'outdent',
				'indent',
				'alignment',
				'|',
				'blockQuote',
				'code',
				'codeBlock',
				'highlight',
				'horizontalLine',
				'|',
				'undo',
				'redo'
			]
		})
			.then((newEditor) => {
				editor = newEditor;
				editor.setData(text);
				editor.model.document.on('change:data', () => {
					triggerChange();
				});
			})
			.catch((error) => {
				console.error('There was a problem initializing the editor.', error);
			});
	});
</script>

<div class="w-fit rounded-lg border-gray-500 border">
	<div
		bind:this={html_el}
		contenteditable="true"
		class="rounded-lg border-gray-500 border text-center w-fit h-fit resize-none dark:bg-gray-500 min-w-[5rem] dark:text-white"
	></div>
</div>

<style>
	:global(.ck-powered-by) {
		display: none;
	}
</style>
