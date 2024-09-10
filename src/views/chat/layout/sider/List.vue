<script setup lang='ts'>
import { computed, onMounted, ref } from 'vue'
import { NPopconfirm, NScrollbar, NSkeleton, useMessage, NAvatar } from 'naive-ui'
import AddHistoryModal from './modal/AddHistoryModal.vue'
import { SvgIcon } from '@/components/common'
import { useAppStore, useAuthStore, useChatStore } from '@/store'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { debounce } from '@/utils/functions/debounce'
import { AiMode, ChatHistoryMeta } from '@/models/chat.model'

interface Props {
	aiMode: AiMode
	search?: string
}

const props = defineProps<Props>()

const { isMobile } = useBasicLayout()

const appStore = useAppStore()
const chatStore = useChatStore()
const authStore = useAuthStore()
const ms = useMessage()
const isDigitalPerson = computed(() => chatStore.aiMode === AiMode.DigitalPerson)

const dataSources = computed(() => {
	let results = chatStore.getChatHistoryMetas(props.aiMode)
	if (props.search) {
		results = results.filter((item) => {
			return item.title.toLowerCase().includes(props.search!.toLowerCase())
		})
	}

	return results
})
const showHistoryModal = ref(false)

async function handleSelect({ uuid }: ChatHistoryMeta) {
	if (isActive(uuid))
		return

	await chatStore.setActive(uuid)
	chatStore.setPrompt('')

	if (isMobile.value)
		appStore.setSiderCollapsed(true)
}

function handleEdit(event?: MouseEvent) {
	event?.stopPropagation()
	showHistoryModal.value = !showHistoryModal.value
}

async function handleDelete(item: ChatHistoryMeta, event?: MouseEvent | TouchEvent) {
	chatStore.setSiderLoading(true)
	try {
		event?.stopPropagation()
		chatStore.toMainPage()
		await chatStore.deleteChatHistoryMeta(item)
		await chatStore.fetchHistory()
		if (isMobile.value)
			appStore.setSiderCollapsed(true)
	}
	catch (error) {
		ms.error(`${error}`)
	}
	finally {
		chatStore.setSiderLoading(false)
	}
}

const handleDeleteDebounce = debounce(handleDelete, 600)

function isActive(uuid: number) {
	return chatStore.active === uuid
}

onMounted(async () => {
	if (authStore.session?.auth)
		return

	chatStore.setSiderLoading(true)
	try {
		await chatStore.fetchHistory()
	}
	catch (error) {
		ms.error(`${error}`)
	}
	finally {
		chatStore.setSiderLoading(false)
	}
})
</script>

<template>
	<NScrollbar class="px-4 pl-0">
		<div class="flex flex-col gap-2 text-sm">
			<template v-if="!dataSources.length">
				<div class="flex flex-col items-center mt-4 text-center text-neutral-300">
					<SvgIcon icon="ri:inbox-line" class="mb-2 text-3xl" />
					<span>{{ $t('common.noData') }}</span>
				</div>
			</template>
			<template v-else>
				<template v-if="!chatStore.siderLoading">
					<div v-for="(item, index) of dataSources" :key="index">
						<a class="relative flex items-center gap-3 p-3 break-all rounded-md cursor-pointer hover:bg-neutral-100 group dark:hover:bg-[#303030]"
							:class="isActive(item.uuid) && ['bg-[#4FB3D2]/[.15]', 'text-[#38AACC]', 'pr-14']"
							@click="handleSelect(item)">
							<span v-if="isDigitalPerson">
								<NAvatar :size="24" :src="item.icon" />
							</span>
							<span v-else>
								<SvgIcon :icon="item.icon" class="text-2xl" />
							</span>
							<div class="relative flex-1 overflow-hidden break-all text-ellipsis whitespace-nowrap">
								<span>{{ item.title }}</span>
							</div>
							<div v-if="isActive(item.uuid)" class="absolute z-10 flex visible right-1">
								<button class="p-1" v-if="!isDigitalPerson">
									<SvgIcon icon="ri:edit-line" @click="handleEdit($event)" />
								</button>
								<NPopconfirm placement="bottom" @positive-click="handleDeleteDebounce(item, $event)">
									<template #trigger>
										<button class="p-1">
											<SvgIcon icon="ri:delete-bin-line" />
										</button>
									</template>
									{{ $t('chat.deleteHistoryConfirm') }}
								</NPopconfirm>
							</div>
						</a>
					</div>
				</template>
				<!-- 以下为骨架屏 -->
				<template v-else>
					<div v-for="(_, index) in 5" :key="index" class="px-2">
						<NSkeleton height="32px" width="32px" class="inline-block mr-4" />
						<NSkeleton height="32px" width="calc(100% - 60px)" class="inline-block" />
					</div>
				</template>
			</template>
		</div>
	</NScrollbar>
	<AddHistoryModal v-model:show="showHistoryModal" mode="modify" />
</template>
