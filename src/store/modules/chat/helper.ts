import { getChatHistoryMetasByAIModes } from '@/api'
import type { ChatHistoryMeta, ChatState } from '@/models/chat.model'
import { AiMode } from '@/models/chat.model'
import { generateSessionId } from '@/utils/functions'
import { ss } from '@/utils/storage'

const LOCAL_NAME = 'chatStorage'

export function defaultState(): ChatState {
	const uuid = generateSessionId()
	return {
		active: uuid,
		history: [{ uuid, title: 'New Chat', isEdit: false }],
		aiMode: AiMode.MyFavorites,
		chat: [{ uuid, data: [] }],
		siderLoading: false,
		prompt: '',
		selectedModel: '',
	}
}

export function getLocalState(): ChatState {
	const localState = ss.get(LOCAL_NAME)
	return { ...defaultState(), ...localState }
}

export function setLocalState(state: ChatState) {
	ss.set(LOCAL_NAME, state)
}

export async function fetchChatHistoryMetasWithAiModes(aiMode: AiMode): Promise<ChatHistoryMeta[]> {
	let params = ''
	if (aiMode === AiMode.KnowledgeBase)
		params = [AiMode.LocalAI].join(',')
	else
		params = [aiMode].join(',')

	const res = await getChatHistoryMetasByAIModes(params)
	if (res.status === 'Fail' || res.status === 'Error')
		throw new Error(`${res.message}`)
	return res.data as ChatHistoryMeta[]
}
