<script setup lang='ts'>
import { NButton, NInput, NSpin, useMessage } from 'naive-ui'
import { ref } from 'vue'
import { useUserStore } from '@/store'

const loading = ref(false)
const errorMessage = ref('INIT')
const email = ref('')
const password = ref('')
const ms = useMessage()
const userStore = useUserStore()

async function createUser() {
  try {
    const genUser = await userStore.createUserInfo({ email: email.value })
    email.value = genUser.email
    password.value = genUser.password

    errorMessage.value = ''
  }
  catch (error: any) {
    ms.error(`${error}`)
    errorMessage.value = error.message
  }
}
</script>

<template>
  <NSpin :show="loading">
    <div class="p-4 space-y-5 min-h-[200px]">
      <div class="space-y-6">
        <div v-if="errorMessage !== 'INIT'" class="p-4 rounded-md bg-neutral-100 dark:bg-neutral-700">
          <template v-if="errorMessage">
            <p>
              {{ $t('setting.createUserFailed') }}
            </p>
            <p>
              {{ errorMessage }}
            </p>
          </template>
          <template v-else>
            <p>
              {{ $t('setting.createUserSuccess') }}
            </p>
            <p>
              {{ $t('setting.email') }}：{{ email }}
            </p>
            <p>
              {{ $t('setting.password') }}：{{ password }}
            </p>
          </template>
        </div>
        <div class="flex items-center space-x-4">
          <span class="flex-shrink-0 w-[100px]">{{ $t('setting.email') }}</span>
          <div class="flex-1">
            <NInput v-model:value="email" :placeholder="$t('setting.emailPlaceholder')" />
          </div>
        </div>
        <div class="flex items-center justify-end space-x-4">
          <NButton size="large" type="primary" @click="createUser()">
            {{ $t('setting.createUser') }}
          </NButton>
        </div>
      </div>
    </div>
  </NSpin>
</template>
