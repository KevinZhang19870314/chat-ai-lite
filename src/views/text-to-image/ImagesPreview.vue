<script setup lang='ts'>
import { useAppStore, useTextToImageStore } from '@/store';
import { computed, onMounted, ref } from 'vue'
import { NButton, NSpin, useMessage, NPagination, NTooltip, NImage } from 'naive-ui'
import { SvgIcon } from '@/components/common'
import { useBasicLayout } from '@/hooks/useBasicLayout';
import 'gridstack/dist/gridstack.min.css';
import 'gridstack/dist/gridstack-extra.min.css';
import { GridStack } from 'gridstack';
import { useRouter } from 'vue-router';

const appStore = useAppStore()
const router = useRouter()
const ms = useMessage()
const textToImageStore = useTextToImageStore()
const { isMobile } = useBasicLayout()
const collapsed = computed(() => appStore.siderCollapsed)

const loading = ref(false)
const page = ref(1)
const total = ref(1)
const size = ref(100)

const items = computed(() => {
	if (!textToImageStore.records || textToImageStore.records.length === 0) {
		return []
	}

	const records = []
	for (let i = 0; i < textToImageStore.records.length; i++) {
		const record: any = textToImageStore.records[i]
		record.id = i
		record.src = new URL(record.image_url, location.origin).toString()
		const size = Math.floor(Math.random() * 3) + 1
		record.w = size
		record.h = size

		records.push(record)
	}

	return records
})

// const pics = [
// 	{ id: 1, src: 'https://fastly.picsum.photos/id/165/664/653.jpg?hmac=25bZQk0RgPdfcDZ3pjU7Bv-53QVfEGwYORyPICU0IQQ', row: 2, column: 2 },
// 	{ id: 2, src: 'https://fastly.picsum.photos/id/165/664/653.jpg?hmac=25bZQk0RgPdfcDZ3pjU7Bv-53QVfEGwYORyPICU0IQQ', row: 1, column: 2 },
// 	{ id: 3, src: 'https://fastly.picsum.photos/id/165/664/653.jpg?hmac=25bZQk0RgPdfcDZ3pjU7Bv-53QVfEGwYORyPICU0IQQ', row: 2, column: 1 },
// 	{ id: 4, src: 'https://fastly.picsum.photos/id/165/664/653.jpg?hmac=25bZQk0RgPdfcDZ3pjU7Bv-53QVfEGwYORyPICU0IQQ', row: 1, column: 2 },
// 	{ id: 5, src: 'https://fastly.picsum.photos/id/165/664/653.jpg?hmac=25bZQk0RgPdfcDZ3pjU7Bv-53QVfEGwYORyPICU0IQQ', row: 2, column: 2 },
// 	{ id: 6, src: 'https://fastly.picsum.photos/id/165/664/653.jpg?hmac=25bZQk0RgPdfcDZ3pjU7Bv-53QVfEGwYORyPICU0IQQ', row: 1, column: 1 },
// 	{ id: 7, src: 'https://fastly.picsum.photos/id/165/664/653.jpg?hmac=25bZQk0RgPdfcDZ3pjU7Bv-53QVfEGwYORyPICU0IQQ', row: 2, column: 2 },
// 	{ id: 8, src: 'https://fastly.picsum.photos/id/165/664/653.jpg?hmac=25bZQk0RgPdfcDZ3pjU7Bv-53QVfEGwYORyPICU0IQQ', row: 1, column: 2 },
// 	{ id: 9, src: 'https://fastly.picsum.photos/id/165/664/653.jpg?hmac=25bZQk0RgPdfcDZ3pjU7Bv-53QVfEGwYORyPICU0IQQ', row: 2, column: 1 },
// 	{ id: 10, src: 'https://fastly.picsum.photos/id/165/664/653.jpg?hmac=25bZQk0RgPdfcDZ3pjU7Bv-53QVfEGwYORyPICU0IQQ', row: 1, column: 2 },
// 	{ id: 11, src: 'https://fastly.picsum.photos/id/165/664/653.jpg?hmac=25bZQk0RgPdfcDZ3pjU7Bv-53QVfEGwYORyPICU0IQQ', row: 2, column: 2 },
// 	{ id: 12, src: 'https://fastly.picsum.photos/id/165/664/653.jpg?hmac=25bZQk0RgPdfcDZ3pjU7Bv-53QVfEGwYORyPICU0IQQ', row: 1, column: 1 }
// ]

async function refresh() {
	try {
		loading.value = true
		total.value = await textToImageStore.fetchTextToImageListByPage(size.value, page.value)
	} catch (error) {
		ms.error(`${error}`)
	} finally {
		loading.value = false
	}
}

function handlePageChange(p: number) {
	page.value = p
	refresh()
}

function handleRefresh() {
	refresh()

	// reload page
	router.replace({ path: '/text-to-image/images-preview', query: { t: new Date().getTime() } })
}

onMounted(async () => {
	await refresh()

	GridStack.init({ column: 8 })
})
</script>

<template>
	<div class="max-w-screen-2xl flex flex-col justify-center m-auto overflow-auto"
		:class="[isMobile ? 'p-2' : 'p-4', collapsed ? 'pl-[80px]' : 'p-4']">
		<div class="pb-4 flex text-2xl items-center justify-between">
			<div class="flex gap-2 font-extrabold ">
				<span>{{ `${$t('textToImages.genRecords')}` }}</span>
				<NTooltip trigger="hover" class="max-w-xs">
					<template #trigger>
						<NButton type="primary" circle tertiary @click="handleRefresh">
							<SvgIcon icon="tabler:refresh-dot" class="text-lg" />
						</NButton>
					</template>
					{{ $t('common.refresh') }}
				</NTooltip>
			</div>
			<NPagination v-model:page="page" :item-count="total" :page-sizes="[size]" size="large"
				@update-page="handlePageChange" />
		</div>
		<NSpin :show="loading">
			<div class="grid-stack">
				<div class="grid-stack-item" :gs-w="item.w" :gs-h="item.h" v-for="item in items" :key="item.id">
					<div class="grid-stack-item-content !overflow-hidden">
						<NTooltip trigger="hover">
							<template #trigger>
								<NImage class="h-full w-full" :src="item.src" :img-props="{ style: 'width: 100%; height: 100%;' }" />
							</template>
							{{ item.query }}
						</NTooltip>
					</div>
				</div>
			</div>
		</NSpin>
	</div>
</template>

<style lang="less" scoped>
.masonry {
	column-count: 4;
	column-gap: 1rem;
}

.masonry-item {
	break-inside: avoid;
	margin-bottom: 1rem;
}

.col-span-2 {
	grid-column: span 2;
}

.row-span-2 {
	grid-row: span 2;
}
</style>
