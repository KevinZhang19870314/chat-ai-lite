<script lang="ts" setup>
import { computed, ref } from 'vue'
import { NTabPane, NTabs } from 'naive-ui'

import { useBasicLayout } from '@/hooks/useBasicLayout'
import { useAppStore } from '@/store'
import UserInfo from './components/UserInfo.vue'

const appStore = useAppStore()
const { isMobile } = useBasicLayout()
const collapsed = computed(() => appStore.siderCollapsed)
const currentTabIndex = ref(0)
</script>

<template>
	<div class="max-w-screen-2xl flex flex-col justify-center m-auto overflow-auto"
		:class="[isMobile ? 'p-2' : 'p-4', collapsed ? 'pl-[80px]' : 'p-4']">
		<NTabs v-model:value="currentTabIndex" type="line">
			<NTabPane :tab="$t('admin.userInfo')" :name="0">
				<UserInfo />
			</NTabPane>
		</NTabs>
	</div>
</template>

<style lang="less" scoped></style>
