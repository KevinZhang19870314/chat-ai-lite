import { defineStore } from 'pinia'
import type { UserInfo, UserState } from './helper'
import { UserType, defaultSetting, getLocalState, setLocalState } from './helper'
import { createAccount, deleteUser, getUserByPage, updatePersonalInfo, updateUser } from '@/api'

export const useUserStore = defineStore('user-store', {
	state: (): UserState => {
		return {
			userInfo: getLocalState().userInfo,
			userList: [],
		}
	},
	getters: {
		/** super_admin:超级管理员用户，拥有管理员用户的权限，并可以添加订阅 & 创建普通用户等能力 */
		isSuperAdmin(state) {
			return state.userInfo?.type === UserType.SuperAdmin
		},
		/** 管理员用户 OR 超级管理员用户，拥有高级用户的权限，并可以访问所有模块 */
		isAdminAndAbove(state) {
			return state.userInfo?.type === UserType.Admin || state.userInfo?.type === UserType.SuperAdmin
		},
		/** 管理员用户，拥有高级用户的权限，并可以访问所有模块 */
		isAdmin(state) {
			return state.userInfo?.type === UserType.Admin
		},
		/** 高级用户及以上权限 */
		isPremiumAndAbove(state) {
			return state.userInfo?.type === UserType.Premium || state.userInfo?.type === UserType.Admin || state.userInfo?.type === UserType.SuperAdmin
		},
		/** premium: 拥有普通用户的权限，并可以访问文档翻译模块和GPT 4 */
		isPremium(state) {
			return state.userInfo?.type === UserType.Premium
		},
		/** normal:普通用户，可以使用ChatGPT 3.5 */
		isNormal(state) {
			return state.userInfo?.type === UserType.Normal
		},
		isFeishuUser(state) {
			return state.userInfo?.is_feishu_user
		},
		isGithubUser(state) {
			return state.userInfo?.is_github_user
		},
	},
	actions: {
		getModels() {
			const modelOptions = [
				{
					label: 'Claude 3 Sonnet',
					key: 'claude-3-sonnet-20240229',
					value: 'claude-3-sonnet-20240229',
					icon: 'logos:anthropic-icon',
					disabled: false,
				},
				{
					label: 'Claude 3 Opus',
					key: 'claude-3-opus-20240229',
					value: 'claude-3-opus-20240229',
					disabled: false,
					icon: 'logos:anthropic-icon',
				},
				{
					label: '通义千问 / qwen-turbo',
					key: 'qwen-turbo',
					value: 'qwen-turbo',
					icon: 'logos:turbopack-icon',
				},
				{
					label: '通义千问 / qwen-plus',
					key: 'qwen-plus',
					value: 'qwen-plus',
					icon: 'icon-park:plus-cross',
				},
				{
					label: '通义千问 / qwen-max',
					key: 'qwen-max',
					value: 'qwen-max',
					icon: 'logos:mixmax',
				},
				{
					label: '谷歌 Gemini Pro',
					key: 'gemini-pro',
					value: 'gemini-pro',
					icon: 'simple-icons:googlegemini',
				},
				{
					label: 'Hugging Face Gemma 2B',
					key: 'hf/google/gemma-2b-it',
					value: 'hf/google/gemma-2b-it',
					icon: 'openmoji:hugging-face',
					disabled: false,
				},
				{
					label: 'Hugging Face Gemma 7B',
					key: 'hf/google/gemma-7b-it',
					value: 'hf/google/gemma-7b-it',
					icon: 'openmoji:hugging-face',
					disabled: false,
				},
				{
					label: 'Mistral 7B',
					key: 'mistralai/Mistral-7B-Instruct-v0.1',
					value: 'mistralai/Mistral-7B-Instruct-v0.1',
					icon: 'logos:mistral-ai-icon',
				},
				{
					label: 'Mixtral 8x7B',
					key: 'mistralai/Mixtral-8x7B-Instruct-v0.1',
					value: 'mistralai/Mixtral-8x7B-Instruct-v0.1',
					disabled: this.isNormal,
					icon: 'logos:mistral-ai-icon',
				},
				{
					label: '月之暗面 8K',
					key: 'moonshot-v1-8k',
					value: 'moonshot-v1-8k',
					icon: 'solar:moon-fog-bold',
				},
				{
					label: '月之暗面 32K',
					key: 'moonshot-v1-32k',
					value: 'moonshot-v1-32k',
					icon: 'solar:moon-fog-bold',
				},
				{
					label: '月之暗面 128k',
					key: 'moonshot-v1-128k',
					value: 'moonshot-v1-128k',
					disabled: this.isNormal,
					icon: 'solar:moon-fog-bold',
				},
				{
					label: 'Azure GPT-3.5 Turbo',
					key: 'azure-jp-gpt3',
					value: 'azure-jp-gpt3',
					icon: 'devicon:azure',
					disabled: false,
				},
				{
					label: 'GPT-3.5 Turbo 1106',
					key: 'gpt-3.5-turbo-1106',
					value: 'gpt-3.5-turbo-1106',
					icon: 'logos:openai-icon',
				},
				{
					label: 'GPT-3.5 Turbo 0125 (推荐)',
					key: 'gpt-3.5-turbo-0125',
					value: 'gpt-3.5-turbo-0125',
					icon: 'logos:openai-icon',
				},
				{
					label: 'GPT-3.5 Turbo',
					key: 'gpt-3.5-turbo',
					value: 'gpt-3.5-turbo',
					icon: 'logos:openai-icon',
				},
				{
					label: 'GPT-3.5 Turbo 16k',
					key: 'gpt-3.5-turbo-16k',
					value: 'gpt-3.5-turbo-16k',
					icon: 'logos:openai-icon',
				},
				{
					label: 'gpt-4o (推荐)',
					key: 'gpt-4o',
					value: 'gpt-4o',
					disabled: this.isNormal,
					icon: 'logos:openai-icon',
				},
				{
					label: 'gpt-4-turbo (推荐)',
					key: 'gpt-4-turbo',
					value: 'gpt-4-turbo',
					disabled: this.isNormal,
					icon: 'logos:openai-icon',
				},
				{
					label: 'GPT-4 Turbo 2024-04-09 (推荐)',
					key: 'gpt-4-turbo-2024-04-09',
					value: 'gpt-4-turbo-2024-04-09',
					disabled: this.isNormal,
					icon: 'logos:openai-icon',
				},
				{
					label: 'GPT-4 0125 Preview',
					key: 'gpt-4-0125-preview',
					value: 'gpt-4-0125-preview',
					disabled: this.isNormal,
					icon: 'logos:openai-icon',
				},
				{
					label: 'GPT-4 1106 Preview',
					key: 'gpt-4-1106-preview',
					value: 'gpt-4-1106-preview',
					disabled: this.isNormal,
					icon: 'logos:openai-icon',
				},
				{
					label: 'GPT-4',
					key: 'gpt-4',
					value: 'gpt-4',
					disabled: this.isNormal,
					icon: 'logos:openai-icon',
				},
				{
					label: 'GPT-4 32k',
					key: 'gpt-4-32k',
					value: 'gpt-4-32k',
					disabled: this.isNormal,
					icon: 'logos:openai-icon',
				},
				{
					label: 'GPT-4 0613',
					key: 'gpt-4-0613',
					value: 'gpt-4-0613',
					disabled: this.isNormal,
					icon: 'logos:openai-icon',
				},
				{
					label: 'GPT-4 32k 0613',
					key: 'gpt-4-32k-0613',
					value: 'gpt-4-32k-0613',
					disabled: this.isNormal,
					icon: 'logos:openai-icon',
				},
			]
			return modelOptions
		},
		async createUserInfo(userInfo: Partial<UserInfo>): Promise<{ email: string, password: string }> {
			try {
				const res = await createAccount<{ email: string, password: string }>(userInfo.email!)
				if (res.status === 'Fail' || res.status === 'Error')
					throw new Error(`${res.message}`)

				return Promise.resolve(res.data)
			}
			catch (error) {
				return Promise.reject(error)
			}
		},
		updateUserInfo(userInfo: Partial<UserInfo>) {
			if (!userInfo)
				this.userInfo = {}
			else
				this.userInfo = { ...this.userInfo, ...userInfo }
			this.recordState()
		},

		resetUserInfo() {
			this.userInfo = { ...defaultSetting().userInfo }
			this.recordState()
		},

		recordState() {
			setLocalState(this.$state)
		},

		async updateModelToDB(id: string, model: string) {
			try {
				this.userInfo.model = model
				this.recordState()

				const payload = {
					id,
					fields: {
						model,
					},
				}

				const res = await updatePersonalInfo(payload)
				if (res.status === 'Fail' || res.status === 'Error')
					throw new Error(`${res.message}`)

				return Promise.resolve(res.data)
			}
			catch (error) {
				return Promise.reject(error)
			}
		},

		updateAvatarToDB(id: string, avatar: string) {
			this.userInfo.avatar = avatar
			this.recordState()

			const payload = {
				id,
				fields: {
					avatar,
				},
			}

			updatePersonalInfo(payload)
		},

		updateDescriptionToDB(id: string, description: string) {
			this.userInfo.description = description
			this.recordState()

			const payload = {
				id,
				fields: {
					description,
				},
			}

			updatePersonalInfo(payload)
		},

		updateNicknameToDB(id: string, nickname: string) {
			this.userInfo.nickname = nickname
			this.recordState()

			const payload = {
				id,
				fields: {
					nickname,
				},
			}

			updatePersonalInfo(payload)
		},

		async fetchUserListByPage(pageSize: number, page: number, email = '', type = '') {
			const res = await getUserByPage<{ records: any, total: number }>(pageSize, page, email, type)
			if (res.status === 'Error') {
				this.userList = []
				throw res.message
			}

			this.userList = res.data.records || []
			return res.data.total
		},

		async deleteUser(id: string) {
			const res = await deleteUser(id)
			if (res.status === 'Error')
				throw res.message

			return res.data
		},

		async upgradeToPremium(id: string, total_image_requests: number) {
			const res = await updateUser({ id, fields: { type: UserType.Premium, total_image_requests } })
			if (res.status === 'Error')
				throw res.message

			return res.data
		},

		async appendTextToImageRequestsToDB(id: string, times: number) {
			this.userInfo.total_image_requests = times
			this.recordState()

			const payload = {
				id,
				fields: {
					total_image_requests: times,
				},
			}

			const res = await updateUser(payload)
			if (res.status === 'Error')
				throw res.message

			return res.data
		},
	},
})
