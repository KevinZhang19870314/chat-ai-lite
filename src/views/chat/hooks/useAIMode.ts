import { computed } from 'vue'
import { useChatStore } from '@/store'
import type { AiMode } from '@/models/chat.model'

export function useAIMode() {
  const chatStore = useChatStore()
  const aiMode = computed<AiMode>(() => chatStore.aiMode)

  function setAIMode(mode: AiMode) {
    chatStore.setAIMode(mode)
  }

  return {
    aiMode,
    setAIMode,
  }
}
