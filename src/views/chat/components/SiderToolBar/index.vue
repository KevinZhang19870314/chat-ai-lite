<script setup lang='ts'>
import { NButton, NDropdown, NInput, NSpace, NTooltip } from 'naive-ui'
import { computed } from 'vue'
import { SvgIcon } from '@/components/common'
import { AiMode } from '@/models/chat.model'
import { t } from '@/locales'

interface Props {
	addButtonTips?: string
	search: string
	aiMode?: AiMode
}

interface Emit {
	(e: 'add', val?: AiMode): void
	(e: 'update:search', val: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emit>()

const newOptions = [
	{
		label: t('chat.newLocalAI'),
		key: AiMode.LocalAI,
	},
]

const searchValue = computed({
	get: () => props.search,
	set: (val: string) => emit('update:search', val),
})

function handleAdd() {
	emit('add')
}

function handleAddSelect(key: AiMode) {
	emit('add', key)
}
</script>

<template>
	<div class="p-4 pl-0">
		<NSpace align="center" :item-style="props.addButtonTips ? {} : { width: '100%' }" :wrap="false">
			<NInput v-model:value="searchValue" :placeholder="$t('common.search')" size="small" />
			<template v-if="props.aiMode === AiMode.KnowledgeBase">
				<NDropdown trigger="hover" placement="bottom-start" :options="newOptions" @select="handleAddSelect">
					<NButton size="small" type="primary" @click="handleAdd">
						<SvgIcon class="text-xl" icon="ri:add-fill" />
					</NButton>
				</NDropdown>
			</template>
			<template v-else>
				<NTooltip trigger="hover" v-if="props.addButtonTips">
					<template #trigger>
						<NButton size="small" type="primary" @click="handleAdd">
							<SvgIcon class="text-xl" icon="ri:add-fill" />
						</NButton>
					</template>
					{{ props.addButtonTips }}
				</NTooltip>
			</template>
		</NSpace>
	</div>
</template>
