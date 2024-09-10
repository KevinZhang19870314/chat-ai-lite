<script setup lang='ts'>
import type { MenuOption } from 'naive-ui'
import { NMenu } from 'naive-ui'
import { computed, h } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useIconRender } from '@/hooks/useIconRender'
import { t } from '@/locales'

const { iconRender } = useIconRender()
const router = useRouter()

const menuValue = computed(() => router.currentRoute.value.name ? router.currentRoute.value.name.toString() : 'Images Preview')

const menuOptions: MenuOption[] = [
	{
		label: () =>
			h(
				RouterLink,
				{
					to: {
						name: 'Images Preview',
					},
				},
				{ default: () => t('textToImages.imagesPreview') },
			),
		key: 'Images Preview',
		icon: iconRender({ icon: 'solar:chat-round-video-broken' }),
	},
	{
		label: () =>
			h(
				RouterLink,
				{
					to: {
						name: 'Generate Images',
					},
				},
				{ default: () => t('textToImages.genImages') },
			),
		key: 'Generate Images',
		icon: iconRender({ icon: 'fluent:video-clip-wand-24-regular' }),
	},
]
</script>

<template>
	<div class="flex flex-col w-[240px]">
		<NMenu :value="menuValue" :options="menuOptions" />
	</div>
</template>
