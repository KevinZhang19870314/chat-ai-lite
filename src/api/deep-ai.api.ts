import type { GenericAbortSignal } from 'axios'
import type { ChatHistoryMeta, ChatRequest, KnowledgeBase, LocalAIRequest, Prompt, TextToImagePayload, UpdateChatHistoryMeta, UpdatePrompt } from '@/models/chat.model'
import { AiMode } from '@/models/chat.model'
import { del, get, post, put } from '@/utils/request'

export function asyncChatWithRole<T>(question: string, onProgress: Function, data: ChatRequest, abortSignal: GenericAbortSignal) {
	return post<T>({
		url: '/chat-with-role/ask',
		data,
		signal: abortSignal,
		onDownloadProgress: (progressEvent) => {
			onProgress(progressEvent)
		},
	})
}

export function asyncAskBot<T>(request: LocalAIRequest, onProgress: Function, abortSignal: GenericAbortSignal) {
	return post<T>({
		url: '/local-ai/async-ask-bot',
		data: request,
		signal: abortSignal,
		onDownloadProgress: (progressEvent) => {
			onProgress(progressEvent)
		},
	})
}

export function ingestText<T>(text: string) {
	return post<T>({
		url: '/local-ai/ingest-text',
		data: { text },
	})
}

// verify
export function login<T>(username: string, password: string) {
	const formData = new FormData()
	formData.append('username', username)
	formData.append('password', password)

	return post<T>({
		url: '/auth/token',
		data: formData,
		headers: { 'Content-Type': 'multipart/form-data' },
	})
}

export function refreshAccessToken<T>(refreshToken: string) {
	return post<T>({
		url: '/auth/refresh-access-token',
		data: { refresh_token: refreshToken },
	})
}

export function feishuAuth<T>() {
	return get<T>({
		url: '/feishu-auth/auth',
	})
}

export function githubAuth<T>() {
	return get<T>({
		url: '/github/auth',
	})
}

export function session<T>() {
	return get<T>({
		url: '/auth/user',
	})
}

export function registerUser<T>(email: string, password: string, verificationCode: number) {
	return post<T>({
		url: '/auth/register',
		data: { email, password, verification_code: verificationCode },
	})
}

export function sendSMTPVerificationCode<T>(recipient: string) {
	return post<T>({
		url: '/auth/send-verification-code',
		data: { recipient },
	})
}

/** 更新自己的个人信息，任何用户都可以更新自己的用户信息 */
export async function updatePersonalInfo<T>(payload: { id: string, fields: any }) {
	return post<T>({
		url: '/auth/update',
		data: payload,
	})
}

export function createAccount<T>(email: string) {
	return post<T>({
		url: '/auth/user',
		data: { email },
	})
}

export function addChatHistoryMeta<T>(data: ChatHistoryMeta) {
	delete data.id
	delete data.user_id
	if (!data.knowledge_base_id)
		delete data.knowledge_base_id
	return post<T>({
		url: '/chat-history-meta/create',
		data,
	})
}

export function updateChatHistoryMeta<T>(data: UpdateChatHistoryMeta) {
	return post<T>({
		url: '/chat-history-meta/update',
		data,
	})
}

export function getChatHistoryMetasByAIModes<T>(params: string) {
	// Need query params to support array in URL, eg. 'ai_modes=ai_mode1,ai_mode2'
	const data = {
		ai_modes: params,
	}

	return get<T>({
		url: '/chat-history-meta/query-with-ai-modes',
		data,
	})
}

export function deleteChatHistoryMeta<T>(id: string) {
	return post<T>({
		url: '/chat-history-meta/delete',
		data: { id },
	})
}

export function deleteChatHistoryMetaByTitle<T>(title: string) {
	return post<T>({
		url: '/chat-history-meta/delete',
		data: { title },
	})
}

export function getPrompts<T>(term = '') {
	return get<T>({
		url: `/prompt/all${term ? `?term=${term}` : ''}`,
	})
}

export async function getPromptsByPage<T>(limit = 10, page = 1, category = '', isEnabled = 1, term = '') {
	const queryParams: any = {
		page,
		limit,
		is_enabled: isEnabled || 0,
		category: category || undefined,
		term: term || undefined,
	}

	const queryString = Object.keys(queryParams)
		.filter(key => queryParams[key] !== undefined)
		.map(key => `${key}=${queryParams[key]}`)
		.join('&')

	const url = `/prompt/get?${queryString}`

	return get<T>({ url })
}

