import type { Router } from 'vue-router'
import { WHITE_LIST } from './whiteList'
import { useAuthStoreWithout } from '@/store/modules/auth'

export function setupPageGuard(router: Router) {
  router.beforeEach(async (to, from, next) => {
    if (WHITE_LIST.find(item => (to.path === item || to.path.includes(item)))) {
      next()
      return
    }

    const authStore = useAuthStoreWithout()
    if (!authStore.session) {
      try {
        const data = await authStore.getSession()
        if (String(data.auth) === 'true')
          authStore.removeToken()
        if (to.path === '/500')
          next({ name: 'Root' })
        else
          next()
      }
      catch (error: any) {
        if (to.path !== '/500') {
          if (error && error.response && error.response.status === 401) {
            authStore.removeToken()
            authStore.session = { auth: true, model: 'ChatGPTAPI', user: {} }
            next('/authorize')
          }
          else { next({ name: '500' }) }
        }
        else { next() }
      }
    }
    else {
      if (authStore.session.auth && to.path !== '/authorize')
        next('/authorize')
      else
        next()
    }
  })
}
