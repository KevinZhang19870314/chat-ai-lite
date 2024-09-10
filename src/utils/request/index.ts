import type { AxiosProgressEvent, AxiosResponse, ResponseType as AxiosResponseType, GenericAbortSignal } from 'axios'
import request from './axios'
import { useAuthStore } from '@/store'

export interface HttpOption {
  url: string
  data?: any
  method?: string
  headers?: any
  onDownloadProgress?: (progressEvent: AxiosProgressEvent) => void
  signal?: GenericAbortSignal
  responseType?: AxiosResponseType
  beforeRequest?: () => void
  afterRequest?: () => void
}

export interface Response<T = any> {
  data: T
  message: string | null
  status: string
}

function http<T = any>(
  { url, data, method, headers, onDownloadProgress, signal, beforeRequest, afterRequest, responseType }: HttpOption,
) {
  const successHandler = (res: AxiosResponse<Response<T>>) => {
    const authStore = useAuthStore()

    if (res.data.status === 'Success' || res.status === 200 || typeof res.data === 'string')
      return res.data

    if (res.data.status === 'Unauthorized') {
      authStore.removeToken()
      window.location.reload()
    }

    return Promise.reject(res.data)
  }

  const failHandler = (error: Response<Error> | any) => {
    afterRequest?.()
    // if (error.response?.status === 401) {
    //   const authStore = useAuthStore()
    //   authStore.removeToken()
    //   authStore.session = { auth: true, model: 'ChatGPTAPI', user: {} }
    // }

    // throw new Error(error)
    return Promise.reject(error)
  }

  beforeRequest?.()

  method = method || 'GET'

  const params = Object.assign(typeof data === 'function' ? data() : data ?? {}, {})

  if (method === 'GET')
    return request.get(url, { params, signal, responseType, onDownloadProgress }).then(successHandler, failHandler)
  else if (method === 'POST')
    return request.post(url, params, { headers, signal, responseType, onDownloadProgress }).then(successHandler, failHandler)
  else if (method === 'DELETE')
    return request.delete(url, { params, signal, onDownloadProgress }).then(successHandler, failHandler)
  else if (method === 'PUT')
    return request.put(url, params, { headers, signal, onDownloadProgress }).then(successHandler, failHandler)
  else if (method === 'PATCH')
    return request.patch(url, params, { headers, signal, onDownloadProgress }).then(successHandler, failHandler)
  else throw new Error('不支持的请求方式')
}

export function get<T = any>(
  { url, data, method = 'GET', onDownloadProgress, signal, beforeRequest, afterRequest, responseType = 'json' }: HttpOption,
): Promise<Response<T>> {
  return http<T>({
    url,
    method,
    data,
    onDownloadProgress,
    signal,
    beforeRequest,
    afterRequest,
    responseType,
  })
}

export function del<T = any>(
  { url, data, method = 'DELETE', headers, onDownloadProgress, signal, beforeRequest, afterRequest }: HttpOption,
): Promise<Response<T>> {
  return http<T>({
    url,
    method,
    data,
    headers,
    onDownloadProgress,
    signal,
    beforeRequest,
    afterRequest,
  })
}

export function put<T = any>(
  { url, data, method = 'PUT', headers, onDownloadProgress, signal, beforeRequest, afterRequest }: HttpOption,
): Promise<Response<T>> {
  return http<T>({
    url,
    method,
    data,
    headers,
    onDownloadProgress,
    signal,
    beforeRequest,
    afterRequest,
  })
}

export function post<T = any>(
  { url, data, method = 'POST', headers, onDownloadProgress, signal, beforeRequest, afterRequest, responseType = 'json' }: HttpOption,
): Promise<Response<T>> {
  return http<T>({
    url,
    method,
    data,
    headers,
    onDownloadProgress,
    signal,
    beforeRequest,
    afterRequest,
    responseType,
  })
}

export default post
