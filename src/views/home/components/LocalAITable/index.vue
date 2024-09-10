<script setup lang='ts'>
import { NAvatar, NButton, NGrid, NGridItem, NPagination, NSkeleton, NSpace, NThing, NTooltip, useDialog, useMessage } from 'naive-ui'
import { computed, defineAsyncComponent, onMounted, ref, watch } from 'vue'
import { SvgIcon } from '@/components/common'
import { useAISquareStore, useAppStore, useAuthStore, useChatStore } from '@/store'
import type { KnowledgeBase } from '@/models/chat.model'
import { AiMode } from '@/models/chat.model'
import { t } from '@/locales'
import { generateSessionId } from '@/utils/functions'
import { useBasicLayout } from '@/hooks/useBasicLayout'

interface Props {
  /** 搜索关键词 */
  term: string
  category: string
}

const props = defineProps<Props>()
const UploadAIData = defineAsyncComponent(() => import('@/components/common/UploadAIData/index.vue'))
const NewLocalAI = defineAsyncComponent(() => import('@/views/home/components/NewLocalAI/index.vue'))
const aiSquareStore = useAISquareStore()
const authStore = useAuthStore()
const dialog = useDialog()
const chatStore = useChatStore()
const ms = useMessage()
const appStore = useAppStore()
const { isMobile } = useBasicLayout()

const loading = ref(false)
const knowledgeBaseList = computed(() => aiSquareStore.knowledgeBaseList)
const page = ref(1)
const total = ref(1)
const size = 15
const showUploadFileModal = ref(false)
const showEditLocalAIModal = ref(false)

async function handleUpload(item: KnowledgeBase) {
  aiSquareStore.setCurrentKnowledgeBase(item)
  showUploadFileModal.value = !showUploadFileModal.value
}

function handleDelete(item: KnowledgeBase) {
  const d = dialog.warning({
    title: t('chat.deleteKnowledgeBase'),
    content: t('chat.deleteKnowledgeBaseConfirm'),
    positiveText: t('common.yes'),
    negativeText: t('common.no'),
    onPositiveClick: async () => {
      d.loading = true
      chatStore.setSiderLoading(true)
      try {
        await aiSquareStore.removeKnowledgeBaseByKnowledgeBaseId(item.id!, AiMode.LocalAI)
        await chatStore.fetchHistory()
        refresh()
      }
      catch (error) {
        ms.error(`${error}`)
      }
      finally {
        d.loading = false
        chatStore.setSiderLoading(false)
      }
    },
  })
}

function getChatHistoryMeta(knowledge_base_id: string) {
  return chatStore.history.find(item => item.knowledge_base_id === knowledge_base_id)
}

async function handleChat(item: KnowledgeBase) {
  chatStore.setSiderLoading(true)
  loading.value = true
  try {
    const exists = getChatHistoryMeta(item.id!)
    if (exists) {
      chatStore.setActive(exists.uuid)
    }
    else {
      await chatStore.addHistory({
        title: `${item.name} - ${t('common.chat')}`,
        icon: item.icon,
        ai_mode: AiMode.LocalAI,
        uuid: generateSessionId(),
        isEdit: false,
        knowledge_base_id: item.id,
      })

      await chatStore.fetchHistory()
    }

    if (isMobile.value)
      appStore.setSiderCollapsed(true)
  }
  catch (error) {
    ms.error(`${error}`)
  }
  finally {
    chatStore.setSiderLoading(false)
    loading.value = false
  }
}

async function handlePageChange(p: number) {
  page.value = p
  await refresh()
}

async function refresh() {
  loading.value = true
  try {
    total.value = await aiSquareStore.fetchKnowledgeBaseListByPage(size, page.value)
  }
  catch (error) {
    ms.error(`${error}`)
  }
  finally {
    loading.value = false
  }
}

function handleEdit(item: KnowledgeBase) {
  aiSquareStore.setCurrentKnowledgeBase(item)
  showEditLocalAIModal.value = !showEditLocalAIModal.value
}

watch(() => props.term, async () => {
  page.value = 1
  await refresh()
})

watch(() => props.category, async () => {
  page.value = 1
  await refresh()
})

watch(() => aiSquareStore.refreshMode, (val) => {
  if (val === AiMode.LocalAI) {
    page.value = 1
    refresh()
  }

  aiSquareStore.setRefreshMode('default')
})

