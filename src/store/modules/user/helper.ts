import { ss } from '@/utils/storage'

const LOCAL_NAME = 'userStorage'

export enum UserType {
	Normal = 'normal',
	Premium = 'premium',
	Admin = 'admin',
	SuperAdmin = 'super_admin',
}

export interface UserInfo {
	avatar?: string
	description?: string
	id?: string
	email?: string
	nickname?: string
	charged_amount?: number
	total_requests?: number
	used_requests?: number
	merchant_order_id?: number
	is_feishu_user?: boolean
	is_github_user?: boolean
	type?: UserType
	model?: string
	total_image_requests?: number
	used_image_requests?: number
}

export interface UserState {
	userInfo: UserInfo
	userList?: UserInfo[]
}

export function defaultSetting(): UserState {
	return {
		userInfo: {
			avatar: 'https://cdn-icons-png.flaticon.com/512/1698/1698535.png',
			email: 'admin@admin.com',
			description: '天苍苍，野茫茫，风吹草低见牛羊。',
			model: 'gpt-3.5-turbo',
		},
	}
}

export function getLocalState(): UserState {
	const localSetting: UserState | undefined = ss.get(LOCAL_NAME)
	return { ...defaultSetting(), ...localSetting }
}

export function setLocalState(setting: UserState): void {
	ss.set(LOCAL_NAME, setting)
}
