<script lang="ts" setup>
import { computed, h, onMounted, reactive, ref } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { NButton, NDataTable, NDivider, NEllipsis, NInput, NSelect, NSpace, useDialog, useMessage } from 'naive-ui'

import { useBasicLayout } from '@/hooks/useBasicLayout'
import { useAppStore, usePromptStore } from '@/store'
import { t } from '@/locales'
import type { Prompt } from '@/models/chat.model'
import { SvgIcon } from '@/components/common'
import { AIAssistantCategories } from '@/utils/constants'
import AddAIAssistant from '@/views/admin/components/AddAIAssistant.vue'

const appStore = useAppStore()
const promptStore = usePromptStore()
const dialog = useDialog()
const ms = useMessage()
const { isMobile } = useBasicLayout()
const collapsed = computed(() => appStore.siderCollapsed)
const loading = ref(false)
const searchValue = ref<string>('')
const showAddAIAssistantModal = ref(false)
const addAIAssistantMode = ref<'add' | 'modify'>('add')
const currentAIAssistant = ref<Prompt | undefined>()
const category = ref('all')
const categoryOptions: { label: string, key: string, value: string }[] = AIAssistantCategories.map(item => ({
  label: t(item.titleI18n),
  key: item.category,
  value: item.category,
}))
const status = ref(-1)
const statusOptions = [
  { label: t('common.all'), key: -1, value: -1 },
  { label: t('common.enabled'), key: 1, value: 1 },
  { label: t('common.disabled'), key: 0, value: 0 },
]

const promptList = computed(() => promptStore.promptList)
const pagination = reactive({
  page: 1,
  itemCount: 1,
  pageSize: 10,
})
function createColumns(): DataTableColumns<Prompt> {
  return [
    {
      title: t('store.roleIcon'),
      key: 'icon',
      align: 'left',
      width: 150,
      render(row) {
        return h(SvgIcon, {
          icon: row.icon,
          class: 'text-4xl',
        })
      },
    },
    {
      title: t('store.roleTitle'),
      key: 'title',
      align: 'left',
      width: 200,
    },
    {
      title: t('store.roleDescription'),
      key: 'description',
      align: 'left',
      render(row) {
        return h(
          NEllipsis,
          {
            style: {
              maxWidth: '200px',
            },
            tooltip: false,
            lineClamp: 2,
            expandTrigger: 'click',
          },
          {
            default: () => `${row.description}`,
          },
        )
      },
    },
    {
      title: t('store.greetings'),
      key: 'greetings',
      align: 'left',
      render(row) {
        return h(
          NEllipsis,
          {
            style: {
              maxWidth: '200px',
            },
            tooltip: false,
            lineClamp: 2,
            expandTrigger: 'click',
          },
          {
            default: () => `${row.greetings}`,
          },
        )
      },
    },
    {
      title: t('store.roleType'),
      key: 'category',
      align: 'left',
      render(row) {
        return h(
          'span',
          {},
          {
            default: () => t(AIAssistantCategories.find(item => item.category === row.category)?.titleI18n || ''),
          },
        )
      },
    },
    {
      title: t('common.action'),
      key: 'actions',
      width: 140,
      align: 'center',
      render(row) {
        return h('div', { class: 'flex items-center flex-row gap-2' }, {
          default: () => [
            h(
              NButton,
              {
                tertiary: true,
                strong: false,
                size: 'small',
                type: 'default',
                onClick: () => handleEditAIAssistant(row),
              },
              { default: () => t('common.edit') },
            ),
            row.is_enabled && h(
              NButton,
              {
                tertiary: true,
                strong: false,
                size: 'small',
                type: 'error',
                onClick: () => toggleAIAssistant(row),
              },
              { default: () => t('common.disabled') },
            ),
            !row.is_enabled && h(
              NButton,
              {
                tertiary: true,
                strong: false,
                size: 'small',
                type: 'primary',
                onClick: () => toggleAIAssistant(row),
              },
              { default: () => t('common.enabled') },
            ),
          ],
        })
      },
    },
  ]
}
const columns = createColumns()
function renderTemplate() {
  return promptList.value.map((item: any) => {
    return item
  })
}
const dataSource = computed(() => {
  const data = renderTemplate()
  return data
})

function handleUpdateCategory(value: string) {
  category.value = value
  refresh()
}

function handleUpdateStatus(value: number) {
  status.value = value
  refresh()
}

function handleAddAIAssistant() {
  addAIAssistantMode.value = 'add'
  currentAIAssistant.value = undefined
  showAddAIAssistantModal.value = !showAddAIAssistantModal.value
}

function handleEditAIAssistant(row: Prompt) {
  addAIAssistantMode.value = 'modify'
  currentAIAssistant.value = row
  showAddAIAssistantModal.value = !showAddAIAssistantModal.value
}

function toggleAIAssistant(row: Prompt) {
  const d = dialog.warning({
    title: t('admin.toggleAIAssistant'),
    content: `${row.is_enabled ? t('common.disabled') : t('common.enabled')} 【${row.title}】?`,
    positiveText: t('common.yes'),
    negativeText: t('common.no'),
    onPositiveClick: async () => {
      d.loading = true
      try {
        await promptStore.togglePrompt(row.id!, !row.is_enabled)
        refresh()
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

async function refresh() {
  loading.value = true
  try {
    const total = await promptStore.fetchPromptListByPage(pagination.pageSize, pagination.page, category.value, status.value, searchValue.value)
    pagination.itemCount = +total
  }
  catch (error) {
    ms.error(`${error}`)
  }
  finally {
    loading.value = false
  }
}

function handlePageChange(p: number) {
  pagination.page = p
  refresh()
}

function handleSearch() {
  refresh()
}

onMounted(() => {
  refresh()
})
</script>

<template>
  <div class="max-w-screen-2xl flex flex-col justify-center m-auto overflow-auto" :class="[isMobile ? 'p-2' : 'p-4', collapsed ? 'pl-[80px]' : 'p-4']">
    <NSpace justify="start" align="center" class="pb-4 w-full mt-4">
      <NInput v-model:value="searchValue" style="width: 320px;" autofocus :placeholder="$t('common.search')" @keyup.enter="handleSearch" />
      <NButton type="primary" @click="handleSearch">
        <SvgIcon class="text-xl" icon="ic:sharp-search" />
        {{ $t('common.search') }}
      </NButton>
      <NDivider vertical />
      <div class="flex items-center gap-4">
        <span>{{ $t('store.category') }}</span>
        <NSelect
          style="width: 140px"
          :value="category"
          :options="categoryOptions"
          @update-value="handleUpdateCategory"
        />
      </div>
      <div class="flex items-center gap-4">
        <span>{{ $t('common.status') }}</span>
        <NSelect
          style="width: 140px"
          :value="status"
          :options="statusOptions"
          @update-value="handleUpdateStatus"
        />
      </div>
      <NDivider vertical />
      <NButton type="primary" strong @click="handleAddAIAssistant">
        {{ $t('admin.newAIAssistant') }}
      </NButton>
    </NSpace>
    <div class="min-h-[100px]">
      <NDataTable
        remote
        :loading="loading"
        :max-height="680"
        :columns="columns"
        :data="dataSource"
        :pagination="pagination"
        @update:page="handlePageChange"
      />
    </div>
  </div>
  <template v-if="showAddAIAssistantModal">
    <AddAIAssistant v-model:show="showAddAIAssistantModal" :mode="addAIAssistantMode" :data="currentAIAssistant" @success="refresh" />
  </template>
</template>

<style lang="less" scoped>

</style>
