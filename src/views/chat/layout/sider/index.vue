<script setup lang='ts'>
import type { CSSProperties } from 'vue'
import { computed, ref, watch } from 'vue'
import { NButton, NLayoutSider } from 'naive-ui'
import AIModeGroup from '../../components/AIModeGroup/index.vue'
import { useAIMode } from '../../hooks/useAIMode'
import List from './List.vue'
import Footer from './Footer.vue'
import MyFavoritesSider from './types/MyFavoritesSider.vue'
import ChatLLMSider from './types/ChatLLMSider.vue'
import AISquareSider from './types/AISquareSider.vue'
import AdminSider from './types/AdminSider.vue'
import TextToImageSider from './types/TextToImageSider.vue'
import DigitalPersonSider from './types/DigitalPersonSider.vue'
import { useAppStore, useChatStore } from '@/store'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { generateSessionId } from '@/utils/functions'
import { AiMode } from '@/models/chat.model'

const appStore = useAppStore()
const chatStore = useChatStore()

const { aiMode } = useAIMode()
const mode = AiMode

const { isMobile } = useBasicLayout()
const show = ref(false)

const collapsed = computed(() => appStore.siderCollapsed)
const isDark = computed(() => appStore.theme === 'dark')

function handleAdd() {
	chatStore.addHistory({ title: 'New Chat', uuid: generateSessionId(), isEdit: false })
	if (isMobile.value)
		appStore.setSiderCollapsed(true)
}

function handleUpdateCollapsed() {
	appStore.setSiderCollapsed(!collapsed.value)
}

const getMobileClass = computed<CSSProperties>(() => {
	if (isMobile.value) {
		return {
			position: 'fixed',
			zIndex: 50,
		}
	}
	return {}
})

const mobileSafeArea = computed(() => {
	if (isMobile.value) {
		return {
			paddingBottom: 'env(safe-area-inset-bottom)',
		}
	}
	return {}
})

watch(
	isMobile,
	(val) => {
		appStore.setSiderCollapsed(val)
	},
	{
		immediate: true,
		flush: 'post',
	},
)
</script>

<template>
	<NLayoutSider :collapsed="collapsed" :collapsed-width="60" :width="300"
		:show-trigger="isMobile ? false : 'arrow-circle'" collapse-mode="transform" position="absolute" bordered
		:style="getMobileClass" class="sider" :content-style="{ 'min-width': 0 }" @update-collapsed="handleUpdateCollapsed">
		<div class="flex flex-col h-full" :style="mobileSafeArea">
			<main class="flex flex-col flex-1 min-h-0">
				<div class="flex flex-row overflow-hidden">
					<AIModeGroup />
					<div v-show="!collapsed" class="flex border-l-[1px] pl-2 h-full"
						:class="isDark ? 'border-l-neutral-800' : 'border-l-neutral-200'">
						<template v-if="aiMode === mode.MyFavorites">
							<MyFavoritesSider />
						</template>
						<template v-else-if="aiMode === mode.ChatLLM">
							<ChatLLMSider />
						</template>
						<template v-else-if="aiMode === mode.KnowledgeBase">
							<AISquareSider />
						</template>
						<template v-else-if="aiMode === mode.Admin">
							<AdminSider />
						</template>
						<template v-else-if="aiMode === mode.DigitalPerson">
							<DigitalPersonSider />
						</template>
						<template v-else-if="aiMode === mode.TextToImage">
							<TextToImageSider />
						</template>
						<template v-else>
							<div class="flex flex-col w-[240px]">
								<div class="p-4 pl-0">
									<NButton dashed block @click="handleAdd">
										{{ $t('chat.newChatButton') }}
									</NButton>
								</div>
								<div class="flex-1 min-h-0 pb-4 pl-0 overflow-hidden">
									<List :ai-mode="AiMode.ChatLLM" />
								</div>
								<div class="p-4 pl-0 flex flex-col gap-2">
									<NButton block @click="show = true">
										{{ $t('store.siderButton') }}
									</NButton>
								</div>
							</div>
						</template>
					</div>
				</div>
			</main>
			<Footer />
		</div>
	</NLayoutSider>
	<template v-if="isMobile">
		<div v-show="!collapsed" class="fixed inset-0 z-40 bg-black/40" @click="handleUpdateCollapsed" />
	</template>
</template>
