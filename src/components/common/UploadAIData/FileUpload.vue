<script lang="ts" setup>
import type { UploadFileInfo } from 'naive-ui'
import { NButton, NIcon, NP, NText, NUpload, NUploadDragger, useMessage } from 'naive-ui'
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5'
import { computed, ref } from 'vue'
import { t } from '@/locales'
import { useAISquareStore, useAuthStore } from '@/store'
import { SvgIcon } from '@/components/common'
import { AiMode } from '@/models/chat.model'

interface Props {
	mode: 'button' | 'card'
	/** 是否支持多选 */
	multiple?: boolean
	/** 限制上传文件数量 */
	max?: number
	aiMode?: AiMode
	/** 当mode为card时，需要传入 */
	uploadFileTipsI18n?: string
	/** 当mode为card时，需要传入 */
	uploadFileFormatI18n?: string
	/** 当mode为card时，需要传入 */
	uploadFileSizeLimitI18n?: string
	/** 使用v-model:value绑定时，需要此字段 */
	value?: any
}

interface Emit {
	(e: 'update:value', value: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emit>()

const ms = useMessage()
const loading = ref(false)
const maxFileSize = computed(() => {
	return 3
})
const authStore = useAuthStore()
const aiSquareStore = useAISquareStore()
const uploadAction = computed(() => {
	return '/deep-ai/local-ai/ingest-file'
})

const currentKnowledgeBase = computed(() => aiSquareStore.currentKnowledgeBase)
const headers = computed(() => {
	return {
		Authorization: `Bearer ${authStore.token}`,
	}
})

function handleFinish({
	file,
	event,
}: {
	file: UploadFileInfo
	event?: ProgressEvent
}) {
	loading.value = false
	const response = (event?.currentTarget as any)?.response
	try {
		const res = JSON.parse(response)
		if (res.status === 'Error') {
			ms.error(res.message)
			emit('update:value', '')
		}
		else {
			ms.success(t('upload.uploadFileSuccess'))
			emit('update:value', res.data)
		}
	}
	catch (error) { }
	return file
}

function handleError({
	file,
	event,
}: {
	file: UploadFileInfo
	event?: any
}) {
	loading.value = false
	ms.error(event?.target?.response || t('upload.uploadFileFailed'))
	emit('update:value', '')
	return file
}

async function handleBeforeUpload(data: {
	file: UploadFileInfo
	fileList: UploadFileInfo[]
}) {
	loading.value = true
	// limit the uplaod file size
	const fileSize = data.file.file?.size || 0
	if (fileSize > maxFileSize.value * 1024 * 1024) {
		ms.error(t('upload.uploadFileSizeLimit', { size: `${maxFileSize.value}M` }))
		return false
	}

	return true
}

const data = computed(() => {
	let result: any = {
		knowledge_base_id: `${currentKnowledgeBase.value?.id}`,
		assistant_id: `${currentKnowledgeBase.value?.assistant_id}`,
	}

	return result
})
</script>

<template>
	<NUpload :multiple="props.multiple !== undefined ? props.multiple : true" directory-dnd :action="uploadAction"
		:max="props.max !== undefined ? props.max : 5" :data="data" :headers="headers" :show-file-list="props.mode === 'card'"
		@before-upload="handleBeforeUpload" @finish="handleFinish" @error="handleError">
		<template v-if="props.mode === 'card'">
			<NUploadDragger>
				<div>
					<NIcon size="32" :depth="3">
						<ArchiveIcon />
					</NIcon>
				</div>
				<NText class="text-sm block mt-2">
					{{ $t(props.uploadFileTipsI18n || '') }}
				</NText>
				<NP depth="3" class="block" style="font-size: 12px; margin: 8px 0 0 0;">
					{{ $t(props.uploadFileFormatI18n || '') }}
					{{ $t(props.uploadFileSizeLimitI18n || '', { size: `${maxFileSize}M` }) }}
				</NP>
			</NUploadDragger>
		</template>
		<template v-else>
			<NButton type="primary" :loading="loading" block>
				<template #icon>
					<SvgIcon icon="uil:upload" class="text-base" />
				</template>
				{{ $t('common.upload') }}
			</NButton>
		</template>
	</NUpload>
</template>
