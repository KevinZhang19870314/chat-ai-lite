import { defineStore } from 'pinia'
import { fetchChatHistoryMetasWithAiModes, getLocalState, setLocalState } from './helper'
import { router } from '@/router'
import { addChatHistoryMeta, deleteChatHistoryMeta, deleteChatHistoryMetaByTitle, updateChatHistoryMeta } from '@/api'
import { generateSessionId } from '@/utils/functions'
import type { Chat, ChatHistoryMeta, ChatMessage, ChatRole, ChatState, UpdateChatHistoryMeta } from '@/models/chat.model'
import { AiMode } from '@/models/chat.model'

export const useChatStore = defineStore('chat-store', {
	state: (): ChatState => {
		const localState = getLocalState()
		return {
			active: localState.active,
			history: localState.history,
			chat: localState.chat,
			siderLoading: false,
			prompt: '',
			aiMode: localState.aiMode,
			selectedModel: '',
		}
	},

	getters: {
		getChatHistoryByCurrentActive(state: ChatState) {
			if (state.aiMode === AiMode.MyFavorites || state.aiMode === AiMode.DigitalPerson) {
				const index = state.history.findIndex(item => item.uuid === state.active)
				if (index !== -1)
					return state.history[index]
			}
			else {
				const index = state.history.findIndex(item => item.uuid === state.active)
				if (index !== -1)
					return state.history[index]
			}

			return null
		},
		getChatHistoryMetaByTitle(state: ChatState) {
			return (title: string) => {
				return state.history.find(item => item.title === title)
			}
		},

		getChatByUuid(state: ChatState) {
			return (uuid?: number) => {
				if (uuid)
					return state.chat.find(item => item.uuid === uuid)?.data ?? []
				return state.chat.find(item => item.uuid === state.active)?.data ?? []
			}
		},
		getMessagesByUuid(state: ChatState) {
			// retrieve top k messages, if topK is -1, retrieve all
			return (uuid?: number, topK = -1) => {
				let chats = []
				if (uuid)
					chats = state.chat.find(item => item.uuid === uuid)?.data ?? []
				else
					chats = state.chat.find(item => item.uuid === state.active)?.data ?? []

				const messages: ChatMessage[] = []
				for (const chat of chats) {
					if (chat.text) {
						messages.push({
							role: chat.role as ChatRole,
							content: chat.text,
						})
					}
				}

				if (topK === -1)
					return messages
				else
					return messages.slice(-topK)
			}
		},
		getChatHistoryMetas(state: ChatState) {
			return (aiMode: AiMode) => {
				let params = [aiMode]
				if (aiMode === AiMode.KnowledgeBase)
					params = [AiMode.LocalAI]

				const data = state.history.filter(item => params.includes(item.ai_mode!))
				return data ?? []
			}
		},
	},

	actions: {
		setAIMode(aiMode: AiMode) {
			this.aiMode = aiMode
			this.recordState()
		},
		setSiderLoading(context: boolean) {
			this.siderLoading = context
		},
		setPrompt(context: string) {
			this.prompt = context
		},
		async fetchHistory() {
			try {
				const chatHistoryMeta = await fetchChatHistoryMetasWithAiModes(this.aiMode)
				const data: ChatHistoryMeta[] = []
				chatHistoryMeta.forEach((item: ChatHistoryMeta) => {
					data.push({
						uuid: item.uuid,
						isEdit: false,
						title: item.title,
						icon: item.icon,
						description: item.description,
						id: item.id,
						user_id: item.user_id,
						greetings: item.greetings,
						ai_mode: item.ai_mode,
						knowledge_base_id: item.knowledge_base_id,
						assistant_id: item.assistant_id,
						thread_id: item.thread_id,
						meta: item.meta,
					})

					const index = this.chat.findIndex((f: any) => f.uuid === item.uuid)
					if (index === -1)
						this.chat.unshift({ uuid: item.uuid, data: [] })
				})

				this.history = data
				this.recordState()

				return Promise.resolve(this.history)
			}
			catch (error) {
				return Promise.reject(error)
			}
		},

		async addHistory(history: ChatHistoryMeta, chatData: Chat[] = []) {
			const res = await addChatHistoryMeta<ChatHistoryMeta>(history)
			if (res.status === 'Error')
				throw new Error(`${res.message}`)
			this.chat.unshift({ uuid: history.uuid, data: chatData })
			this.active = history.uuid
			this.reloadRoute(history.uuid)
		},

		updateHistory(uuid: number, edit: Partial<ChatHistoryMeta>) {
			const index = this.history.findIndex(item => item.uuid === uuid)
			if (index !== -1) {
				this.history[index] = { ...this.history[index], ...edit }
				this.recordState()
			}
		},

		updateUserPromptHistory(uuid: number, edit: Partial<ChatHistoryMeta>) {
			const index = this.history.findIndex(item => item.uuid === uuid)
			if (index !== -1) {
				this.history[index] = { ...this.history[index], ...edit }
				this.recordState()
			}
		},

		async updateChatHistoryMeta(payload: UpdateChatHistoryMeta) {
			const res = await updateChatHistoryMeta<ChatHistoryMeta>(payload)
			if (res.status === 'Error')
				throw new Error(`${res.message}`)
			this.updateUserPromptHistory(res.data.uuid, res.data)
		},

		async deleteHistory(index: number) {
			this.history.splice(index, 1)
			this.chat.splice(index, 1)

			if (this.history.length === 0) {
				this.active = null
				this.reloadRoute()
				return
			}

			if (index > 0 && index <= this.history.length) {
				const uuid = this.history[index - 1].uuid
				this.active = uuid
				this.reloadRoute(uuid)
				return
			}

			if (index === 0) {
				if (this.history.length > 0) {
					const uuid = this.history[0].uuid
					this.active = uuid
					this.reloadRoute(uuid)
				}
			}

			if (index > this.history.length) {
				const uuid = this.history[this.history.length - 1].uuid
				this.active = uuid
				this.reloadRoute(uuid)
			}
		},

		async deleteChatHistoryMeta(item: { id?: string, title?: string, uuid?: number }) {
			let res: any = {}
			if (item.id)
				res = await deleteChatHistoryMeta(item.id!)
			else if (item.title)
				res = await deleteChatHistoryMetaByTitle(item.title!)

			if (res.status === 'Error')
				throw new Error(`${res.message}`)

			let chatHistoryMeta
			if (!item.id && item.title)
				chatHistoryMeta = this.getChatHistoryMetaByTitle(item.title!)
			if (item.uuid)
				this.clearChatByUuid(item.uuid)
			else if (chatHistoryMeta)
				this.clearChatByUuid(chatHistoryMeta.uuid)
		},

		async setActive(uuid: number) {
			this.active = uuid
			if (this.active)
				await this.reloadRoute(uuid)
		},

		getChatByUuidAndIndex(uuid: number, index: number) {
			if (!uuid || uuid === 0) {
				if (this.chat.length)
					return this.chat[0].data[index]
				return null
			}
			const chatIndex = this.chat.findIndex(item => item.uuid === uuid)
			if (chatIndex !== -1)
				return this.chat[chatIndex].data[index]
			return null
		},

		addChatByUuid(uuid: number, chat: Chat) {
			if (!uuid || uuid === 0) {
				if (this.history.length === 0) {
					const uuid = generateSessionId()
					this.history.push({ uuid, title: chat.text, isEdit: false })
					this.chat.push({ uuid, data: [chat] })
					this.active = uuid
					this.recordState()
					this.reloadRoute(uuid)
				}
				else {
					this.chat[0].data.push(chat)
					if (this.history[0].title === 'New Chat')
						this.history[0].title = chat.text
					this.recordState()
				}
			}

			const index = this.chat.findIndex(item => item.uuid === uuid)
			if (index !== -1) {
				this.chat[index].data.push(chat)
				if (this.aiMode !== AiMode.MyFavorites && this.history[index] && this.history[index].title === 'New Chat')
					this.history[index].title = chat.text
				this.recordState()
			}
		},

		updateChatByUuid(uuid: number, index: number, chat: Chat) {
			if (!uuid || uuid === 0) {
				if (this.chat.length) {
					this.chat[0].data[index] = chat
					this.recordState()
				}
				return
			}

			const chatIndex = this.chat.findIndex(item => item.uuid === uuid)
			if (chatIndex !== -1) {
				this.chat[chatIndex].data[index] = chat
				this.recordState()
			}
		},

		updateChatSomeByUuid(uuid: number, index: number, chat: Partial<Chat>) {
			if (!uuid || uuid === 0) {
				if (this.chat.length) {
					this.chat[0].data[index] = { ...this.chat[0].data[index], ...chat }
					this.recordState()
				}
				return
			}

			const chatIndex = this.chat.findIndex(item => item.uuid === uuid)
			if (chatIndex !== -1) {
				this.chat[chatIndex].data[index] = { ...this.chat[chatIndex].data[index], ...chat }
				this.recordState()
			}
		},

		deleteChatByUuid(uuid: number, index: number) {
			if (!uuid || uuid === 0) {
				if (this.chat.length) {
					this.chat[0].data.splice(index, 1)
					this.recordState()
				}
				return
			}

			const chatIndex = this.chat.findIndex(item => item.uuid === uuid)
			if (chatIndex !== -1) {
				this.chat[chatIndex].data.splice(index, 1)
				this.recordState()
			}
		},

		clearChatByUuid(uuid: number) {
			if (!uuid || uuid === 0) {
				if (this.chat.length) {
					this.chat[0].data = []
					this.recordState()
				}
				return
			}

			const index = this.chat.findIndex(item => item.uuid === uuid)
			if (index !== -1) {
				this.chat[index].data = []
				// this.chat.splice(index, 1)
				this.recordState()
			}
		},

		async reloadRoute(uuid?: number) {
			this.recordState()
			await router.push({ name: 'Chat', params: { uuid } })
		},

		recordState() {
			setLocalState(this.$state)
		},
		toMainPage() {
			const mode = this.aiMode
			if (mode === AiMode.MyFavorites)
				router.push('/my-favorites')
			else if (mode === AiMode.ChatLLM)
				router.push('/chatllm')
			else if (mode === AiMode.KnowledgeBase)
				router.push('/ai-square')
			else if (mode === AiMode.Admin)
				router.push('/admin')
			else if (mode === AiMode.DigitalPerson)
				router.push('/digital-person')
			else if (mode === AiMode.TextToImage)
				router.push('/text-to-image')
			else
				router.push('/my-favorites')
		},

		setSelectedModel(model: string) {
			this.selectedModel = model
		},
	},
})
