<script lang="ts" setup>
import { computed, h, onMounted, reactive, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NAvatar, NButton, NDataTable, NInput, NSelect, NSpace, NSpin, useDialog, useMessage } from 'naive-ui'

import { useBasicLayout } from '@/hooks/useBasicLayout'
import { useAppStore, useUserStore } from '@/store'
import { t } from '@/locales'
import { SvgIcon } from '@/components/common'
import type { UserInfo } from '@/store/modules/user/helper'
import { UserType } from '@/store/modules/user/helper'

const appStore = useAppStore()
const dialog = useDialog()
const userStore = useUserStore()
const ms = useMessage()
const { isMobile } = useBasicLayout()
const collapsed = computed(() => appStore.siderCollapsed)
const loading = ref(false)
const searchValue = ref<string>('')
const UserTypeMapping = {
	[UserType.Normal as string]: t('admin.normalUser'),
	[UserType.Premium as string]: t('admin.premiumUser'),
	[UserType.Admin as string]: t('admin.adminUser'),
	[UserType.SuperAdmin as string]: t('admin.superAdmin'),
}
const userType = ref('')
const userTypeOptions = [
	{ label: t('common.all'), key: '', value: '' },
	{ label: t('admin.superAdmin'), key: 'super_admin', value: 'super_admin' },
	{ label: t('admin.adminUser'), key: 'admin', value: 'admin' },
	{ label: t('admin.premiumUser'), key: 'premium', value: 'premium' },
	{ label: t('admin.normalUser'), key: 'normal', value: 'normal' },
]

const userTypeBindingOptions = computed(() => userStore.isSuperAdmin ? userTypeOptions : userTypeOptions.filter(f => f.key !== 'super_admin'))

const userList = computed(() => userStore.userList)
const pagination = reactive({
	page: 1,
	itemCount: 1,
	pageSize: 10,
})
function createColumns(): DataTableColumns<UserInfo> {
	return [
		{
			title: t('setting.avatar'),
			key: 'avatar',
			align: 'left',
			width: 60,
			render(row) {
				return h(NAvatar, {
					round: true,
					src: row.avatar,
					size: 'small',
				})
			},
		},
		{
			title: t('setting.email'),
			key: 'email',
			width: 150,
		},
		{
			title: t('setting.nickname'),
			key: 'nickname',
			width: 150,
			render(row) {
				return h('span', {}, {
					default: () => `${row.nickname ? row.nickname : '-'}`,
				})
			},
		},
		{
			title: t('admin.model'),
			key: 'model',
			width: 150,
		},
		{
			title: t('textToImages.totalImageRequests'),
			key: 'total_image_requests',
			width: 150,
		},
		{
			title: t('setting.description'),
			key: 'description',
			width: 300,
		},
		{
			title: t('admin.userType'),
			key: 'type',
			width: 100,
			render(row) {
				return h('span', {
					class: `font-bold ${row.type === UserType.SuperAdmin
						? 'text-[#38AACC]'
						: (row.type === UserType.Admin
							? 'text-[#299AB4]'
							: (row.type === UserType.Premium ? 'text-blue-300' : 'text-gray-500'))}`,
				}, {
					default: () => UserTypeMapping[row.type!],
				})
			},
		},
		{
			title: t('common.action'),
			key: 'actions',
			width: 150,
			align: 'center',
			render(row) {
				const showDelButton = row.email !== userStore.userInfo.email && userStore.isSuperAdmin
				const delButtonContent = showDelButton
					? h(
						NButton,
						{
							tertiary: true,
							size: 'small',
							type: 'error',
							onClick: () => handleDelete(row),
						},
						{ default: () => t('common.delete') },
					)
					: ''
				const showUpgradeButton = row.type === UserType.Normal && userStore.isSuperAdmin
				const upgradeButtonContent = showUpgradeButton
					? h(
						NButton,
						{
							tertiary: true,
							size: 'small',
							type: 'primary',
							onClick: () => handleUpgrade(row),
						},
						{ default: () => t('admin.upgrade') },
					)
					: ''
				const showTextToImageButtonContent = userStore.isSuperAdmin
				const textToImageButtonContent = showTextToImageButtonContent
					? h(
						NButton,
						{
							tertiary: true,
							size: 'small',
							type: 'primary',
							onClick: () => handleAppendTextToImageRequests(row),
						},
						{ default: () => t('textToImages.genImages') },
					)
					: ''
				return h('div', { class: 'flex items-center justify-center flex-row gap-2' }, {
					default: () => [
						delButtonContent,
						upgradeButtonContent,
						textToImageButtonContent,
						(!showDelButton && !showUpgradeButton && !showTextToImageButtonContent) && '-',
					],
				})
			},
		},
	]
}

