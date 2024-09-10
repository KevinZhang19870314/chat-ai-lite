import { defineStore } from 'pinia'
import { getRefreshToken, getToken, removeRefreshToken, removeToken, setRefreshToken, setToken } from './helper'
import { refreshAccessToken, session } from '@/api'
import { store, useUserStore } from '@/store'

interface SessionResponse {
  auth: boolean
  model: 'ChatGPTAPI' | 'ChatGPTUnofficialProxyAPI'
  user: object | null
}

export interface AuthState {
  token: string | undefined
  refreshToken: string | undefined
  session: SessionResponse | null
}

export const useAuthStore = defineStore('auth-store', {
  state: (): AuthState => ({
    token: getToken(),
    refreshToken: getRefreshToken(),
    session: null,
  }),

  getters: {
    isChatGPTAPI(state): boolean {
      return state.session?.model === 'ChatGPTAPI'
    },
  },

  actions: {
    async getSession() {
      try {
        const { data } = await session<any>()
        const userStore = useUserStore()
        userStore.updateUserInfo(data)
        this.session = { auth: false, model: 'ChatGPTAPI', user: data }
        return Promise.resolve(this.session)
      }
      catch (error) {
        this.session = { auth: true, model: 'ChatGPTAPI', user: {} }
        return Promise.reject(error)
      }
    },

    async refreshAccessToken(refreshToken: string) {
      try {
        const tokenData = await refreshAccessToken(refreshToken)
        this.setToken((tokenData as any)?.access_token)
        this.setRefreshToken((tokenData as any)?.refresh_token)
        return Promise.resolve(tokenData)
      }
      catch (error) {
        return Promise.reject(error)
      }
    },

    setToken(token: string) {
      this.token = token
      setToken(token)
    },

    removeToken() {
      this.token = undefined
      removeToken()
    },

    setRefreshToken(token: string) {
      this.refreshToken = token
      setRefreshToken(token)
    },

    removeRefreshToken() {
      this.refreshToken = undefined
      removeRefreshToken()
    },
  },
})

export function useAuthStoreWithout() {
  return useAuthStore(store)
}
