import { defineStore } from 'pinia'
import type { ToolsStore } from './helper'

export const useToolsStore = defineStore('tools-store', {
	state: (): ToolsStore => {
		return {
			audio: null,
			audioEndedCallback: () => { },
		}
	},

	actions: {
		addAudioEndedListener(func: () => void = () => { }) {
			this.audioEndedCallback = () => {
				func && func()
			}
			this.audio?.addEventListener('ended', this.audioEndedCallback)
		},
		removeAudioEndedListener() {
			this.audio?.removeEventListener('ended', this.audioEndedCallback)
		},
	},
})