export function createPrompt<T>(prompt: Prompt) {
	return post<T>({
		url: '/prompt/create',
		data: prompt,
	})
}

export function bulkInsertPrompts<T>(prompts: Prompt[]) {
	return post<T>({
		url: '/prompt/bulk-insert',
		data: prompts,
	})
}

export function updatePrompt<T>(data: UpdatePrompt) {
	return post<T>({
		url: '/prompt/update',
		data,
	})
}

export function likesPrompt<T>(data: { id: string, likes: boolean }) {
	return post<T>({
		url: '/prompt/likes',
		data,
	})
}

export function deletePrompt<T>(id: string) {
	return post<T>({
		url: '/prompt/delete',
		data: { id },
	})
}

export function togglePrompt<T>(id: string, isEnabled: boolean) {
	return post<T>({
		url: '/prompt/toggle',
		data: { id, is_enabled: isEnabled },
	})
}

export function getVectorDocRecordsByPage<T>(limit = 10, page = 1, knowledge_base_id: string, term = '') {
	return get<T>({
		url: `/vector-doc-record/get?page=${page}&limit=${limit}&knowledge_base_id=${knowledge_base_id}${term ? `&term=${term}` : ''}`,
	})
}

export function deleteVectorDocRecordByFilename<T>(filename: string, knowledge_base_id: string, ai_mode: AiMode = AiMode.LocalAI) {
	return post<T>({
		url: '/vector-doc-record/delete-by-filename',
		data: { filename, knowledge_base_id, ai_mode },
	})
}

export function createKnowledgeBase<T>(knowledgeBase: KnowledgeBase) {
	return post<T>({
		url: '/knowledge-base/create',
		data: knowledgeBase,
	})
}

export function updateKnowledgeBase<T>(payload: { id: string, fields: any }) {
	return post<T>({
		url: '/knowledge-base/update',
		data: payload,
	})
}

export function getKnowledgeBaseByPage<T>(limit = 10, page = 1, term = '', type = 'localai') {
	return get<T>({
		url: `/knowledge-base/get?page=${page}&limit=${limit}${term ? `&term=${term}` : ''}${type ? `&type=${type}` : ''}`,
	})
}

export function getUsePlugins<T>(knowledgeBaseId: string) {
	return get<T>({
		url: `/knowledge-base/get-use-plugins/${knowledgeBaseId}`,
	})
}

export function deleteKnowledgeBase<T>(id: string, ai_mode: AiMode = AiMode.LocalAI) {
	return post<T>({
		url: '/knowledge-base/delete',
		data: { id, ai_mode },
	})
}

export function getPlugins<T>() {
	return get<T>({
		url: '/plugins/all',
	})
}

export function getActivePlugins<T>() {
	return get<T>({
		url: '/plugins/active',
	})
}

export function deletePlugin<T>(id: string) {
	return del<T>({
		url: `/plugins/${id}`,
	})
}

export function togglePlugin<T>(id: string) {
	return put<T>({
		url: `/plugins/toggle/${id}`,
	})
}

export function uploadRegistry<T>(urlRepo: string) {
	return post<T>({
		url: '/plugins/upload-registry',
		data: { url: urlRepo },
	})
}

export function getUserByPage<T>(limit = 10, page = 1, email = '', type = '') {
	return get<T>({
		url: `/user/get?page=${page}&limit=${limit}${email ? `&email=${email}` : ''}${type ? `&type=${type}` : ''}`,
	})
}

export function deleteUser<T>(id: string) {
	return post<T>({
		url: '/user/delete',
		data: { id },
	})
}

/** 更新其他用户，只有admin或者super_admin才有权限 */
export async function updateUser<T>(payload: { id: string, fields: any }) {
	return post<T>({
		url: '/user/update',
		data: payload,
	})
}

export function asyncChatLLM<T>(data: ChatRequest, abortSignal: GenericAbortSignal, onProgress: Function) {
	return post<T>({
		url: '/chat-llm/chat',
		data,
		signal: abortSignal,
		onDownloadProgress: (progressEvent) => {
			onProgress(progressEvent)
		},
	})
}

export function textToImage<T>(payload: TextToImagePayload) {
	return post<T>({
		url: '/text-to-image/generate',
		data: payload,
	})
}

export function getTextToImagesByPage<T>(limit = 10, page = 1, term = '') {
	return get<T>({
		url: `/text-to-image/get?page=${page}&limit=${limit}${term ? `&term=${term}` : ''}`,
	})
}
