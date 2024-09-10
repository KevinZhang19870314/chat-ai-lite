<script setup lang="ts">
import { computed, defineAsyncComponent, h, onMounted, ref } from 'vue'

import { NAvatar, NButton, NDivider, NDropdown, NImage, NList, NListItem, NModal, NSpace, NSpin, NSwitch, NTag, NThing, NUpload, useDialog, useMessage } from 'naive-ui'
import { useAISquareStore, useAuthStore, useUserStore } from '@/store'
import { SvgIcon } from '@/components/common'
import type { AvailablePlugin } from '@/models/chat.model'
import { t } from '@/locales'

interface Props {
  visible: boolean
}

interface Emit {
  (ev: 'update:visible', visible: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emit>()

const UploadPluginRepo = defineAsyncComponent(() => import('@/views/home/components/UploadPluginRepo/index.vue'))
const showUploadPluginRepoModal = ref(false)
const authStore = useAuthStore()
const userStore = useUserStore()
const dialog = useDialog()
const aiSquareStore = useAISquareStore()
const pluginsList = computed(() => aiSquareStore.pluginsList)
const ms = useMessage()
const headers = computed(() => {
  return {
    Authorization: `Bearer ${authStore.token}`,
  }
})

const loading = ref(false)
const disabled = computed(() => {
  return !userStore.isAdminAndAbove
})

const uploadOptions = [
  {
    key: 'FILE',
    type: 'render',
    render: () => {
      return h(NUpload, {
        multiple: false,
        headers: headers.value,
        disabled: disabled.value,
        action: '/deep-ai/plugins/upload',
        accept: '.zip,.tar',
        onFinish: ({ file, _ }: any) => {
          ms.success(t('upload.uploadFileSuccess'))
          return file
        },
        onError: ({ file, event }: any) => {
          ms.error((event?.target as any).response || t('upload.uploadFileFailed'))
          return file
        },
      }, () => [
        h(NButton, {
          tertiary: true,
          block: true,
          disabled: disabled.value,
        }, () => [
          h(SvgIcon, {
            icon: 'material-symbols:folder-zip',
            class: 'mr-2 text-xl',
          }),
          t('localAI.fromFile'),
        ]),
      ])
    },
  },
  {
    key: 'GITHUB',
    type: 'render',
    render: () => {
      return h(NButton, {
        tertiary: true,
        block: true,
        disabled: disabled.value,
        onClick: () => {
          showUploadPluginRepoModal.value = !showUploadPluginRepoModal.value
        },
      }, () => [
        h(SvgIcon, {
          icon: 'mdi:github',
          class: 'mr-2 text-xl',
        }),
        t('localAI.fromGitHub'),
      ])
    },
  },
]

const showModal = computed({
  get() {
    return props.visible
  },
  set(value) {
    emit('update:visible', value)
  },
})

onMounted(async () => {
  await refresh()
})

function handleRefresh() {
  refresh()
}

async function refresh() {
  loading.value = true
  try {
    await aiSquareStore.fetchAllPlugins()
  }
  catch (error) {
    ms.error(`${error}`)
  }
  finally {
    loading.value = false
  }
}

function handleLink(plugin: AvailablePlugin) {
  window.open(plugin.plugin_url)
}

function handleView(_: AvailablePlugin) {
  ms.info('开发中...')
}

async function handleDelete(plugin: AvailablePlugin) {
  const d = dialog.warning({
    title: t('localAI.deletePlugin'),
    content: t('localAI.deletePluginConfirm'),
    positiveText: t('common.yes'),
    negativeText: t('common.no'),
    onPositiveClick: async () => {
      d.loading = true
      try {
        await aiSquareStore.deletePlugin(plugin.id!)
        await refresh()
      }
      catch (error) {
        ms.error(`${error}`)
      }
      finally {
        d.loading = false
      }
    },
  })
}

async function handleToggle(plugin: AvailablePlugin) {
  loading.value = true
  try {
    await aiSquareStore.togglePlugin(plugin.id!)
    await refresh()
  }
  catch (error) {
    ms.error(`${error}`)
  }
  finally {
    loading.value = false
  }
}

function handleUploadFromGithubSuccess() {
  refresh()
  showUploadPluginRepoModal.value = false
}
</script>

<template>
  <NModal v-model:show="showModal" :mask-closable="false" :title="$t('chat.pluginsManagement')" class="max-w-[960px]" preset="card">
    <NSpin :show="loading">
      <NSpace justify="end">
        <NDropdown
          trigger="hover"
          placement="bottom-start"
          :options="uploadOptions"
        >
          <NButton type="primary">
            <template #icon>
              <SvgIcon icon="uil:upload" class="text-base" />
            </template>
            {{ $t('localAI.uploadPlugin') }}
          </NButton>
        </NDropdown>
        <NButton strong :loading="loading" @click="handleRefresh">
          {{ $t('common.refresh') }}
        </NButton>
      </NSpace>
      <NDivider />
      <NList hoverable clickable class="max-h-[500px] overflow-auto">
        <NListItem v-for="(plugin, index) in pluginsList" :key="index">
          <NThing class="p-2">
            <template #avatar>
              <NImage
                v-if="plugin.thumb"
                width="80"
                :src="plugin.thumb"
              />
              <NAvatar v-else :size="80" class="bg-gradient-to-r from-green-400 to-blue-500 hover:from-pink-500 hover:to-yellow-500">
                <!-- Get the first letter of the plugin -->
                <span class="text-4xl font-bold">{{ plugin.name[0] }}</span>
              </NAvatar>
            </template>
            <template #header>
              {{ `${plugin.name} - ${plugin.author_name} (v${plugin.version})` }}
            </template>
            <template #header-extra>
              <NButton circle size="small" tertiary @click="handleLink(plugin)">
                <SvgIcon icon="ph:link" class="text-base text-orange-500" />
              </NButton>
            </template>
            <template #description>
              {{ plugin.description }}
            </template>
            <template #footer>
              <NSpace>
                <NTag v-for="tag in plugin.tags.split(',')" :key="tag" type="info" size="small" :bordered="false">
                  {{ tag }}
                </NTag>
              </NSpace>
            </template>
            <template #action>
              <div v-if="plugin.id !== 'core_plugin'" class="flex flex-row justify-between pt-2">
                <div class="flex flex-row gap-4">
                  <NButton size="small" @click="handleView(plugin)">
                    {{ $t('common.view') }}
                  </NButton>
                  <NButton size="small" type="error" tertiary :disabled="disabled" @click="handleDelete(plugin)">
                    {{ $t('common.delete') }}
                  </NButton>
                </div>
                <NSwitch v-model:value="plugin.active" :disabled="disabled" @update:value="handleToggle(plugin)">
                  <template #checked>
                    {{ $t('common.enabled') }}
                  </template>
                  <template #unchecked>
                    {{ $t('common.disabled') }}
                  </template>
                </NSwitch>
              </div>
            </template>
          </NThing>
        </NListItem>
      </NList>
    </NSpin>
  </NModal>
  <UploadPluginRepo v-if="showUploadPluginRepoModal" v-model:visible="showUploadPluginRepoModal" @successed="handleUploadFromGithubSuccess" />
</template>
