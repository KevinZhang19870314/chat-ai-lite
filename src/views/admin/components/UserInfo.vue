<script setup lang="ts">
import type { SelectOption } from 'naive-ui'
import { NButton, NInput, NPopconfirm, NSelect, NTooltip, useMessage } from 'naive-ui'
import { computed, h, ref, onMounted } from 'vue'
import { SvgIcon } from '@/components/common'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { t } from '@/locales'
import { useAppStore, useAuthStore, useUserStore } from '@/store'
import type { Language, Theme } from '@/store/modules/app/helper'
import type { UserInfo } from '@/store/modules/user/helper'
import { getCurrentDate } from '@/utils/functions'

const appStore = useAppStore()
const userStore = useUserStore()
const ms = useMessage()
const authStore = useAuthStore()

const { isMobile } = useBasicLayout()
const collapsed = computed(() => appStore.siderCollapsed)
const userInfo = computed(() => userStore.userInfo)

const avatar = ref(userInfo.value.avatar ?? '')
const email = ref(userInfo.value.email ?? '')
const nickname = ref(userInfo.value.nickname ?? '')
const description = ref(userInfo.value.description ?? '')
const model = ref(userInfo.value.model ?? 'gpt-3.5-turbo')
const modelOptions = computed(() => userStore.getModels())
const remainingTextToImageRequests = ref(userInfo.value.total_image_requests! - userInfo.value.used_image_requests!)

const language = computed({
	get() {
		return appStore.language
	},
	set(value: Language) {
		appStore.setLanguage(value)
	},
})
const languageOptions: { label: string, key: Language, value: Language }[] = [
	{ label: '简体中文', key: 'zh-CN', value: 'zh-CN' },
	{ label: 'English', key: 'en-US', value: 'en-US' },
	{ label: '日本語', key: 'ja-JP', value: 'ja-JP' },
]

const theme = computed(() => appStore.theme)
const themeOptions: { label: string, key: Theme, icon: string }[] = [
	{
		label: 'Auto',
		key: 'auto',
		icon: 'ri:contrast-line',
	},
	{
		label: 'Light',
		key: 'light',
		icon: 'ri:sun-foggy-line',
	},
	{
		label: 'Dark',
		key: 'dark',
		icon: 'ri:moon-foggy-line',
	},
]

function renderLabel(option: SelectOption) {
	return [
		h('div', {
			class: 'flex items-center gap-2',
		}, [
			h(
				SvgIcon,
				{
					icon: `${option.icon}`,
					class: 'text-lg',
				},
			),
			option.label as string,
		]),
	]
}

function updateNickname(options: Partial<UserInfo>) {
	try {
		userStore.updateUserInfo(options)
		userStore.updateNicknameToDB(`${userInfo.value.id}`, `${options.nickname}`)
		ms.success(t('common.success'))
	}
	catch (error) {
		ms.error(`${error}`)
	}
}

function updateDescription(options: Partial<UserInfo>) {
	try {
		userStore.updateUserInfo(options)
		userStore.updateDescriptionToDB(`${userInfo.value.id}`, `${options.description}`)
		ms.success(t('common.success'))
	}
	catch (error) {
		ms.error(`${error}`)
	}
}

function updateAvatar(options: Partial<UserInfo>) {
	try {
		userStore.updateUserInfo(options)
		userStore.updateAvatarToDB(`${userInfo.value.id}`, `${options.avatar}`)
		ms.success(t('common.success'))
	}
	catch (error) {
		ms.error(`${error}`)
	}
}

function exportData(): void {
	const date = getCurrentDate()
	const data: string = localStorage.getItem('chatStorage') || '{}'
	const jsonString: string = JSON.stringify(JSON.parse(data), null, 2)
	const blob: Blob = new Blob([jsonString], { type: 'application/json' })
	const url: string = URL.createObjectURL(blob)
	const link: HTMLAnchorElement = document.createElement('a')
	link.href = url
	link.download = `chat-store_${date}.json`
	document.body.appendChild(link)
	link.click()
	document.body.removeChild(link)
}

