import { computed } from 'vue'
import type { AxiosProgressEvent } from 'axios'
import { useChat } from './useChat'
import { loading } from './common/useLoading'
import { abortController } from './common/useAbortController'
import { t } from '@/locales'
import { useChatStore } from '@/store'
import { asyncChatWithRole } from '@/api'
import type { ChatRequest } from '@/models/chat.model'
import { ChatRole } from '@/models/chat.model'

export function useChatWithRole() {
  const chatStore = useChatStore()
  const { addChat, updateChat, updateChatSome } = useChat()

  async function chat(uuid: number, scrollToBottom: Function, scrollToBottomIfAtBottom: Function, greetings = '') {
    if (greetings) {
      addChat(
        +uuid,
        {
          dateTime: new Date().toLocaleString(),
          text: greetings,
          role: ChatRole.ASSISTANT,
          error: false,
          conversationOptions: null,
          requestOptions: { prompt: greetings, options: null },
        },
      )
      scrollToBottom()

      return
    }

    const message = chatStore.prompt
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
        requestOptions: { prompt: message, options: {} },
      },
    )
    scrollToBottom()

    loading.value = true
    chatStore.setPrompt('')

    const dataSources = computed(() => chatStore.getChatByUuid(+uuid))
    try {
      await asyncChatWithRole<any>(message, (progressEvent: AxiosProgressEvent) => {
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
            conversationOptions: {},
            requestOptions: { prompt: message, options: null },
          },
        )

        scrollToBottomIfAtBottom()
      }, buildChatRequest(uuid), abortController.value.signal)

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
        requestOptions: { prompt: message, options: {} },
      },
    )

    try {
      await asyncChatWithRole<any>(message, (progressEvent: AxiosProgressEvent) => {
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
            conversationOptions: {},
            requestOptions: { prompt: message, options: {} },
          },
        )
      }, buildChatRequest(uuid), abortController.value.signal)

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
          requestOptions: { prompt: message, options: {} },
        },
      )
    }
    finally {
      loading.value = false
    }
  }

  function buildChatRequest(uuid: number): ChatRequest {
    const messages = chatStore.getMessagesByUuid(+uuid, 8)
    const chatRequest: ChatRequest = {
      model: chatStore.selectedModel,
      messages,
      max_tokens: 2048,
      temperature: 1,
      uuid,
    }

    return chatRequest
  }

  return {
    loading,
    chat,
    regenChat,
  }
}
