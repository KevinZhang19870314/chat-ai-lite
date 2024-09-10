import { defineStore } from 'pinia'
import type { LocalAIStore } from './helper'
import { createKnowledgeBase, deleteKnowledgeBase, deletePlugin, deleteVectorDocRecordByFilename, getActivePlugins, getKnowledgeBaseByPage, getPlugins, getVectorDocRecordsByPage, togglePlugin, updateKnowledgeBase, uploadRegistry } from '@/api'
import type { AvailablePlugin, KnowledgeBase } from '@/models/chat.model'
import { AiMode } from '@/models/chat.model'

export const useAISquareStore = defineStore('ai-square-store', {
	state: (): LocalAIStore => {
		return {
			vectorDocRecordList: [],
			currentKnowledgeBase: null,
			knowledgeBaseList: [],
			pluginsList: [],
			activePluginsList: [],
			refreshMode: 'default',
			currentKnowledgeBaseTab: 'localai',
		}
	},

	actions: {
		async fetchVectorDocRecordListByPage(pageSize: number, page: number, knowledge_base_id: string, term = '') {
			const res = await getVectorDocRecordsByPage<{ records: string[], total: number }>(pageSize, page, knowledge_base_id, term)
			if (res.status === 'Error')
				throw res.message

			this.vectorDocRecordList = res.data.records || []
			return res.data.total
		},
		async fetchAllPlugins() {
			const res = await getPlugins<{ installed: AvailablePlugin[], registry: AvailablePlugin[] }>()
			if (res.status === 'Error')
				throw res.message

			this.pluginsList = [...res.data.installed, ...res.data.registry]
			return this.pluginsList
		},
		async fetchActivePlugins() {
			const res = await getActivePlugins<AvailablePlugin[]>()
			if (res.status === 'Error')
				throw res.message

			this.activePluginsList = res.data
			this.activePluginsList = this.activePluginsList.filter((plugin: AvailablePlugin) => plugin.id !== 'core_plugin')
			return this.activePluginsList
		},
		async deletePlugin(id: string) {
			const res = await deletePlugin(id)
			if (res.status === 'Error')
				throw res.message

			return res
		},
		async togglePlugin(id: string) {
			const res = await togglePlugin(id)
			if (res.status === 'Error')
				throw res.message

			return res
		},
		async uploadPluginFromGithub(urlRepo: string) {
			const res = await uploadRegistry(urlRepo)
			if (res.status === 'Error')
				throw res.message

			return res
		},
		async removeVectorDocRecordByFilename(filename: string, knowledge_base_id: string, aiMode: AiMode) {
			const res = await deleteVectorDocRecordByFilename(filename, knowledge_base_id, aiMode)
			if (res.status === 'Error')
				throw res.message
		},
		async removeKnowledgeBaseByKnowledgeBaseId(knowledge_base_id: string, ai_mode: AiMode) {
			const res = await deleteKnowledgeBase(knowledge_base_id, ai_mode)
			if (res.status === 'Error')
				throw res.message
		},
		setCurrentKnowledgeBase(knowledgeBase: KnowledgeBase) {
			this.currentKnowledgeBase = knowledgeBase
		},
		async addKnowledgeBase(knowledgeBase: KnowledgeBase) {
			delete knowledgeBase.id
			delete knowledgeBase.user_id
			const res = await createKnowledgeBase(knowledgeBase)
			if (res.status === 'Error')
				throw res.message

			return res.data
		},
		async updateKnowledgeBase(knowledgeBase: KnowledgeBase) {
			const payload: { id: string, fields: any } = {
				id: knowledgeBase.id!,
				fields: { ...knowledgeBase },
			}

			delete payload.fields.id
			if (payload.fields.is_global)
				delete payload.fields.user_id

			const res = await updateKnowledgeBase(payload)
			if (res.status === 'Error')
				throw res.message

			return res.data
		},
		async fetchKnowledgeBaseListByPage(pageSize: number, page: number, term = '', type = 'localai') {
			const res = await getKnowledgeBaseByPage<{ records: KnowledgeBase[], total: number }>(pageSize, page, term, type)
			if (res.status === 'Error')
				throw res.message

			if (type === AiMode.LocalAI)
				this.knowledgeBaseList = res.data.records

			return res.data.total
		},
		setRefreshMode(mode: 'default' | 'localai' | 'openaiassistants' | 'feishu_rag') {
			this.refreshMode = mode
		},
		setCurrentKnowledgeBaseTab(tab: 'localai' | 'openaiassistants' | 'feishu_rag') {
			this.currentKnowledgeBaseTab = tab
		},
	},
})
