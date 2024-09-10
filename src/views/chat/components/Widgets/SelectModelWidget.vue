<script lang="ts" setup>
import { computed, h, onMounted, ref } from 'vue'
import type { SelectOption } from 'naive-ui'
import { NSelect } from 'naive-ui'
import { useChatStore, useUserStore } from '@/store'
import { SvgIcon } from '@/components/common'

interface Props {
	loading: boolean
}

const props = defineProps<Props>()

const userStore = useUserStore()
const chatStore = useChatStore()

const userInfo = computed(() => userStore.userInfo)
const model = ref(userInfo.value.model ?? 'gpt-3.5-turbo')
const modelOptions = computed(() => userStore.getModels())

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

function handleModelChange(val: string) {
	chatStore.setSelectedModel(val)
}

onMounted(() => {
	chatStore.setSelectedModel(model.value)
})
</script>

<template>
	<div class="flex items-center gap-2">
		<span>{{ $t('admin.model') }}</span>
		<NSelect v-model:value="model" style="width: 280px" :options="modelOptions" :disabled="props.loading"
			:render-label="renderLabel" @update-value="handleModelChange" />
	</div>
</template>
