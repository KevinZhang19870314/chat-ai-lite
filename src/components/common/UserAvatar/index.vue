<script setup lang='ts'>
import { computed, h } from 'vue'
import { NAvatar, NDropdown, useMessage } from 'naive-ui'
import { RouterLink } from 'vue-router'
import { useAppStore, useAuthStore, useUserStore } from '@/store'
import defaultAvatar from '@/assets/avatar.jpg'
import { isString } from '@/utils/is'
import { t } from '@/locales'
import { router } from '@/router'
import { useIconRender } from '@/hooks/useIconRender'

const { iconRender } = useIconRender()
const userStore = useUserStore()
const authStore = useAuthStore()
const ms = useMessage()
const appStore = useAppStore()

const userInfo = computed(() => userStore.userInfo)
const collapsed = computed(() => appStore.siderCollapsed)
const options = [
	{
		label: () =>
			h(
				RouterLink,
				{
					to: {
						name: 'Personal Center',
					},
				},
				{ default: () => h('div', { class: 'flex items-center pr-12' }, { default: () => t('admin.personalCenter') }) },
			),
		key: 'Personal Center',
		icon: iconRender({ icon: 'tdesign:personal-information', fontSize: 18 }),
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
				'div',
				{
					class: 'flex items-center pr-12',
				},
				{ default: () => t('common.logout') },
			),
		key: 'Log Out',
		icon: iconRender({ icon: 'material-symbols:logout', fontSize: 18 }),
		props: {
			onClick: () => {
				handleLogout()
			},
		},
	},
]

function handleLogout() {
	authStore.removeToken()
	authStore.removeRefreshToken()
	ms.warning(t('common.logoutSuccess'))
	router.push('/authorize')
}
</script>

<template>
	<div class="flex items-center overflow-hidden">
		<div class="w-10 h-10 overflow-hidden rounded-full shrink-0 cursor-pointer">
			<NDropdown :options="options" placement="top-end" trigger="click">
				<template v-if="isString(userInfo.avatar) && userInfo.avatar.length > 0">
					<NAvatar size="large" round :src="userInfo.avatar" :fallback-src="defaultAvatar" />
				</template>
				<template v-else>
					<NAvatar size="large" round :src="defaultAvatar" />
				</template>
			</NDropdown>
		</div>
		<div v-if="!collapsed" class="flex-1 min-w-0 ml-2">
			<h2 class="overflow-hidden font-bold text-md text-ellipsis whitespace-nowrap">
				{{ userInfo.nickname ? userInfo.nickname : userInfo.email }}
			</h2>
			<p class="overflow-hidden text-xs text-gray-500 text-ellipsis whitespace-nowrap">
				<span v-if="isString(userInfo.description) && userInfo.description !== ''" v-html="userInfo.description" />
			</p>
		</div>
	</div>
</template>
