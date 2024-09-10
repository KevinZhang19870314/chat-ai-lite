<script lang="ts" setup>
import { useMessage } from 'naive-ui'
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store'
import { t } from '@/locales'

const ms = useMessage()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const email = route.query.email
const token = route.query.token
const refreshToken = route.query.refresh_token

onMounted(async () => {
  if (!email || !token) {
    ms.error(t('chat.githubAuthFail'))
    router.replace({ name: 'Root' })
    return
  }

  authStore.setToken(`${token}`)
  authStore.setRefreshToken(`${refreshToken}`)
  await authStore.getSession()
  router.replace({ name: 'Root' })
})
</script>

<template>
  <div class="flex h-full" />
</template>
