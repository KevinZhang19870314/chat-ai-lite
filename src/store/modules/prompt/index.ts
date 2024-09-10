import { defineStore } from 'pinia'
import type { PromptStore } from './helper'
import { setLocalPromptList } from './helper'
import type { Prompt, UpdatePrompt } from '@/models/chat.model'
import { bulkInsertPrompts, createPrompt, deletePrompt, getPrompts, getPromptsByPage, likesPrompt, togglePrompt, updatePrompt } from '@/api'

export const usePromptStore = defineStore('prompt-store', {
	state: (): PromptStore => {
		return {
			promptList: [],
		}
	},

	actions: {
		async fetchPromptList() {
			const res = await getPrompts<Prompt[]>()
			if (res.status === 'Error')
				throw res.message

			this.promptList = res.data
		},
		async fetchPromptListByPage(pageSize: number, page: number, category = '', isEnabled = 1, term = '') {
			const res = await getPromptsByPage<{ prompts: Prompt[], total: number }>(pageSize, page, category, isEnabled, term)
			if (res.status === 'Error')
				throw res.message

			this.promptList = res.data.prompts || []
			return res.data.total
		},
		async createPrompt(prompt: Prompt) {
			const res = await createPrompt<Prompt>(prompt)
			if (res.status === 'Error')
				throw res.message

			return res.data
		},
		async updatePrompt(payload: UpdatePrompt) {
			const res = await updatePrompt<Prompt>(payload)
			if (res.status === 'Error')
				throw res.message

			return res.data
		},
		async likes(payload: { id: string, likes: boolean }) {
			const res = await likesPrompt<Prompt>(payload)
			if (res.status === 'Error')
				throw res.message

			return res.data
		},
		async deletePrompt(id: string) {
			const res = await deletePrompt(id)
			if (res.status === 'Error')
				throw res.message

			return res.data
		},
		async togglePrompt(id: string, isEnabled: boolean) {
			const res = await togglePrompt(id, isEnabled)
			if (res.status === 'Error')
				throw res.message

			return res.data
		},
		async bulkInsertPrompts(prompts: Prompt[]) {
			const res = await bulkInsertPrompts(prompts)
			if (res.status === 'Error')
				throw res.message
		},
		updatePromptList(promptList: []) {
			this.$patch({ promptList })
			setLocalPromptList({ promptList })
		},
		getPromptList() {
			return this.$state
		},
	},
})
