<script lang="ts" setup>
import { computed, ref } from 'vue'
import MarkdownIt from 'markdown-it'
import mdKatex from '@traptitech/markdown-it-katex'
import mila from 'markdown-it-link-attributes'
import hljs from 'highlight.js'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { t } from '@/locales'

interface Props {
	inversion?: boolean
	error?: boolean
	text?: string
	loading?: boolean
	asRawText?: boolean
}

const props = defineProps<Props>()

const { isMobile } = useBasicLayout()

const textRef = ref<HTMLElement>()

const mdi = new MarkdownIt({
	linkify: true,
	highlight(code, language) {
		const validLang = !!(language && hljs.getLanguage(language))
		if (validLang) {
			const lang = language ?? ''
			return highlightBlock(hljs.highlight(code, { language: lang }).value, lang)
		}
		return highlightBlock(hljs.highlightAuto(code).value, '')
	},
})

mdi.use(mila, { attrs: { target: '_blank', rel: 'noopener' } })
mdi.use(mdKatex, { blockClass: 'katexmath-block rounded-md p-[10px]', errorColor: ' #cc0000' })
mdi.use(markdownItImageSize)

const wrapClass = computed(() => {
	return [
		'text-wrap',
		'min-w-[20px]',
		'rounded-md',
		isMobile.value ? 'p-2' : 'px-3 py-2',
		props.inversion ? 'bg-[#299AB4] text-white' : 'bg-[#F4F6F8]',
		props.inversion ? 'dark:bg-[#6FD3F2] dark:text-black' : 'dark:bg-[#1E1E20]',
		props.inversion ? 'message-request' : 'message-reply',
		{ 'text-red-500': props.error },
	]
})

const text = computed(() => {
	let value = props.text ?? ''
	// 插件 https://github.com/chat-ai-dev/pexels_videos 特殊逻辑
	if (value.endsWith('PEXELS.COM\n')) {
		// remove the last characters `PEXELS.COM\n`
		value = value.slice(0, -12)
		return value
	}

	if (!props.asRawText)
		return mdi.render(value)
	return value
})

function highlightBlock(str: string, lang?: string) {
	return `<pre class="code-block-wrapper"><div class="code-block-header"><span class="code-block-header__lang">${lang}</span><span class="code-block-header__copy">${t('chat.copyCode')}</span></div><code class="hljs code-block-body ${lang}">${str}</code></pre>`
}

function markdownItImageSize(md: any, { lazy = true, caption = true } = {}) {
	md.renderer.rules.image = function (tokens: any, idx: any, options: any, env: any, slf: any) {
		const token = tokens[idx]

		// "alt" attr MUST be set, even if empty. Because it's mandatory and
		// should be placed on proper position for tests.
		//
		// Replace content with actual value

		token.attrs[token.attrIndex('alt')][1]
			= slf.renderInlineAsText(token.children, options, env)

		if (lazy && token.attrIndex('loading') === -1) { // add loading="lazy" attribute
			token.attrs.push(['loading', 'lazy'])
		}

		// process optional ={width}x{height} title
		const titleIndex = token.attrIndex('title')
		if (titleIndex >= 0) {
			const [title, size] = token.attrs[titleIndex][1].split('=')
			const [width, height] = size ? size.split('x').map((v: any) => v.trim()).filter(Boolean) : []
			if (title)
				token.attrs.splice(titleIndex, 1, ...typeof caption !== 'boolean' && title ? [['title', title]] : [])

			if (width) {
				token.attrs.push(
					...width ? [['width', width]] : [],
					...height ? [['height', height]] : [],
				)
			}

			if (caption && title)
				return `<figure>${slf.renderToken(tokens, idx, options)}<figcaption>${title}</figcaption></figure>`
		}

		return slf.renderToken(tokens, idx, options)
	}
}

defineExpose({ textRef })
</script>

<template>
	<div class="text-black" :class="wrapClass">
		<div ref="textRef" class="leading-relaxed break-words">
			<div v-if="!inversion">
				<div v-if="!asRawText" class="markdown-body" :class="{ 'animate-typing': loading }" v-html="text" />
				<div v-else class="whitespace-pre-wrap" :class="{ 'animate-typing': loading }" v-text="text" />
			</div>
			<div v-else class="whitespace-pre-wrap" v-text="text" />
			<template v-if="loading && !text">
				<span class="dark:text-white w-[8px] h-[12px] inline-block animate-blink" />
			</template>
		</div>
	</div>
</template>

<style lang="less">
@import url(./style.less);

@keyframes typing {
	0% {
		opacity: 1;
	}

	50% {
		opacity: 0;
	}

	100% {
		opacity: 1;
	}
}

.animate-typing {
	&>:last-child::after {
		content: '';
		display: inline-block;
		vertical-align: middle;
		width: 8px;
		height: 12px;
		background-color: black;
		animation: typing 1s infinite;
	}
}

.dark .animate-typing {
	&> :last-child::after {
		background-color: white;
	}
}
</style>
