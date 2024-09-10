export enum AiMode {
	/** 收藏的Prompts等, server端存储 */
	MyFavorites = 'myfavorites',
	/** 管理面板， 仅客户端存储 */
	Admin = 'admin',
	/**
	 * KnowledgeBase 包含 LocalAI、OpenAIAssistants、FeishuRag
	 *
	 * AI 知识库，以上三种的统称，方便UI逻辑，仅客户端存储
	 */
	KnowledgeBase = 'knowledgebase',
	/** 本地向量知识库, server端存储 */
	LocalAI = 'localai',
	/**
	 * 统一了聊天模型，在同一个聊天窗口可以同时使用各种模型
	 */
	ChatLLM = 'chatllm',
	/**
	 * 数字人
	 */
	DigitalPerson = 'digitalperson',
	/**
	 * 文生图
	 */
	TextToImage = 'texttoimage',
}

export enum LocalAIRole {
	AI = 'AI',
	HUMAN = 'Human',
}

export interface LocalAIMessage {
	who: LocalAIRole
	message: string
}

export interface LocalAIRequest {
	text: string
	knowledge_base_id: string
	chat_history: LocalAIMessage[]
}

export enum ChatRole {
	SYSTEM = 'system',
	ASSISTANT = 'assistant',
	USER = 'user',
}

export interface ChatMessage {
	role: ChatRole
	content: string
}

export interface ChatRequest {
	ai_mode?: AiMode
	model?: string
	messages: ChatMessage[]
	max_tokens?: number
	temperature?: number
	uuid?: number
	top_p?: number
	presence_penalty?: number
	frequency_penalty?: number
}

export interface Chat {
	dateTime: string
	text: string
	role?: string
	error?: boolean
	loading?: boolean
	conversationOptions?: ConversationRequest | null
	requestOptions: { prompt: string, options?: ConversationRequest | null }
}

export interface ChatHistoryMeta {
	id?: string
	user_id?: string
	knowledge_base_id?: string
	title: string
	uuid: number
	ai_mode?: AiMode
	icon?: string
	description?: string
	greetings?: string
	assistant_id?: string
	thread_id?: string
	isEdit: boolean
	meta?: string
}

export interface UpdateChatHistoryMeta {
	id: string
	fields: any
}

export interface UpdatePrompt {
	id: string
	fields: any
}

export interface ChatState {
	active: number | null
	history: ChatHistoryMeta[]
	chat: { uuid: number, data: Chat[] }[]
	siderLoading: boolean
	prompt?: string
	aiMode: AiMode
	selectedModel: string
}

export interface ConversationRequest {
	conversationId?: string
	parentMessageId?: string
}

export interface ConversationResponse {
	conversationId: string
	detail: {
		choices: { finish_reason: string, index: number, logprobs: any, text: string }[]
		created: number
		id: string
		model: string
		object: string
		usage: { completion_tokens: number, prompt_tokens: number, total_tokens: number }
	}
	id: string
	parentMessageId: string
	role: string
	text: string
}

export interface Prompt {
	id?: string
	title: string
	description: string
	icon: string
	greetings: string
	category: string
	likes: number
	is_enabled?: boolean
}

export interface VectorDocRecord {
	id?: string
	filename: string
	doc_id: string
	knowledge_base_id?: string
}

export interface KnowledgeBase {
	id?: string
	user_id?: string
	name: string
	icon: string
	description: string
	is_global?: boolean
	use_plugins?: string
	/** OpenAI assistant id */
	assistant_id?: string
	/** OpenAI assistant file ids, comma separated */
	file_ids?: string
	/** If True, use OpenAI code interpreter */
	use_code_interpreter?: boolean
	/** If True, use OpenAI retrieval */
	use_retrieval?: boolean
	type?: Partial<AiMode>
	/** 新增飞书知识库使用，指定当前知识库的父节点token */
	parent_node_token?: string
	/** 新增飞书知识库使用，指定当前知识库的space_id。例如：G2空间ID：6963978910325293060 */
	space_id?: string
}

export interface AvailablePlugin {
	active: boolean
	author_name: string
	author_url: string
	description: string
	id?: string
	name: string
	plugin_url: string
	tags: string
	thumb: string
	version: string
}

export interface TextToImagePayload {
	model: string
	query: string
	is_global?: boolean
}

export interface TextToImage {
	id: string
	user_id: string
	is_global: boolean
	query: string
	model: string
	size: string
	image_url: string
	created_at: Date
	updated_at: Date
}
