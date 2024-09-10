import { ss } from '@/utils/storage'

const LOCAL_NAME = 'SECRET_TOKEN'
const LOCAL_NAME_REFRESH = 'SECRET_REFRESH_TOKEN'

export function getToken() {
  return ss.get(LOCAL_NAME)
}

export function setToken(token: string) {
  return ss.set(LOCAL_NAME, token)
}

export function removeToken() {
  return ss.remove(LOCAL_NAME)
}

export function getRefreshToken() {
  return ss.get(LOCAL_NAME_REFRESH)
}

export function setRefreshToken(token: string) {
  return ss.set(LOCAL_NAME_REFRESH, token)
}

export function removeRefreshToken() {
  return ss.remove(LOCAL_NAME_REFRESH)
}
