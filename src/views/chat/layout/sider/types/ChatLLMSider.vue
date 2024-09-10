<script setup lang='ts'>
import { useMessage } from 'naive-ui'
import { ref } from 'vue'
import List from '../List.vue'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { useAppStore, useChatStore } from '@/store'
import { generateSessionId } from '@/utils/functions'
import { AiMode } from '@/models/chat.model'
import { t } from '@/locales'
import SiderToolBar from '@/views/chat/components/SiderToolBar/index.vue'

const appStore = useAppStore()
const chatStore = useChatStore()
const ms = useMessage()

const searchValue = ref('')
const { isMobile } = useBasicLayout()

async function handleAdd() {
  chatStore.setSiderLoading(true)
  try {
    await chatStore.addHistory({
      title: t('chat.newChat'),
      icon: 'ri:message-3-line',
      ai_mode: AiMode.ChatLLM,
      uuid: generateSessionId(),
      isEdit: false,
    })
    if (isMobile.value)
      appStore.setSiderCollapsed(true)

    await chatStore.fetchHistory()
  }
  catch (error) {
    ms.error(`${error}`)
  }
  finally {
    chatStore.setSiderLoading(false)
  }
}
</script>

<template>
  <div class="flex flex-col w-[240px]">
    <SiderToolBar
      v-model:search="searchValue"
      :add-button-tips="$t('chat.newChatButton')"
      @add="handleAdd"
    />
    <div class="flex-1 min-h-0 pb-4 pl-0 overflow-hidden">
      <List :ai-mode="AiMode.ChatLLM" :search="searchValue" />
    </div>
  </div>
</template>
