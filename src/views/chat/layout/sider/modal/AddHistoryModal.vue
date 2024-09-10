<script setup lang="ts">
import type { VNodeChild } from 'vue'
import { computed, h, ref, watch } from 'vue'

import type { SelectOption } from 'naive-ui'
import { NButton, NInput, NModal, NSelect, NSpace, NSpin, useMessage } from 'naive-ui'

import { ICONS } from './icons'
import SvgIcon from '@/components/common/SvgIcon/index.vue'
import { addChatHistoryMeta } from '@/api'
import { t } from '@/locales'
import { generateSessionId } from '@/utils/functions'
import { useChatStore } from '@/store'
import type { ChatHistoryMeta, UpdateChatHistoryMeta } from '@/models/chat.model'
import { AiMode } from '@/models/chat.model'

interface Props {
  show: boolean
  mode: 'add' | 'modify'
}

interface Emit {
  (ev: 'update:show', show: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emit>()

const ms = useMessage()
const chatStore = useChatStore()
const activeHistory = computed(() => chatStore.getChatHistoryByCurrentActive)

const loading = ref(false)

const options: Array<SelectOption> = []
ICONS.forEach((icon: string) => {
  options.push({
    value: `${icon}`,
    label: '',
  })
})

function renderLabel(option: SelectOption): VNodeChild {
  return [
    h(
      SvgIcon,
      {
        icon: `${option.value}`,
        class: 'text-xl',
      },
      {
        default: () => h('请选择'),
      },
    ),
  ]
}

const showModal = computed({
  get() {
    return props.show
  },
  set(value) {
    emit('update:show', value)
  },
})

const defaultIcon = 'fluent-emoji-flat:1st-place-medal'
let history = ref<ChatHistoryMeta>({
  id: '',
  isEdit: false,
  user_id: '',
  icon: defaultIcon,
  title: '',
  description: '',
  greetings: '',
  uuid: 0,
  ai_mode: AiMode.MyFavorites,
  knowledge_base_id: '',
})

watch(
  () => activeHistory,
  () => {
    if (props.mode === 'modify') {
      if (activeHistory.value) {
        history = ref<ChatHistoryMeta>({
          id: `${activeHistory.value!.id}`,
          isEdit: false,
          user_id: `${activeHistory.value!.user_id}`,
          icon: `${activeHistory.value!.icon}`,
          title: `${activeHistory.value!.title}`,
          description: `${activeHistory.value!.description}`,
          greetings: `${activeHistory.value!.greetings}`,
          uuid: +activeHistory.value!.uuid,
          ai_mode: AiMode.MyFavorites,
          knowledge_base_id: `${activeHistory.value!.knowledge_base_id}`,
        })
      }
      else {
        history = ref<ChatHistoryMeta>({
          id: '',
          isEdit: false,
          user_id: '',
          icon: defaultIcon,
          title: '',
          description: '',
          greetings: '',
          uuid: 0,
          ai_mode: AiMode.MyFavorites,
          knowledge_base_id: '',
        })
      }
    }
  },
  { deep: true },
)

const disabled = computed (() => {
  if (chatStore.aiMode === AiMode.MyFavorites) {
    return history.value.icon!.trim().length < 1
      || history.value.title.trim().length < 1
      || history.value.description!.trim().length < 1
      || history.value.greetings!.trim().length < 1
  }
  else {
    return history.value.title.trim().length < 1
  }
},
)

async function add() {
  loading.value = true
  try {
    history.value.uuid = generateSessionId()
    const res = await addChatHistoryMeta<ChatHistoryMeta>(history.value)
    if (res.status === 'Error')
      throw new Error(`${res.message}`)
    await chatStore.fetchHistory()
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
    const payload: UpdateChatHistoryMeta = {
      id: `${history.value!.id}`,
      fields: { icon: history.value.icon, title: history.value.title, description: history.value.description, greetings: history.value.greetings || 'Hi' },
    }
    await chatStore.updateChatHistoryMeta(payload)
    chatStore.fetchHistory()
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
  history.value.id = ''
  history.value.user_id = ''
  history.value.icon = defaultIcon
  history.value.title = ''
  history.value.description = ''
  history.value.greetings = ''
}
</script>

<template>
  <NModal v-model:show="showModal" :title="$t('chat.newRoleButton')" style="max-width: 900px;" preset="card">
    <NSpin :show="loading">
      <NSpace vertical>
        <template v-if="chatStore.aiMode === AiMode.MyFavorites">
          {{ $t('store.roleIcon') }}
          <NSelect v-model:value="history.icon" :options="options" :render-label="renderLabel" style="width: 50%;" />
        </template>
        {{ chatStore.aiMode === AiMode.MyFavorites ? $t('store.roleTitle') : $t('store.title') }}
        <NInput v-model:value="history.title" />
        <template v-if="chatStore.aiMode === AiMode.MyFavorites">
          {{ $t('store.roleDescription') }}
          <NInput v-model:value="history.description" type="textarea" />
          {{ $t('store.greetings') }}
          <NInput v-model:value="history.greetings" type="textarea" />
        </template>
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
