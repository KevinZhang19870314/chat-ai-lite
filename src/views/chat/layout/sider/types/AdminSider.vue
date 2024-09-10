<script setup lang='ts'>
import type { MenuOption } from 'naive-ui'
import { NMenu } from 'naive-ui'
import { computed, h } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useIconRender } from '@/hooks/useIconRender'
import { t } from '@/locales'
import { useUserStore } from '@/store'

const { iconRender } = useIconRender()
const router = useRouter()
const userStore = useUserStore()

const menuValue = computed(() => router.currentRoute.value.name ? router.currentRoute.value.name.toString() : 'Personal Center')

const adminMenus: MenuOption[] = [
	{
		label: () =>
			h(
				RouterLink,
				{
					to: {
						name: 'Personal Center',
					},
				},
				{ default: () => t('admin.personalCenter') },
			),
		key: 'Personal Center',
		icon: iconRender({ icon: 'tdesign:personal-information' }),
	},
	{
		key: 'divider-1',
		type: 'divider',
		props: {
			style: {
				marginLeft: '32px',
			},
		},
	},
	{
		label: () =>
			h(
				RouterLink,
				{
					to: {
						name: 'User Management',
					},
				},
				{ default: () => t('admin.userManagement') },
			),
		key: 'User Management',
		icon: iconRender({ icon: 'mdi:users' }),
	},
	{
		label: () =>
			h(
				RouterLink,
				{
					to: {
						name: 'AI Assistant Management',
					},
				},
				{ default: () => t('admin.aiAssistantManagement') },
			),
		key: 'AI Assistant Management',
		icon: iconRender({ icon: 'file-icons:openpolicyagent' }),
	},
]

const noneAdminMenus: MenuOption[] = [
	{
		label: () =>
			h(
				RouterLink,
				{
					to: {
						name: 'Personal Center',
					},
				},
				{ default: () => t('admin.personalCenter') },
			),
		key: 'Personal Center',
		icon: iconRender({ icon: 'tdesign:personal-information' }),
	},
	{
		key: 'divider-1',
		type: 'divider',
		props: {
			style: {
				marginLeft: '32px',
			},
		},
	},
]

const menuOptions = computed(() => {
	return userStore.isAdminAndAbove ? adminMenus : noneAdminMenus
})
</script>

<template>
	<div class="flex flex-col w-[240px]">
		<NMenu :value="menuValue" :options="menuOptions" />
	</div>
</template>
