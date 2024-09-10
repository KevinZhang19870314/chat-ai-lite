<script setup lang='ts'>
import { NAvatar, NButton, NGrid, NGridItem, NInput, NModal, NPagination, NSkeleton, NSpace, NTooltip, useMessage } from 'naive-ui'
import { computed, onMounted, ref, watch } from 'vue'
import { SvgIcon } from '@/components/common'
import { useAuthStore, useChatStore, usePromptStore } from '@/store'
import type { ChatHistoryMeta, Prompt } from '@/models/chat.model'
import { AiMode } from '@/models/chat.model'
import { generateSessionId } from '@/utils/functions'
import { addChatHistoryMeta } from '@/api'

interface Props {
	/** 搜索关键词 */
	term: string
	category: string
}

const props = defineProps<Props>()
const promptStore = usePromptStore()
const chatStore = useChatStore()
const authStore = useAuthStore()
const ms = useMessage()

const loading = ref(false)
const promptList = computed(() => promptStore.promptList)
const page = ref(1)
const total = ref(1)
const size = 15
const showDetailModal = ref(false)
const selectedPrompt = ref<Prompt>({ title: '', icon: '', description: '', greetings: '', category: '', likes: 0 })

function getLike(prompt: Prompt) {
	return chatStore.history.find(item => item.title === prompt.title)
}

async function handleLike(prompt: Prompt) {
	// 点击like之后加入到左侧聊天历史里面去，即UserPrompt表里面
	// 如果已经isLike，则删除ChatHistoryMeta表记录；如果不在，则加入到ChatHistoryMeta表里面
	loading.value = true
	chatStore.setSiderLoading(true)
	try {
		const like = getLike(prompt)
		if (like) {
			await chatStore.deleteChatHistoryMeta({
				title: prompt.title,
			})
			await promptStore.likes({ id: prompt.id!, likes: false })
		}
		else {
			await addHistory(prompt)
			await promptStore.likes({ id: prompt.id!, likes: true })
		}

		await chatStore.fetchHistory()
		refresh()
	}
	catch (error) {
		ms.error(`${error}`)
	}
	finally {
		loading.value = false
		chatStore.setSiderLoading(false)
	}
}

async function handleChat(prompt: Prompt) {
	loading.value = true
	chatStore.setSiderLoading(true)
	try {
		const like = getLike(prompt)
		if (like) {
			chatStore.setActive(like.uuid)
		}
		else {
			await promptStore.likes({ id: prompt.id!, likes: true })
			const uuid = await addHistory(prompt)
			await chatStore.fetchHistory()
			chatStore.setActive(uuid)
		}
	}
	catch (error) {
		ms.error(`${error}`)
	}
	finally {
		loading.value = false
		chatStore.setSiderLoading(false)
	}
}

async function addHistory(prompt: Prompt) {
	const uuid = generateSessionId()
	const item: ChatHistoryMeta = {
		uuid,
		isEdit: false,
		title: prompt.title,
		icon: prompt.icon,
		ai_mode: AiMode.MyFavorites,
		description: prompt.description,
		greetings: prompt.greetings,
	}

	const res = await addChatHistoryMeta<ChatHistoryMeta>(item)
	if (res.status === 'Error')
		throw new Error(`${res.message}`)

	return uuid
}

async function handlePageChange(p: number) {
	page.value = p
	await refresh()
}

async function refresh() {
	loading.value = true
	try {
		total.value = await promptStore.fetchPromptListByPage(size, page.value, props.category, 1, props.term)
	}
	catch (error) {
		ms.error(`${error}`)
	}
	finally {
		loading.value = false
	}
}

function handleViewDetail(item: Prompt) {
	showDetailModal.value = !showDetailModal.value
	selectedPrompt.value = item
}

watch(() => props.term, async () => {
	page.value = 1
	await refresh()
})

watch(() => props.category, async () => {
	page.value = 1
	await refresh()
})

