<script setup lang='ts'>
import { defineAsyncComponent, ref } from 'vue'
import List from '../List.vue'
import { AiMode } from '@/models/chat.model'
import SiderToolBar from '@/views/chat/components/SiderToolBar/index.vue'

const NewLocalAI = defineAsyncComponent(() => import('@/views/home/components/NewLocalAI/index.vue'))

const searchValue = ref('')
const showNewLocalAIModal = ref(false)

async function handleAdd(val: AiMode | undefined) {
	if (val === AiMode.LocalAI)
		showNewLocalAIModal.value = !showNewLocalAIModal.value
}
</script>

<template>
	<div class="flex flex-col w-[240px]">
		<SiderToolBar v-model:search="searchValue" :add-button-tips="$t('chat.newLocalAI')" :ai-mode="AiMode.KnowledgeBase"
			@add="handleAdd" />
		<div class="flex-1 min-h-0 pb-4 pl-0 overflow-hidden">
			<List :ai-mode="AiMode.KnowledgeBase" :search="searchValue" />
		</div>
	</div>
	<NewLocalAI v-if="showNewLocalAIModal" v-model:visible="showNewLocalAIModal" mode="add" />
</template>
