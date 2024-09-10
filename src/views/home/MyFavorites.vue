<script setup lang='ts'>
import { NButton, NInput, NTabPane, NTabs } from 'naive-ui'
import { computed, ref } from 'vue'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { SvgIcon } from '@/components/common'
import { useAppStore, useChatStore } from '@/store'
import { AiMode } from '@/models/chat.model'
import MyFavTable from '@/views/home/components/MyFavTable/index.vue'
import { AIAssistantCategories } from '@/utils/constants'

const { isMobile } = useBasicLayout()
const chatStore = useChatStore()
const appStore = useAppStore()

const collapsed = computed(() => appStore.siderCollapsed)
const searchValue = ref('')
const termValue = ref('')
const tabs = AIAssistantCategories

chatStore.setAIMode(AiMode.MyFavorites)

function handleSearch() {
	termValue.value = searchValue.value
}
</script>

<template>
	<div class="max-w-screen-2xl flex flex-col m-auto" :class="[isMobile ? 'p-2' : 'p-4', collapsed ? 'pl-[80px]' : 'p-4']">
		<div class="pt-4 flex text-2xl font-extrabold items-center justify-center">
			<span class="px-2">{{ `${$t('store.promptStore')}` }}</span>
		</div>
		<div class="py-8 flex items-center justify-center m-auto gap-4 w-[800px]">
			<NInput v-model:value="searchValue" autofocus :placeholder="$t('common.search')" @keyup.enter="handleSearch" />
			<NButton type="primary" @click="handleSearch">
				<SvgIcon class="text-xl" icon="ic:sharp-search" />
				{{ $t('common.search') }}
			</NButton>
		</div>
		<NTabs default-value="all">
			<template #prefix>
				{{ $t('store.category') }}
			</template>
			<NTabPane v-for="(tab, index) in tabs" :key="index"
				:tab="tab.category === 'likes' ? (`🔥${$t(tab.titleI18n)}`) : $t(tab.titleI18n)" :name="tab.category">
				<MyFavTable :term="termValue" :category="tab.category" />
			</NTabPane>
		</NTabs>
	</div>
</template>
