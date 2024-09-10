<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import type { InputInst } from 'naive-ui'
import { NAutoComplete, NButton, NInput } from 'naive-ui'
import { storeToRefs } from 'pinia'
import ExportChatWidget from '../Widgets/ExportChatWidget.vue'
import DeleteChatWidget from '../Widgets/DeleteChatWidget.vue'
import SelectModelWidget from '../Widgets/SelectModelWidget.vue'
import { t } from '@/locales'
import { useChatStore, usePromptStore } from '@/store'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { SvgIcon } from '@/components/common'

interface Props {
	loading: boolean
	uuid: string
}

interface Emit {
	(e: 'apply'): void
}

const props = defineProps<Props>()

const emit = defineEmits<Emit>()
const chatStore = useChatStore()
const inputRef = ref<InputInst | null>(null)

// rewrite val to read and write
const val = computed({
	get: () => chatStore.prompt || '',
	set: (prompt: string) => chatStore.setPrompt(prompt),
})

function handleApply() {
	emit('apply')
}

const show = ref(true)

// 添加PromptStore
const promptStore = usePromptStore()

// 使用storeToRefs，保证store修改后，联想部分能够重新渲染
const { promptList: promptTemplate } = storeToRefs<any>(promptStore)
// 可优化部分
// 搜索选项计算，这里使用value作为索引项，所以当出现重复value时渲染异常(多项同时出现选中效果)
// 理想状态下其实应该是key作为索引项,但官方的renderOption会出现问题，所以就需要value反renderLabel实现
const searchOptions = computed(() => {
	if (val.value?.startsWith('/')) {
		return promptTemplate.value.filter((item: { key: string }) => item.key.toLowerCase().includes(val.value!.substring(1).toLowerCase())).map((obj: { value: any }) => {
			return {
				label: obj.value,
				value: obj.value,
			}
		})
	}
	else {
		return []
	}
})

// value反渲染key
function renderOption(option: { label: string }) {
	for (const i of promptTemplate.value) {
		if (i.value === option.label)
			return [i.key]
	}
	return []
}

const { isMobile } = useBasicLayout()

const placeholder = computed(() => {
	if (isMobile.value)
		return t('chat.placeholderMobile')
	return t('chat.placeholder')
})

const buttonDisabled = computed(() => {
	return props.loading || !val.value || val.value.trim() === ''
})

const footerClass = computed(() => {
	let classes = show.value ? ['p-4', 'pt-0'] : ['px-4', 'pt-0']
	if (isMobile.value)
		classes = ['sticky', 'left-0', 'bottom-0', 'right-0', 'p-2', 'pr-3', 'overflow-hidden']
	return classes
})

function handleEnter(event: KeyboardEvent) {
	if (!isMobile.value) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault()
			handleApply()
		}
	}
	else {
		if (event.key === 'Enter' && event.ctrlKey) {
			event.preventDefault()
			handleApply()
		}
	}
}

onMounted(() => {
	setTimeout(() => {
		inputRef.value?.focus()
	}, 10)
})
</script>

<template>
	<div class="flex items-center justify-center text-6xl transition-opacity opacity-0 hover:opacity-100 hover-delay">
		<SvgIcon :icon="show ? 'iconamoon:arrow-down-2-light' : 'iconamoon:arrow-up-2-light'"
			class="rounded-t-md dark:bg-[#24272e] bg-gray-200 cursor-pointer h-5 w-11" @click="show = !show" />
	</div>
	<footer class="relative" :class="show ? `show ${footerClass}` : `content ${footerClass}`">
		<div class="w-full max-w-screen-2xl m-auto border-t-[1px] border-t-gray-200 dark:border-t-neutral-800">
			<div class="flex flex-col items-start justify-start">
				<div class="flex items-start my-2">
					<SelectModelWidget :loading="loading" />
					<DeleteChatWidget :loading="loading" :uuid="uuid" />
					<ExportChatWidget :loading="loading" :show="!isMobile" />
				</div>
				<div class="w-full relative">
					<NAutoComplete v-model:value="val" :options="searchOptions" :render-label="renderOption">
						<template #default="{ handleInput, handleBlur, handleFocus }">
							<NInput ref="inputRef" v-model:value="val" type="textarea" :placeholder="placeholder" :rows="3"
								:autosize="{ minRows: 6, maxRows: isMobile ? 6 : 8 }" @input="handleInput" @focus="handleFocus"
								@blur="handleBlur" @keypress="handleEnter" />
						</template>
					</NAutoComplete>
					<div class="absolute right-4 bottom-2">
						<div class="flex gap-2 items-center text-gray-400">
							<span class="flex items-center text-xs">
								<SvgIcon icon="uil:enter" />
								{{ $t('common.send') }}
							</span>
							/
							<span class="flex items-center text-xs">
								<SvgIcon icon="material-symbols-light:shift-outline" />
								<SvgIcon icon="uil:enter" />
								{{ $t('common.shiftEnter') }}
							</span>
							<NButton type="primary" :disabled="buttonDisabled" @click="handleApply">
								<template #icon>
									<span class="dark:text-black">
										<SvgIcon icon="ri:send-plane-fill" />
									</span>
								</template>
							</NButton>
						</div>
					</div>
				</div>
			</div>
		</div>
	</footer>
</template>

<style scoped lang="less">
.content {
	transition: max-height 0.2s ease, opacity 0.2s ease;
	max-height: 0;
	opacity: 0;
	overflow: hidden;
}

.show {
	max-height: 1000px;
	opacity: 1;
}

.hover-delay {
	transition-delay: 50ms;
}
</style>
