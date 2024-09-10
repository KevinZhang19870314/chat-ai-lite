<script setup lang='ts'>
import { computed, defineAsyncComponent, ref } from 'vue'
import { NButton, NModal, NP, NSpace, NText } from 'naive-ui'
import FileUpload from './FileUpload.vue'
import { useAISquareStore, useUserStore } from '@/store'
import { SvgIcon } from '@/components/common'
import { AiMode } from '@/models/chat.model'

interface Props {
	visible: boolean
	aiMode?: AiMode
}
interface Emit {
	(e: 'update:visible', visible: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emit>()

const maxFileSize = computed(() => {
	return 3
})
const uploadFileTable = ref()
const loading = ref(false)
const UploadFileTable = defineAsyncComponent(() => import('@/views/home/components/UploadFileTable/index.vue'))
const userStore = useUserStore()

const aiSquareStore = useAISquareStore()
const show = computed({
	get() {
		return props.visible
	},
	set(visible: boolean) {
		emit('update:visible', visible)
	},
})

const currentKnowledgeBase = computed(() => aiSquareStore.currentKnowledgeBase)
const canDeleteDoc = computed(() => {
	return userStore.isAdminAndAbove || (!userStore.isAdminAndAbove && !currentKnowledgeBase.value!.is_global)
})

function handleRefresh() {
	uploadFileTable.value.refresh()
}
</script>

<template>
	<NModal v-model:show="show" :mask-closable="false" :title="currentKnowledgeBase?.name || ''" :auto-focus="false"
		preset="card" style="width: 95%; max-width: 860px">
		<div class="min-h-[100px]">
			<NSpace class="mb-4">
				<NText class="text-base block mt-2">
					{{ $t('upload.uploadFileTips') }}
				</NText>
				<NP depth="3" style="font-size: 12px;">
					{{ $t('upload.uploadFileFormat') }}
					{{ $t('upload.uploadFileSizeLimit', { size: `${maxFileSize}M` }) }}
				</NP>
			</NSpace>
			<NSpace justify="end" class="px-2">
				<FileUpload mode="button" :ai-mode="$props.aiMode" />
				<NButton type="info" :loading="loading" strong tertiary @click="handleRefresh">
					<template #icon>
						<SvgIcon icon="tabler:refresh-dot" class="text-yellow-600" />
					</template>
					{{ $t('common.refresh') }}
				</NButton>
			</NSpace>
			<UploadFileTable ref="uploadFileTable" :can-delete="canDeleteDoc" :ai-mode="$props.aiMode" />
		</div>
	</NModal>
</template>
