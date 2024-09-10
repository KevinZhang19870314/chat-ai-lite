import axios, { type AxiosResponse } from 'axios'
import { useAuthStore } from '@/store'

const service = axios.create({
  baseURL: import.meta.env.VITE_GLOB_DEEP_AI_API_URL,
})

service.interceptors.request.use(
  (config) => {
    const token = useAuthStore().token
    if (token)
      config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => {
    return Promise.reject(error.response)
  },
)

service.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => {
    if (response.status === 200)
      return response

    throw new Error(response.status.toString())
  },
  async (error) => {
    const originalRequest = error.config
    // 检测是否因为令牌过期导致的401错误
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      const authStore = useAuthStore()
      if (authStore.refreshToken) {
        originalRequest._retry = true

        await authStore.refreshAccessToken(authStore.refreshToken!)
        originalRequest.headers.Authorization = `Bearer ${authStore.token}`
        return axios(originalRequest) // 重新发送失败的请求
      }
    }

    return Promise.reject(error)
  },
)

export default service
