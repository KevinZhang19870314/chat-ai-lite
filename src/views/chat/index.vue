<script setup lang='ts'>
import type { Ref } from 'vue'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { NButton, useDialog } from 'naive-ui'
import { Message } from './components'
import { useScroll } from './hooks/useScroll'
import { useChat } from './hooks/useChat'
import { useCopyCode } from './hooks/useCopyCode'
import HeaderComponent from './components/Header/index.vue'
import FooterComponent from './components/Footer/index.vue'
import { useAIMode } from './hooks/useAIMode'
import { loading } from './hooks/common/useLoading'
import { useLocalAI } from './hooks/useLocalAI'
import { abortController } from './hooks/common/useAbortController'
import { useChatWithRole } from './hooks/useChatWithRole'
import { useChatLLM } from './hooks/useChatLLM'
import { SvgIcon } from '@/components/common'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { useChatStore } from '@/store'
import { t } from '@/locales'
import type { Chat, ChatHistoryMeta } from '@/models/chat.model'
import { AiMode, ChatRole } from '@/models/chat.model'
import { useDigitalPerson } from './hooks/useDigitalPerson'

const route = useRoute()
const dialog = useDialog()

const chatStore = useChatStore()
const chatRole = ChatRole

useCopyCode()

const { isMobile } = useBasicLayout()
const { updateChatSome } = useChat()
const { scrollRef, scrollToBottom, scrollToBottomIfAtBottom } = useScroll()
const { aiMode } = useAIMode()
const activeHistory = computed(() => chatStore.getChatHistoryByCurrentActive)

const { uuid } = route.params as { uuid: string }

const { regenChat: regenChatForLocalAI, chat: chatForLocalAI } = useLocalAI()
const { regenChat: regenChatForRole, chat: chatForRole } = useChatWithRole()
const { regenChat: regenChatLLM, chat: chatLLM } = useChatLLM()
const { regenChat: regenChatForDigitalPerson, chat: chatForDigitalPerson } = useDigitalPerson()

async function regen(index: number) {
	if (aiMode.value === AiMode.ChatLLM) {
		regenChatLLM(index, +uuid, aiMode.value)
	}
	else if (aiMode.value === AiMode.KnowledgeBase) {
		if (activeHistory.value?.ai_mode === AiMode.LocalAI)
			regenChatForLocalAI(index, +uuid)
	}
	else if (aiMode.value === AiMode.MyFavorites) {
		regenChatForRole(index, +uuid)
	} else if (aiMode.value === AiMode.DigitalPerson) {
		regenChatForDigitalPerson(index, +uuid)
	}
}

async function gen() {
	if (aiMode.value === AiMode.ChatLLM) {
		chatLLM(+uuid, aiMode.value, scrollToBottom, scrollToBottomIfAtBottom)
	}
	else if (aiMode.value === AiMode.KnowledgeBase) {
		if (activeHistory.value?.ai_mode === AiMode.LocalAI)
			chatForLocalAI(+uuid, scrollToBottom, scrollToBottomIfAtBottom)
	}
	else if (aiMode.value === AiMode.MyFavorites) {
		chatForRole(+uuid, scrollToBottom, scrollToBottomIfAtBottom)
	} else if (aiMode.value === AiMode.DigitalPerson) {
		chatForDigitalPerson(+uuid, scrollToBottom, scrollToBottomIfAtBottom)
	}
}

const dataSources = computed(() => {
	const chats: Chat[] = chatStore.getChatByUuid(+uuid)
	return chats
})

const inputRef = ref<Ref | null>(null)

// 未知原因刷新页面，loading 状态不会重置，手动重置
dataSources.value.forEach((item, index) => {
	if (item.loading)
		updateChatSome(+uuid, index, { loading: false })
})

function handleDelete(index: number) {
	if (loading.value)
		return

	dialog.warning({
		title: t('chat.deleteMessage'),
		content: t('chat.deleteMessageConfirm'),
		positiveText: t('common.yes'),
		negativeText: t('common.no'),
		onPositiveClick: () => {
			chatStore.deleteChatByUuid(+uuid, index)
		},
	})
}

function handleStop() {
	if (loading.value) {
		abortController.value.abort()
		loading.value = false
	}
}

onMounted(async () => {
	scrollToBottom()
	if (inputRef.value && !isMobile.value)
		inputRef.value?.focus()

	if (aiMode.value === AiMode.MyFavorites && dataSources.value.length === 0 && activeHistory.value)
		chatForRole(+uuid, scrollToBottom, scrollToBottomIfAtBottom, `${(activeHistory.value as ChatHistoryMeta).greetings}`)

	if (aiMode.value === AiMode.DigitalPerson && dataSources.value.length === 0 && activeHistory.value) {
		console.log('DigitalPerson', `${(activeHistory.value as ChatHistoryMeta).greetings}`)
		chatForDigitalPerson(+uuid, scrollToBottom, scrollToBottomIfAtBottom, `${(activeHistory.value as ChatHistoryMeta).greetings}`)
	}
})

onUnmounted(() => {
	if (loading.value)
		abortController.value.abort()
})
</script>

<template>
	<div class="flex flex-col w-full h-full">
		<HeaderComponent v-if="isMobile" :loading="loading" :show-using-context="false" />
		<main class="flex-1 overflow-hidden">
			<div id="scrollRef" ref="scrollRef" class="h-full overflow-hidden overflow-y-auto">
				<div id="image-wrapper" class="w-full max-w-screen-2xl m-auto dark:bg-[#101014]"
					:class="[isMobile ? 'p-2' : 'p-4']">
					<template v-if="!dataSources.length">
						<div class="flex items-center justify-center mt-4 text-center text-neutral-300">
							<SvgIcon icon="ri:bubble-chart-fill" class="mr-2 text-3xl" />
							<span>Aha~</span>
						</div>
					</template>
					<template v-else>
						<div>
							<Message v-for="(item, index) of dataSources" :key="index" :date-time="item.dateTime" :text="item.text"
								:inversion="item.role === chatRole.USER" :error="item.error" :loading="item.loading"
								@regenerate="regen(index)" @delete="handleDelete(index)" />
							<div class="sticky bottom-0 left-0 flex justify-center">
								<NButton v-if="loading" type="warning" @click="handleStop">
									<template #icon>
										<SvgIcon icon="ri:stop-circle-line" />
									</template>
									Stop Responding
								</NButton>
							</div>
						</div>
					</template>
				</div>
			</div>
		</main>
		<FooterComponent :loading="loading" :uuid="uuid" @apply="gen" />
	</div>
</template>
