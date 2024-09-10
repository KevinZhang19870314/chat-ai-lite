import { computed } from 'vue'
import type { AxiosProgressEvent } from 'axios'
import type { LocalAIMessage } from '../../../models/chat.model'
import { LocalAIRole } from '../../../models/chat.model'
import { useChat } from './useChat'
import { loading } from './common/useLoading'
import { abortController } from './common/useAbortController'
import { t } from '@/locales'
import { useChatStore } from '@/store'
import { asyncAskBot } from '@/api'
import type { LocalAIRequest } from '@/models/chat.model'
import { ChatRole } from '@/models/chat.model'

export function useLocalAI() {
  const chatStore = useChatStore()
  const { addChat, updateChat, updateChatSome } = useChat()

  async function chat(uuid: number, scrollToBottom: Function, scrollToBottomIfAtBottom: Function) {
    const message = chatStore.prompt
    const knowledge_base_id = chatStore.getChatHistoryByCurrentActive!.knowledge_base_id!

    if (loading.value)
      return

    if (!message || message.trim() === '')
      return

    abortController.value = new AbortController()

    addChat(
      +uuid,
      {
        dateTime: new Date().toLocaleString(),
        text: message,
        role: ChatRole.USER,
        error: false,
        conversationOptions: null,
        requestOptions: { prompt: message, options: null },
      },
    )
    scrollToBottom()

    addChat(
      +uuid,
      {
        dateTime: new Date().toLocaleString(),
        text: '',
        loading: true,
        role: ChatRole.ASSISTANT,
        error: false,
        conversationOptions: null,
        requestOptions: { prompt: message, options: { } },
      },
    )
    scrollToBottom()

    loading.value = true
    chatStore.setPrompt('')

    const dataSources = computed(() => chatStore.getChatByUuid(+uuid))
    try {
      await asyncAskBot<any>(buildLocalAIRequest(uuid, knowledge_base_id, message), (progressEvent: AxiosProgressEvent) => {
        const data = progressEvent.event.target.response
        updateChat(
          +uuid,
          dataSources.value.length - 1,
          {
            dateTime: new Date().toLocaleString(),
            text: data,
            role: ChatRole.ASSISTANT,
            error: false,
            loading: true,
            conversationOptions: { },
            requestOptions: { prompt: message, options: null },
          },
        )

        scrollToBottomIfAtBottom()
      }, abortController.value.signal)

      updateChatSome(+uuid, dataSources.value.length - 1, { loading: false })
    }
    catch (error: any) {
      const errorMessage = error?.message ?? t('common.wrong')
      if (error.message === 'canceled') {
        updateChatSome(
          +uuid,
          dataSources.value.length - 1,
          {
            loading: false,
          },
        )
        scrollToBottomIfAtBottom()
        return
      }

      updateChat(
        +uuid,
        dataSources.value.length - 1,
        {
          dateTime: new Date().toLocaleString(),
          text: errorMessage,
          role: ChatRole.ASSISTANT,
          error: true,
          loading: false,
          conversationOptions: null,
          requestOptions: { prompt: message, options: null },
        },
      )
      scrollToBottomIfAtBottom()
    }
    finally {
      loading.value = false
    }
  }

  async function regenChat(index: number, uuid: number) {
    if (loading.value)
      return

    abortController.value = new AbortController()

    const dataSources = computed(() => chatStore.getChatByUuid(+uuid))
    const { requestOptions } = dataSources.value[index]
    const message = requestOptions?.prompt ?? ''
    loading.value = true
    const knowledge_base_id = chatStore.getChatHistoryByCurrentActive!.knowledge_base_id!

    updateChat(
      +uuid,
      index,
      {
        dateTime: new Date().toLocaleString(),
        text: '',
        role: ChatRole.ASSISTANT,
        error: false,
        loading: true,
        conversationOptions: null,
        requestOptions: { prompt: message, options: { } },
      },
    )

    try {
      await asyncAskBot<any>(buildLocalAIRequest(uuid, knowledge_base_id, message), (progressEvent: AxiosProgressEvent) => {
        const data = progressEvent.event.target.response
        updateChat(
          +uuid,
          index,
          {
            dateTime: new Date().toLocaleString(),
            text: data,
            role: ChatRole.ASSISTANT,
            error: false,
            loading: true,
            conversationOptions: { },
            requestOptions: { prompt: message, options: { } },
          },
        )
      }, abortController.value.signal)

      updateChatSome(+uuid, index, { loading: false })
    }
    catch (error: any) {
      const errorMessage = error?.message ?? t('common.wrong')
      if (error.message === 'canceled') {
        updateChatSome(
          +uuid,
          dataSources.value.length - 1,
          {
            loading: false,
          },
        )
        return
      }

      updateChat(
        +uuid,
        index,
        {
          dateTime: new Date().toLocaleString(),
          text: errorMessage,
          role: ChatRole.ASSISTANT,
          error: true,
          loading: false,
          conversationOptions: null,
          requestOptions: { prompt: message, options: { } },
        },
      )
    }
    finally {
      loading.value = false
    }
  }

  function buildLocalAIRequest(uuid: number, knowledge_base_id: string, message: string): LocalAIRequest {
    const messages = chatStore.getMessagesByUuid(+uuid, 8)
    // remove the last item: because we need the chat_history, so we don't need the current Human message
    messages.pop()
    // to chat history
    const chat_history: LocalAIMessage[] = []
    messages.forEach((message) => {
      chat_history.push({
        who: message.role === ChatRole.ASSISTANT ? LocalAIRole.AI : LocalAIRole.HUMAN,
        message: message.content,
      })
    })
    const request: LocalAIRequest = {
      text: message,
      knowledge_base_id,
      chat_history,
    }

    return request
  }

  return {
    loading,
    chat,
    regenChat,
  }
}