function importData(event: Event): void {
	const target = event.target as HTMLInputElement
	if (!target || !target.files)
		return

	const file: File = target.files[0]
	if (!file)
		return

	const reader: FileReader = new FileReader()
	reader.onload = () => {
		try {
			const data = JSON.parse(reader.result as string)
			localStorage.setItem('chatStorage', JSON.stringify(data))
			ms.success(t('common.success'))
			location.reload()
		}
		catch (error) {
			ms.error(t('common.invalidFileFormat'))
		}
	}
	reader.readAsText(file)
}

function clearData(): void {
	localStorage.removeItem('chatStorage')
	location.reload()
}

function handleImportButtonClick(): void {
	const fileInput = document.getElementById('fileInput') as HTMLElement
	if (fileInput)
		fileInput.click()
}

async function updateModel(options: Partial<UserInfo>) {
	try {
		userStore.updateUserInfo(options)
		await userStore.updateModelToDB(`${userInfo.value.id}`, `${options.model}`)
		ms.success(t('common.success'))
	}
	catch (error) {
		ms.error(`${error}`)
	}
}

onMounted(() => {
	authStore.getSession()
})
</script>

<template>
	<div class="max-w-screen-2xl flex flex-col justify-center m-auto overflow-auto"
		:class="[isMobile ? 'p-2' : 'p-4', collapsed ? 'pl-[80px]' : 'p-4']">
		<div class="flex flex-col justify-center gap-8 mt-4">
			<!-- 邮箱 -->
			<div class="flex items-center space-x-4">
				<span class="flex-shrink-0 w-[100px]">{{ $t('setting.email') }}</span>
				<div class="w-[220px]">
					<NInput v-model:value="email" readonly />
				</div>
			</div>
			<!-- 昵称 -->
			<div class="flex items-center space-x-4">
				<span class="flex-shrink-0 w-[100px]">{{ $t('setting.nickname') }}</span>
				<div class="w-[220px]">
					<NInput v-model:value="nickname" :placeholder="$t('setting.nicknamePlaceholder')" />
				</div>
				<NButton size="tiny" text type="primary" @click="updateNickname({ nickname })">
					{{ $t('common.save') }}
				</NButton>
			</div>
			<!-- 描述 -->
			<div class="flex items-center space-x-4">
				<span class="flex-shrink-0 w-[100px]">{{ $t('setting.description') }}</span>
				<div class="w-[440px]">
					<NInput v-model:value="description" placeholder="" />
				</div>
				<NButton size="tiny" text type="primary" @click="updateDescription({ description })">
					{{ $t('common.save') }}
				</NButton>
			</div>
			<!-- 头像链接 -->
			<div class="flex items-center space-x-4">
				<span class="flex-shrink-0 w-[100px]">{{ $t('setting.avatarLink') }}</span>
				<div class="w-[440px]">
					<NInput v-model:value="avatar" placeholder="" />
				</div>
				<NButton size="tiny" text type="primary" @click="updateAvatar({ avatar })">
					{{ $t('common.save') }}
				</NButton>
			</div>
			<!-- 用户类型 -->
			<div class="flex items-center space-x-4">
				<span class="flex-shrink-0 w-[100px]">{{ $t('admin.userType') }}</span>
				<div>
					<div v-if="userStore.isSuperAdmin">
						{{ $t('admin.superAdmin') }}
					</div>
					<div v-else-if="userStore.isAdmin">
						{{ $t('admin.adminUser') }}
					</div>
					<div v-else class="flex items-center gap-2">
						<div>
							{{ userStore.isNormal ? $t('admin.normalUser') : $t('admin.premiumUser') }}
						</div>
					</div>
				</div>
			</div>
			<!-- 模型选择 -->
			<div class="flex items-center space-x-4">
				<span class="flex-shrink-0 w-[100px]">{{ $t('admin.model') }}</span>
				<div class="flex flex-wrap items-center gap-4">
					<NSelect v-model:value="model" style="width: 320px" :options="modelOptions" :render-label="renderLabel" />
				</div>
				<NButton size="tiny" text type="primary" @click="updateModel({ model })">
					{{ $t('common.save') }}
				</NButton>
			</div>
			<!-- 文生图剩余次数 -->
			<div class="flex items-center space-x-4">
				<span class="flex-shrink-0 w-[100px]">{{ $t('textToImages.remainingTextToImageRequests') }}</span>
				<div>
					<div>
						{{ $t('textToImages.nTimes', { times: remainingTextToImageRequests }) }}
					</div>
				</div>
			</div>
			<!-- 聊天记录 -->
			<div class="flex items-center space-x-4">
				<span class="flex-shrink-0 w-[100px]">{{ $t('setting.chatHistory') }}</span>

				<div class="flex flex-wrap items-center gap-4">
					<NButton size="small" @click="exportData">
						<template #icon>
							<SvgIcon icon="ri:download-2-fill" />
						</template>
						{{ $t('common.export') }}
					</NButton>

					<input id="fileInput" type="file" style="display:none" @change="importData">
					<NButton size="small" @click="handleImportButtonClick">
						<template #icon>
							<SvgIcon icon="ri:upload-2-fill" />
						</template>
						{{ $t('common.import') }}
					</NButton>

					<NPopconfirm placement="bottom" @positive-click="clearData">
						<template #trigger>
							<NButton size="small">
								<template #icon>
									<SvgIcon icon="ri:close-circle-line" />
								</template>
								{{ $t('common.clear') }}
							</NButton>
						</template>
						{{ $t('chat.clearHistoryConfirm') }}
					</NPopconfirm>
				</div>
			</div>
			<!-- 主题 -->
			<div class="flex items-center space-x-4">
				<span class="flex-shrink-0 w-[100px]">{{ $t('setting.theme') }}</span>
				<div class="flex flex-wrap items-center gap-4">
					<template v-for="item of themeOptions" :key="item.key">
						<NTooltip>
							<template #trigger>
								<NButton size="small" :type="item.key === theme ? 'primary' : undefined"
									@click="appStore.setTheme(item.key)">
									<template #icon>
										<SvgIcon :icon="item.icon" />
									</template>
								</NButton>
							</template>
							{{ item.label }}
						</NTooltip>
					</template>
				</div>
			</div>
			<!-- 语言 -->
			<div class="flex items-center space-x-4">
				<span class="flex-shrink-0 w-[100px]">{{ $t('setting.language') }}</span>
				<div class="flex flex-wrap items-center gap-4">
					<NSelect style="width: 140px" :value="language" :options="languageOptions"
						@update-value="(value: any) => appStore.setLanguage(value)" />
				</div>
			</div>
			<template v-if="userStore.isAdminAndAbove">
				<!-- 是否管理员 -->
				<div class="flex items-center space-x-4">
					<span class="flex-shrink-0 w-[100px]">{{ $t('admin.isAdmin') }}</span>
					<SvgIcon :icon="userStore.isAdminAndAbove ? 'dashicons:yes' : 'dashicons:no'" class="text-2xl"
						:class="[userStore.isAdminAndAbove ? 'text-green-500' : 'text-red-500']" />
				</div>
				<!-- 是否飞书用户 -->
				<div class="flex items-center space-x-4">
					<span class="flex-shrink-0 w-[100px]">{{ $t('admin.isFeiShuUser') }}</span>
					<SvgIcon :icon="userStore.userInfo.is_feishu_user ? 'dashicons:yes' : 'dashicons:no'" class="text-2xl"
						:class="[userStore.userInfo.is_feishu_user ? 'text-green-500' : 'text-red-500']" />
				</div>
				<!-- 是否Github用户 -->
				<div class="flex items-center space-x-4">
					<span class="flex-shrink-0 w-[100px]">{{ $t('admin.isGithubUser') }}</span>
					<SvgIcon :icon="userStore.userInfo.is_github_user ? 'dashicons:yes' : 'dashicons:no'" class="text-2xl"
						:class="[userStore.userInfo.is_github_user ? 'text-green-500' : 'text-red-500']" />
				</div>
			</template>
		</div>
	</div>
</template>

<style lang="less" scoped></style>