onMounted(async () => {
  if (authStore.session?.auth)
    return
  await refresh()
})

defineExpose({
  refresh,
})
</script>

<template>
  <NGrid
    v-if="!loading"
    x-gap="24"
    y-gap="24"
    cols="1 s:1 m:2 l:3 xl:5 2xl:5"
    responsive="screen"
  >
    <NGridItem v-for="(item, index) of knowledgeBaseList" :key="index">
      <NThing
        class="rounded-md p-4 shadow-md shadow-gray-500/30 hover:shadow-gray-500/40 gap-1"
      >
        <template #avatar>
          <NAvatar style="background-color: transparent;" :size="48" round>
            <SvgIcon :icon="item.icon" class="text-[48px]" />
          </NAvatar>
        </template>
        <template #header>
          <div class="cursor-default">
            {{ item.name }}
          </div>
        </template>
        <template v-if="item.is_global" #header-extra>
          <NTooltip trigger="hover">
            <template #trigger>
              <SvgIcon icon="uiw:global" class="text-2xl text-gray-500" />
            </template>
            {{ $t('localAI.globalKnowledgeBase') }}
          </NTooltip>
        </template>
        <div class="line-clamp-2 cursor-default">
          {{ item.description }}
        </div>
        <template #action>
          <NSpace justify="end">
            <NTooltip trigger="hover">
              <template #trigger>
                <NButton size="small" type="default" tertiary circle @click="handleUpload(item)">
                  <template #icon>
                    <SvgIcon icon="uil:upload" class="text-base" />
                  </template>
                </NButton>
              </template>
              {{ $t('common.upload') }}
            </NTooltip>
            <NTooltip trigger="hover">
              <template #trigger>
                <NButton size="small" type="default" strong circle @click="handleChat(item)">
                  <template #icon>
                    <SvgIcon icon="fluent:chat-28-regular" class="text-base" />
                  </template>
                </NButton>
              </template>
              {{ $t('common.chat') }}
            </NTooltip>
            <NTooltip trigger="hover">
              <template #trigger>
                <NButton size="small" type="default" tertiary circle @click="handleEdit(item)">
                  <template #icon>
                    <SvgIcon icon="circum:edit" class="text-base" />
                  </template>
                </NButton>
              </template>
              {{ $t('common.edit') }}
            </NTooltip>
            <NTooltip trigger="hover">
              <template #trigger>
                <NButton size="small" type="error" tertiary circle @click="handleDelete(item)">
                  <template #icon>
                    <SvgIcon icon="ep:delete-filled" class="text-base" />
                  </template>
                </NButton>
              </template>
              {{ $t('common.delete') }}
            </NTooltip>
          </NSpace>
        </template>
      </NThing>
    </NGridItem>
  </NGrid>
  <!-- 以下为骨架屏 -->
  <NGrid
    v-else
    x-gap="24"
    y-gap="24"
    cols="1 s:1 m:2 l:3 xl:5 2xl:5"
    responsive="screen"
  >
    <NGridItem v-for="(_, index) in (knowledgeBaseList.length || size)" :key="index">
      <NThing
        class="rounded-md p-4 shadow-lg shadow-gray-500/30 hover:shadow-gray-500/40 gap-2"
      >
        <template #avatar>
          <NSkeleton height="48px" width="48px" circle />
        </template>
        <template #header>
          <NSkeleton text width="48px" />
        </template>
        <NSkeleton text :repeat="2" />
        <template #action>
          <NSpace justify="end">
            <NSkeleton height="28px" width="28px" circle />
            <NSkeleton height="28px" width="28px" circle />
            <NSkeleton height="28px" width="28px" circle />
            <NSkeleton height="28px" width="28px" circle />
          </NSpace>
        </template>
      </NThing>
    </NGridItem>
  </NGrid>
  <div class="flex justify-end p-4">
    <NPagination v-model:page="page" :item-count="total" :page-sizes="[size]" size="large" @update-page="handlePageChange" />
  </div>
  <UploadAIData v-if="showUploadFileModal" v-model:visible="showUploadFileModal" />
  <NewLocalAI v-if="showEditLocalAIModal" v-model:visible="showEditLocalAIModal" mode="modify" />
</template>
