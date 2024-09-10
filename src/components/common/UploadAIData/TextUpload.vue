<script lang="ts" setup>
import { NButton, NInput, NSelect, NSpin, useMessage } from 'naive-ui'
import { ref } from 'vue'
import { t } from '@/locales'
import { ingestText } from '@/api'
import { AiMode } from '@/models/chat.model'

interface Emit {
	(e: 'close'): void
}

const emit = defineEmits<Emit>()

const ms = useMessage()
const text = ref('')
const loading = ref(false)
const aiMode = ref(AiMode.LocalAI)
const aiModeOptions = [{
	label: '通用AI',
	value: AiMode.LocalAI,
}]

async function handleIngestText() {
	if (!text.value) {
		ms.warning(t('upload.aiDataRequired'))
		return
	}

	loading.value = true
	// replace all \n with empty
	const textValue = text.value.trim().replace(/\n/g, '')
	await ingestText(textValue)
	ms.success(t('common.success'))
	emit('close')
	loading.value = false
}
</script>

<template>
	<NSpin :show="loading">
		<div class="p-4 space-y-5 min-h-[200px]">
			<div class="space-y-6">
				<div class="p-4 rounded-md bg-neutral-100 dark:bg-neutral-700">
					<p>
						{{ $t('upload.uploadTextTips') }}
					</p>
				</div>
				<div class="flex items-center space-x-4">
					<span class="flex-shrink-0 w-[100px]">{{ $t('upload.aiMode') }}</span>
					<div class="flex-1">
						<NSelect v-model:value="aiMode" :options="aiModeOptions" />
					</div>
				</div>
				<div class="flex items-center space-x-4">
					<span class="flex-shrink-0 w-[100px]">{{ $t('upload.ingestText') }}</span>
					<div class="flex-1">
						<NInput v-model:value="text" type="textarea" maxlength="2000" rows="6" show-count />
					</div>
				</div>
				<div class="flex items-center justify-end space-x-4">
					<NButton size="large" type="success" @click="handleIngestText()">
						{{ $t('upload.uploadIngestText') }}
					</NButton>
				</div>
			</div>
		</div>
	</NSpin>
</template>
