import type { AvailablePlugin, KnowledgeBase } from '@/models/chat.model'

export interface LocalAIStore {
	vectorDocRecordList: string[]
	currentKnowledgeBase: KnowledgeBase | null
	knowledgeBaseList: KnowledgeBase[]
	pluginsList: AvailablePlugin[]
	activePluginsList?: AvailablePlugin[]
	refreshMode?: 'default' | 'localai' | 'openaiassistants' | 'feishu_rag'
	currentKnowledgeBaseTab?: 'localai' | 'openaiassistants' | 'feishu_rag'
}
