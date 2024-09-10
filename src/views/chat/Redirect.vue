<script lang="ts" setup>
import { onBeforeUnmount, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const state = reactive({
	data: null,
	loading: false,
})

let timerId: any = null

async function fetchData() {
	state.loading = true
	try {
		router.replace({ name: 'Root' })
	}
	catch (error) {
		timerId = setTimeout(fetchData, 5000)
	}
	finally {
		state.loading = false
	}
}

function cancelFetchData() {
	clearTimeout(timerId)
}

onBeforeUnmount(() => {
	cancelFetchData()
})

onMounted(async () => {
	fetchData()
})
</script>

<template>
	<div class="flex h-full" />
</template>
