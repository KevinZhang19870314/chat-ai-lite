<script setup lang="ts">
import { computed, ref } from 'vue'
import { useMessage, NInput, NButton, NCheckbox, NSelect, NImage } from 'naive-ui'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { useAppStore, useTextToImageStore, useUserStore } from '@/store'
import { SvgIcon } from '@/components/common'

const appStore = useAppStore()
const userStore = useUserStore()
const textToImageStore = useTextToImageStore()
const ms = useMessage()
const { isMobile } = useBasicLayout()
const collapsed = computed(() => appStore.siderCollapsed)
const imageUrl = computed(() => textToImageStore.imageUrl)
const loading = ref(false)
const query = ref('')
const isGlobal = ref(true)
const examples = ref([
	`在繁华的都市夜景中，闪烁的霓虹灯照亮了街道，行人熙熙攘攘，车辆川流不息。`,
	`一座古老的城堡坐落在悬崖边，背后是波涛汹涌的大海，天空乌云密布，雷电交加。`,
	`一个神秘的森林，阳光透过浓密的树叶洒在地上，空气中弥漫着薄雾，隐约可见一条小径。`,
	`一个未来科技城市，空中有飞行汽车穿梭，高楼大厦充满了科幻感，天空湛蓝，云层稀薄。`,
	`在一片宁静的湖边，夕阳西下，湖面倒映着橙红色的天空，几只天鹅优雅地游弋。`,
	`一个神秘的古文明遗迹，断壁残垣间长满了绿色的藤蔓，考古学家正在仔细研究。`,
	`一群五彩斑斓的热带鱼在清澈见底的海水中游动，海底珊瑚礁色彩斑斓，充满生机。`,
	`一个寒冷的冬日早晨，雪花纷飞，白雪覆盖了整个村庄，烟囱里缓缓升起炊烟。`,
	`一片金色的麦田在微风中轻轻摇曳，远处是一座古老的风车，天空中白云飘飘。`,
	`一处古老神秘的废墟,石头砌成的古老建筑,蔓延的藤蔓和绿植,隐藏着未知的秘密。`,
	`一个充满异域风情的集市，五彩斑斓的摊位，热闹的人群，空气中弥漫着香料的味道。`,
])
const model = ref('dall-e-2')
const modelOptions = [
	{
		label: 'DALL·E 2',
		key: 'dall-e-2',
		value: 'dall-e-2',
	},
	{
		label: 'DALL·E 3',
		key: 'dall-e-3',
		value: 'dall-e-3',
		disabled: userStore.isNormal
	},
]

const payload = computed(() => {
	return {
		query: query.value,
		model: model.value,
		is_global: isGlobal.value,
	}
})


function handleGenRandomQuery() {
	const example = examples.value[Math.floor(Math.random() * examples.value.length)]
	query.value = example
}

async function handleGenerate() {
	loading.value = true

	try {
		await textToImageStore.generateImage(payload.value)
	} catch (error) {
		ms.error(`${error}`)
	}
	finally {
		loading.value = false
	}
}
</script>

<template>
	<div class="max-w-screen-2xl flex flex-col justify-center m-auto overflow-auto"
		:class="[isMobile ? 'p-2' : 'p-4', collapsed ? 'pl-[80px]' : 'p-4']">
		<div class="pb-4 flex gap-2 text-2xl font-extrabold items-center">
			<span>{{ `${$t('common.textToImage')}` }}</span>
			<NButton type="info" round @click="handleGenRandomQuery">
				<template #icon>
					<SvgIcon icon="fe:random" />
				</template>
				{{ $t('common.example') }}
			</NButton>
		</div>
		<div class="flex flex-col gap-4">
			<div class="w-full flex flex-col gap-2">
				<div>{{ $t('textToImages.description') }}</div>
				<NInput v-model:value="query" type="textarea" :placeholder="$t('textToImages.describeImage')" maxlength="200"
					show-count :autosize="{ minRows: 8, maxRows: 18 }" />
			</div>
		</div>
		<div class="flex gap-4">
			<div class="pt-4 flex items-center gap-2">
				<div>{{ $t('admin.model') }}</div>
				<NSelect v-model:value="model" style="width: 220px" :options="modelOptions" />
			</div>
			<div class="pt-4 flex items-center gap-2" v-if="false">
				<NCheckbox v-model:checked="isGlobal">
					<div>{{ $t('textToImages.visibleForEveryone') }}</div>
				</NCheckbox>
			</div>
		</div>
		<div class="pt-4 flex justify-end">
			<NButton :loading="loading" :disabled="!query" size="large" class="!w-[200px]" type="primary" round
				@click="handleGenerate">
				{{ $t('textToImages.generate') }}
			</NButton>
		</div>
		<div class="flex" v-if="imageUrl">
			<NImage width="512" :src="imageUrl" />
		</div>
	</div>
</template>

<style lang="less" scoped></style>
