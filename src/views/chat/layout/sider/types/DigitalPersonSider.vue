<script setup lang='ts'>
import { ref } from 'vue'
import List from '../List.vue'
import { AiMode } from '@/models/chat.model'
import SiderToolBar from '@/views/chat/components/SiderToolBar/index.vue'

const searchValue = ref('')
</script>

<template>
	<div class="flex flex-col w-[240px]">
		<SiderToolBar v-model:search="searchValue" />
		<div class="flex-1 min-h-0 pb-4 pl-0 overflow-hidden">
			<List :ai-mode="AiMode.DigitalPerson" :search="searchValue" />
		</div>
	</div>
</template>
