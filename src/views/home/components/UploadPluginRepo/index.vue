<script setup lang="ts">
import { computed, ref } from 'vue'

import { NButton, NInput, NModal, NSpace, useMessage } from 'naive-ui'

import { useAISquareStore } from '@/store'

interface Props {
  visible: boolean
}

interface Emit {
  (ev: 'update:visible', visible: boolean): void
  (ev: 'successed'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emit>()

const ms = useMessage()
const aiSquareStore = useAISquareStore()
const repoUrl = ref('')

const loading = ref(false)

const showModal = computed({
  get() {
    return props.visible
  },
  set(value) {
    emit('update:visible', value)
  },
})

// validate: must match regex https url
const disabled = computed(() => {
  return !/^https?:\/\/([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/.test(repoUrl.value)
},
)

async function handleUpload() {
  loading.value = true
  try {
    await aiSquareStore.uploadPluginFromGithub(repoUrl.value)
    emit('successed')
  }
  catch (error) {
    ms.error(`${error}`)
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <NModal v-model:show="showModal" :title="$t('localAI.uploadPluginWithRepo')" style="max-width: 640px;" preset="card">
    <NSpace vertical>
      {{ $t('localAI.repoUrl') }}
      <NInput v-model:value="repoUrl" />
      <NButton block type="primary" :disabled="disabled" :loading="loading" @click="handleUpload">
        {{ $t('common.confirm') }}
      </NButton>
    </NSpace>
  </NModal>
</template>
