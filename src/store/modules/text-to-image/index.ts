import { defineStore } from 'pinia'
import type { TextToImageStore } from './helper'
import { TextToImagePayload } from '@/models/chat.model'
import { getTextToImagesByPage, textToImage } from '@/api'

export const useTextToImageStore = defineStore('text-to-image', {
	state: (): TextToImageStore => {
		return {
			imageUrl: '',
			records: [],
		}
	},

	actions: {
		async generateImage(payload: TextToImagePayload) {
			const res = await textToImage(payload)
			if (res.status === 'Error') {
				this.imageUrl = ''
				throw res.message
			}

			this.imageUrl = res.data as string
			return res.data
		},
		async fetchTextToImageListByPage(pageSize: number, page: number, term = '') {
			const res = await getTextToImagesByPage<{ records: any, total: number }>(pageSize, page, term)
			if (res.status === 'Error') {
				this.records = []
				throw res.message
			}

			this.records = res.data.records || []
			// this.records = Array.from({ length: 10 }, () => res.data.records).flat()
			return +res.data.total
		},
	},
})
