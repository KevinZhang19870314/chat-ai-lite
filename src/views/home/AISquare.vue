<script lang="ts" setup>
import { NButton, NDivider, NSpace, NTabPane, NTabs } from 'naive-ui'

import { computed, defineAsyncComponent, ref } from 'vue'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { AiMode } from '@/models/chat.model'
import { useAISquareStore, useAppStore, useChatStore } from '@/store'
import LocalAITable from '@/views/home/components/LocalAITable/index.vue'
import PluginList from '@/views/home/components/PluginList/index.vue'

const NewLocalAI = defineAsyncComponent(() => import('@/views/home/components/NewLocalAI/index.vue'))
const { isMobile } = useBasicLayout()
const appStore = useAppStore()
const chatStore = useChatStore()
const aiSquareStore = useAISquareStore()

chatStore.setAIMode(AiMode.KnowledgeBase)

const localAITable = ref()
const loading = ref(false)
const showNewLocalAIModal = ref(false)
const showPluginListModal = ref(false)
const collapsed = computed(() => appStore.siderCollapsed)

function handleRefreshLocalAITable() {
	localAITable.value.refresh()
}

function handleAddLocalAI() {
	showNewLocalAIModal.value = !showNewLocalAIModal.value
}

function handlePlugins() {
	showPluginListModal.value = !showPluginListModal.value
}
</script>

<template>
	<div class="max-w-screen-2xl flex flex-col justify-center m-auto"
		:class="[isMobile ? 'p-2' : 'p-4', collapsed ? 'pl-[80px]' : 'p-4']">
		<NTabs v-model:value="aiSquareStore.currentKnowledgeBaseTab" type="bar" placement="top" size="large">
			<NTabPane :tab="$t('localAI.localVectorKnowledgeBase')" name="localai">
				<NSpace class="pt-4 w-full" vertical>
					<div class="text-xl pb-4 font-medium">
						{{ $t('chat.localAISlogan') }}
					</div>
				</NSpace>
				<NSpace justify="start" class="w-full">
					<NButton type="primary" strong @click="handleAddLocalAI">
						{{ $t('chat.newLocalAI') }}
					</NButton>
					<NButton type="default" :loading="loading" strong @click="handlePlugins">
						{{ $t('chat.plugins') }}
					</NButton>
					<NButton type="default" :loading="loading" strong @click="handleRefreshLocalAITable">
						{{ $t('common.refresh') }}
					</NButton>
				</NSpace>
				<NDivider />
				<LocalAITable ref="localAITable" term="" category="all" />
			</NTabPane>
		</NTabs>
	</div>
	<NewLocalAI v-if="showNewLocalAIModal" v-model:visible="showNewLocalAIModal" mode="add" />
	<PluginList v-if="showPluginListModal" v-model:visible="showPluginListModal" />
</template>