onMounted(async () => {
	if (authStore.session?.auth)
		return
	await refresh()
})
</script>

<template>
	<NGrid v-if="!loading" x-gap="24" y-gap="24" cols="1 s:1 m:2 l:3 xl:5 2xl:5" responsive="screen">
		<NGridItem v-for="(item, index) of promptList" :key="index">
			<div class="rounded-md p-4 shadow-md shadow-gray-500/30 hover:shadow-gray-500/40 flex flex-col items-center gap-1">
				<NAvatar style="background-color: transparent;" :size="76" round>
					<SvgIcon :icon="item.icon" class="text-[76px]" />
				</NAvatar>
				<div class="cursor-default text-lg">
					{{ item.title }}
				</div>
				<div class="line-clamp-2 cursor-default text-sm">
					{{ item.description }}
				</div>
				<NSpace class="pt-2">
					<NTooltip trigger="hover">
						<template #trigger>
							<NButton size="small" round @click="handleLike(item)">
								<template #icon>
									<SvgIcon icon="icon-park-solid:like" class="text-base hover:text-red-500"
										:class="getLike(item) ? 'text-red-500' : 'text-gray-500'" />
								</template>
								<span class="text-sm">{{ item.likes }}</span>
							</NButton>
						</template>
						{{ $t('myFav.likes') }}
					</NTooltip>
					<NTooltip trigger="hover">
						<template #trigger>
							<NButton size="small" circle @click="handleChat(item)">
								<template #icon>
									<SvgIcon icon="fluent:chat-28-regular" class="text-base" />
								</template>
							</NButton>
						</template>
						{{ $t('common.chat') }}
					</NTooltip>
					<NTooltip trigger="hover">
						<template #trigger>
							<NButton size="small" circle @click="handleViewDetail(item)">
								<template #icon>
									<SvgIcon icon="fluent-mdl2:view" class="text-base" />
								</template>
							</NButton>
						</template>
						{{ $t('common.view') }}
					</NTooltip>
				</NSpace>
			</div>
		</NGridItem>
	</NGrid>
	<!-- 以下为骨架屏 -->
	<NGrid v-else x-gap="24" y-gap="24" cols="1 s:1 m:2 l:3 xl:5 2xl:5" responsive="screen">
		<NGridItem v-for="(_, index) in (promptList.length || size)" :key="index">
			<div class="rounded-md p-4 shadow-lg shadow-gray-500/30 hover:shadow-gray-500/40 flex flex-col items-center gap-2">
				<NSkeleton height="48px" width="76px" circle />
				<NSkeleton text width="60%" />
				<NSkeleton text :repeat="2" />
				<NSpace class="pt-2">
					<NSkeleton height="28px" width="28px" circle />
					<NSkeleton height="28px" width="28px" circle />
					<NSkeleton height="28px" width="28px" circle />
				</NSpace>
			</div>
		</NGridItem>
	</NGrid>
	<div class="flex justify-end p-4">
		<NPagination v-model:page="page" :item-count="total" :page-sizes="[size]" size="large"
			@update-page="handlePageChange" />
	</div>
	<NModal v-model:show="showDetailModal" style="max-width: 900px;" preset="card">
		<NSpace vertical>
			{{ $t('store.roleIcon') }}
			<SvgIcon :icon="selectedPrompt.icon" class="text-4xl" />
			{{ $t('store.roleTitle') }}
			<NInput v-model:value="selectedPrompt.title" readonly />
			{{ $t('store.roleDescription') }}
			<NInput v-model:value="selectedPrompt.description" type="textarea" readonly />
			{{ $t('store.greetings') }}
			<NInput v-model:value="selectedPrompt.greetings" type="textarea" readonly />
			<NButton block type="primary" @click="showDetailModal = false">
				{{ $t('common.confirm') }}
			</NButton>
		</NSpace>
	</NModal>
</template>
