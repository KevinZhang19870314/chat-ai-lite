<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { NButton, NDivider, NInput, NModal, NSelect, NSpace, NSpin, useMessage } from 'naive-ui'

import { t } from '@/locales'
import type { Prompt, UpdatePrompt } from '@/models/chat.model'
import { AIAssistantCategories } from '@/utils/constants'
import { usePromptStore } from '@/store'

interface Props {
  show: boolean
  mode: 'add' | 'modify'
  data?: Prompt
}

interface Emit {
  (ev: 'update:show', show: boolean): void
  (ev: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emit>()

const promptStore = usePromptStore()
const ms = useMessage()
const categoryOptions: { label: string, key: string, value: string }[] = AIAssistantCategories
  .filter(f => f.category !== 'all' && f.category !== 'likes')
  .map(item => ({
    label: t(item.titleI18n),
    key: item.category,
    value: item.category,
  }))

const loading = ref(false)

const showModal = computed({
  get() {
    return props.show
  },
  set(value) {
    emit('update:show', value)
  },
})

const defaultIcon = 'fluent-emoji-flat:1st-place-medal'
const aiAssistant = ref<Prompt>({
  id: '',
  title: '',
  description: '',
  icon: defaultIcon,
  greetings: '',
  category: '',
  likes: 0,
  is_enabled: true,
})

const disabled = computed (() => {
  return aiAssistant.value.icon!.trim().length < 1
    || aiAssistant.value.title.trim().length < 1
    || aiAssistant.value.description!.trim().length < 1
    || aiAssistant.value.greetings!.trim().length < 1
    || aiAssistant.value.category!.trim().length < 1
},
)

async function add() {
  loading.value = true
  try {
    const payload: Prompt = {
      title: aiAssistant.value.title,
      description: aiAssistant.value.description,
      icon: aiAssistant.value.icon,
      greetings: aiAssistant.value.greetings,
      category: aiAssistant.value.category,
      likes: 0,
    }
    await promptStore.createPrompt(payload)

    emit('success')
    ms.success(`${t('common.addSuccess')}`)
    showModal.value = false
    reset()
  }
  catch (error: any) {
    ms.error(`${error}`)
  }
  finally {
    loading.value = false
  }
}

async function modify() {
  loading.value = true
  try {
    const payload: UpdatePrompt = {
      id: aiAssistant.value.id!,
      fields: {
        icon: aiAssistant.value.icon,
        title: aiAssistant.value.title,
        description: aiAssistant.value.description,
        greetings: aiAssistant.value.greetings,
        category: aiAssistant.value.category,
      },
    }

    await promptStore.updatePrompt(payload)

    emit('success')
    ms.success(`${t('common.editSuccess')}`)
    showModal.value = false
    reset()
  }
  catch (error) {
    ms.error(`${error}`)
  }
  finally {
    loading.value = false
  }
}

function reset() {
  aiAssistant.value.id = ''
  aiAssistant.value.title = ''
  aiAssistant.value.description = ''
  aiAssistant.value.icon = defaultIcon
  aiAssistant.value.greetings = ''
  aiAssistant.value.category = ''
  aiAssistant.value.likes = 0
  aiAssistant.value.is_enabled = true
}

onMounted(() => {
  if (props.mode === 'modify') {
    aiAssistant.value = { ...props.data! }
  }
  else {
    aiAssistant.value = {
      id: '',
      title: '',
      description: '',
      icon: defaultIcon,
      greetings: '',
      category: '',
      likes: 0,
      is_enabled: true,
    }
  }
})
</script>

<template>
  <NModal v-model:show="showModal" :title="mode === 'add' ? $t('admin.newAIAssistant') : $t('admin.editAIAssistant')" style="max-width: 900px;" preset="card">
    <NSpin :show="loading">
      <NSpace vertical>
        {{ $t('store.icon') + $t('admin.iconTips') }}
        <NInput v-model:value="aiAssistant.icon" />
        {{ $t('store.title') }}
        <NInput v-model:value="aiAssistant.title" />
        {{ $t('store.description') }}
        <NInput v-model:value="aiAssistant.description" type="textarea" />
        {{ $t('store.greetings') }}
        <NInput v-model:value="aiAssistant.greetings" type="textarea" />
        {{ $t('store.category') }}
        <NSelect v-model:value="aiAssistant.category" :options="categoryOptions" />
        <NDivider />
        <NButton
          block
          type="primary"
          :disabled="disabled"
          @click="() => { props.mode === 'add' ? add() : modify() }"
        >
          {{ $t('common.confirm') }}
        </NButton>
      </NSpace>
    </NSpin>
  </NModal>
</template>
