<script setup lang='ts'>
import { computed, h, onMounted, reactive, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NButton, NDataTable, useDialog, useMessage } from 'naive-ui'

import { t } from '@/locales'
import { SvgIcon } from '@/components/common'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { useAISquareStore } from '@/store'
import { AiMode } from '@/models/chat.model'

interface Props {
	canDelete: boolean
	aiMode?: AiMode
}
interface DataProps {
	renderFilename?: string
	filename?: string
	file_id?: string
}

const props = defineProps<Props>()

const { isMobile } = useBasicLayout()
const aiSquareStore = useAISquareStore()
const ms = useMessage()
const dialog = useDialog()
const list = computed(() => aiSquareStore.vectorDocRecordList)
const searchValue = ref<string>('')
const loading = ref(false)
const currentKnowledgeBase = computed(() => aiSquareStore.currentKnowledgeBase)

function deleteDocument(row: DataProps) {
	const d = dialog.warning({
		title: t('chat.deleteFile'),
		content: t('chat.deleteFileConfirm'),
		positiveText: t('common.yes'),
		negativeText: t('common.no'),
		onPositiveClick: async () => {
			d.loading = true
			try {
				if (!props.aiMode || props.aiMode === AiMode.LocalAI)
					await aiSquareStore.removeVectorDocRecordByFilename(row.filename!, `${currentKnowledgeBase.value?.id}`, props.aiMode ?? AiMode.LocalAI)

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
function createColumns(): DataTableColumns<DataProps> {
	return [
		{
			title: t('chat.uploadedFilename'),
			key: 'renderFilename',
			render(row) {
				const fileExtension = row.filename!.split('.').pop()?.toLowerCase() // 获取文件扩展名

				let icon = ''
				let iconClass = ''
				if (fileExtension === 'pdf') {
					icon = 'bi:file-pdf'
					iconClass = 'text-red-500'
				}
				else if (fileExtension === 'md' || fileExtension === 'markdown') {
					icon = 'bi:filetype-md'
					iconClass = 'text-sky-500'
				}
				else if (fileExtension === 'txt') {
					icon = 'icon-park-outline:file-txt'
					iconClass = 'text-amber-500'
				}
				else { icon = 'mdi:file' }

				return h('div', { class: 'flex items-center flex-row gap-2' }, [
					h(SvgIcon, { icon, class: `text-2xl ${iconClass}` }), // 正确传递 SvgIcon 的属性
					h('span', { class: 'text-sm' }, row.renderFilename),
				])
			},
		},
		{
			title: t('common.action'),
			key: 'actions',
			width: 100,
			align: 'center',
			render(row) {
				return h('div', { class: 'flex items-center flex-col gap-2' }, {
					default: () => [
						props.canDelete && h(
							NButton,
							{
								tertiary: true,
								size: 'small',
								type: 'error',
								onClick: () => deleteDocument(row),
							},
							{ default: () => t('common.delete') },
						),
					],
				})
			},
		},
	]
}

const columns = createColumns()
const pagination = reactive({
	page: 1,
	itemCount: 1,
	pageSize: 5,
})
function renderTemplate() {
	const limit = isMobile.value ? 10 : 50

	return list.value.map((item: any) => {
		if (!item.filename) {
			return {
				renderFilename: item.length <= limit ? item : `${item.substring(0, limit)}...`,
				filename: item,
			}
		}
		else {
			return {
				renderFilename: item.filename.length <= limit ? item.filename : `${item.filename.substring(0, limit)}...`,
				filename: item.filename,
				file_id: item.id,
			}
		}
	})
}

const dataSource = computed(() => {
	const data = renderTemplate()
	const value = searchValue.value
	if (value && value !== '') {
		return data.filter((item: DataProps) => {
			return item.renderFilename!.includes(value)
		})
	}
	return data
})

async function refresh() {
	loading.value = true
	try {
		if (!props.aiMode || props.aiMode === AiMode.LocalAI) {
			const total = await aiSquareStore.fetchVectorDocRecordListByPage(pagination.pageSize, pagination.page, `${currentKnowledgeBase.value?.id}`)
			pagination.itemCount = +total
		}
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

onMounted(() => {
	refresh()
})

defineExpose({
	refresh,
})
</script>

<template>
	<div class="min-h-[100px] p-2">
		<NDataTable remote :loading="loading" :max-height="550" :columns="columns" :data="dataSource" :pagination="pagination"
			@update:page="handlePageChange" />
	</div>
</template>