const columns = createColumns()
function renderTemplate() {
	return userList.value?.map((item: any) => {
		return item
	})
}
const dataSource = computed(() => {
	const data = renderTemplate()
	return data
})

async function refresh() {
	loading.value = true
	try {
		const total = await userStore.fetchUserListByPage(pagination.pageSize, pagination.page, searchValue.value, userType.value)
		pagination.itemCount = +total
	}
	catch (error) {
		ms.error(`${error}`)
	}
	finally {
		loading.value = false
	}
}

function handlePageChange(p: number) {
	pagination.page = p
	refresh()
}

function handleSearch() {
	refresh()
}

function handleDelete(row: UserInfo) {
	const d = dialog.warning({
		title: t('admin.deleteUser'),
		content: t('admin.deleteUserTips', { name: row.nickname || row.email }),
		positiveText: t('common.yes'),
		negativeText: t('common.no'),
		onPositiveClick: async () => {
			d.loading = true
			try {
				await userStore.deleteUser(row.id!)
				refresh()
			}
			catch (error) {
				ms.error(`${error}`)
			}
			finally {
				d.loading = false
			}
		},
	})
}

function handleUpgrade(row: UserInfo) {
	const d = dialog.warning({
		title: t('admin.upgradeUser'),
		content: t('admin.upgradeUserTips', { name: row.nickname || row.email }),
		positiveText: t('common.yes'),
		negativeText: t('common.no'),
		onPositiveClick: async () => {
			d.loading = true
			try {
				await userStore.upgradeToPremium(row.id!, row.total_image_requests! + 10)
				refresh()
			}
			catch (error) {
				ms.error(`${error}`)
			}
			finally {
				d.loading = false
			}
		},
	})
}

function handleAppendTextToImageRequests(row: UserInfo) {
	const times = 10
	const d = dialog.warning({
		title: t('textToImages.appendTextToImageRequests'),
		content: t('textToImages.appendTextToImageRequestsTips', { times: times }),
		positiveText: t('common.yes'),
		negativeText: t('common.no'),
		onPositiveClick: async () => {
			d.loading = true
			try {
				await userStore.appendTextToImageRequestsToDB(row.id!, row.total_image_requests! + times)
				ms.success(t('textToImages.appendTextToImageRequestsSuccess'))
				refresh()
			}
			catch (error) {
				ms.error(`${error}`)
			}
			finally {
				d.loading = false
			}
		},
	})
}

function handleUpdateUserType(value: string) {
	userType.value = value
	refresh()
}

onMounted(() => {
	refresh()
})
</script>

<template>
	<div class="max-w-screen-2xl flex flex-col justify-center m-auto overflow-auto"
		:class="[isMobile ? 'p-2' : 'p-4', collapsed ? 'pl-[80px]' : 'p-4']">
		<NSpace justify="start" align="center" class="pb-4 w-full mt-4">
			<div class="flex items-center gap-4">
				<span>{{ $t('setting.email') }}</span>
				<NInput v-model:value="searchValue" style="width: 320px;" autofocus @keyup.enter="handleSearch" />
			</div>
			<div class="flex items-center gap-4">
				<span>{{ $t('admin.userType') }}</span>
				<NSelect style="width: 140px" :value="userType" :options="userTypeBindingOptions"
					@update-value="handleUpdateUserType" />
			</div>
			<NButton type="primary" @click="handleSearch">
				<SvgIcon class="text-xl" icon="ic:sharp-search" />
				{{ $t('common.search') }}
			</NButton>
		</NSpace>
		<NSpin :show="loading">
			<div class="min-h-[100px]">
				<NDataTable :remote="true" :max-height="680" :columns="columns" :data="dataSource" :pagination="pagination"
					@update:page="handlePageChange" />
			</div>
		</NSpin>
	</div>
</template>

<style lang="less" scoped></style>
