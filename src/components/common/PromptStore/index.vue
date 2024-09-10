<script setup lang='ts'>
import type { DataTableColumns } from 'naive-ui'
import { computed, h, reactive, ref, watch } from 'vue'
import { NButton, NCard, NDataTable, NDivider, NInput, NList, NListItem, NModal, NSpace, NTabPane, NTabs, NThing, useMessage } from 'naive-ui'
import PromptRecommend from '../../../assets/recommend.json'
import { SvgIcon } from '..'
import { usePromptStore } from '@/store'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { t } from '@/locales'
import type { Prompt, UpdatePrompt } from '@/models/chat.model'

interface DataProps {
  renderIcon?: string
  renderTitle?: string
  renderDescription?: string
  id?: string
  icon?: string
  title?: string
  description?: string
}

interface Props {
  visible: boolean
}

interface Emit {
  (e: 'update:visible', visible: boolean): void
}

const props = defineProps<Props>()

const emit = defineEmits<Emit>()

const ms = useMessage()
const showModal = ref(false)
const importLoading = ref(false)
const exportLoading = ref(false)

const searchValue = ref<string>('')
// 移动端自适应相关
const { isMobile } = useBasicLayout()
const promptStore = usePromptStore()

const pagination = reactive({
  page: 1,
  itemCount: 1,
  pageSize: 10,
})

const show = computed({
  get: () => props.visible,
  set: (visible: boolean) => emit('update:visible', visible),
})

async function refresh() {
  try {
    const total = await promptStore.fetchPromptListByPage(pagination.pageSize, pagination.page)
    pagination.itemCount = +total
  }
  catch (error) {
    ms.error(`${error}`)
  }
}

function handlePageChange(p: number) {
  pagination.page = p
  refresh()
}

// watch show change, if show == true, fetch
watch(show, async () => {
  if (show.value)
    await refresh()
})

// Prompt在线导入推荐List,根据部署者喜好进行修改(assets/recommend.json)
const promptRecommendList = PromptRecommend
const promptList = computed(() => promptStore.promptList)

// 用于添加修改的临时prompt参数
const tempPromptId = ref('')
const tempPromptIcon = ref('')
const tempPromptTitle = ref('')
const tempPromptDescription = ref('')
const tempPromptGreetings = ref('')
const tempPromptCategory = ref('')

// Modal模式，根据不同模式渲染不同的Modal内容
const modalMode = ref('')

// 添加修改导入都使用一个Modal, 临时修改内容占用tempPromptKey,切换状态前先将内容都清楚
function changeShowModal(mode: 'add' | 'modify' | 'local_import', selected: DataProps = { id: '', icon: '', title: '', description: '' }) {
  if (mode === 'add') {
    tempPromptId.value = ''
    tempPromptIcon.value = ''
    tempPromptTitle.value = ''
    tempPromptDescription.value = ''
  }
  else if (mode === 'modify') {
    tempPromptId.value = selected.id!
    tempPromptIcon.value = selected.icon!
    tempPromptTitle.value = selected.title!
    tempPromptDescription.value = selected.description!
  }
  else if (mode === 'local_import') {
    tempPromptId.value = ''
    tempPromptIcon.value = ''
    tempPromptTitle.value = 'local_import'
    tempPromptDescription.value = ''
  }
  showModal.value = !showModal.value
  modalMode.value = mode
}

// 在线导入相关
const downloadURL = ref('')
const downloadDisabled = computed(() => downloadURL.value.trim().length < 1)
function setDownloadURL(url: string) {
  downloadURL.value = url
}

// 控制 input 按钮
const inputStatus = computed (() => tempPromptTitle.value.trim().length < 1 || tempPromptDescription.value.trim().length < 1)

// Prompt模板相关操作
async function addPromptTemplate() {
  try {
    const newPrompt: Prompt = {
      title: tempPromptTitle.value,
      description: tempPromptDescription.value,
      icon: tempPromptIcon.value,
      greetings: tempPromptGreetings.value || 'Hi',
      category: tempPromptCategory.value,
      likes: 0,
    }
    await promptStore.createPrompt(newPrompt)

    await refresh()
    ms.success(t('common.addSuccess'))
    changeShowModal('add')
  }
  catch (error) {
    ms.error(`${error}`)
  }
}

async function modifyPromptTemplate() {
  const payload: UpdatePrompt = {
    id: tempPromptId.value,
    fields: {
      icon: tempPromptIcon.value,
      title: tempPromptTitle.value,
      description: tempPromptDescription.value,
      greetings: tempPromptGreetings.value || 'Hi',
      category: tempPromptCategory.value,
    },
  }

  await promptStore.updatePrompt(payload)
  await refresh()
  ms.success(t('common.editSuccess'))
  changeShowModal('modify')
}

async function deletePromptTemplate(row: DataProps) {
  try {
    await promptStore.deletePrompt(row.id!)
    await refresh()
    ms.success(t('common.deleteSuccess'))
  }
  catch (err) {
    ms.error(`${err}`)
  }
}

async function importPromptTemplate(from = 'online') {
  try {
    // const escapedJsonString = tempPromptDescription.value.replace(/\\/g, '\\\\')
    const jsonData = JSON.parse(tempPromptDescription.value)
    let key = ''
    let value = ''
    // 可以扩展加入更多模板字典的key
    if ('key' in jsonData[0]) {
      key = 'key'
      value = 'value'
    }
    else if ('act' in jsonData[0]) {
      key = 'act'
      value = 'prompt'
    }
    else if ('title' in jsonData[0]) {
      key = 'title'
      value = 'description'
    }
    else {
      // 不支持的字典的key防止导入 以免破坏prompt商店打开
      ms.warning('prompt key not supported.')
      throw new Error('prompt key not supported.')
    }

    const prompts: Prompt[] = []
    for (const i of jsonData)
      prompts.push({ icon: i.icon, title: i[key], description: i[value], greetings: i.greetings, category: i.category, likes: i.likes })

    await promptStore.bulkInsertPrompts(prompts)
    await refresh()
    ms.success(t('common.importSuccess'))
  }
  catch (err) {
    ms.error(`${err}`)
  }
  if (from === 'local')
    showModal.value = !showModal.value
}

// 模板导出
function exportPromptTemplate() {
  exportLoading.value = true
  const jsonDataStr = JSON.stringify(promptList.value)
  const blob = new Blob([jsonDataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'ChatGPTPromptTemplate.json'
  link.click()
  URL.revokeObjectURL(url)
  exportLoading.value = false
}

// 模板在线导入
async function downloadPromptTemplate() {
  try {
    importLoading.value = true
    const response = await fetch(downloadURL.value)
    const jsonData = await response.json()
    if ('title' in jsonData[0] && 'description' in jsonData[0])
      tempPromptDescription.value = JSON.stringify(jsonData)
    if ('act' in jsonData[0] && 'prompt' in jsonData[0]) {
      const newJsonData = jsonData.map((item: { act: string, prompt: string }) => {
        return {
          title: item.act,
          description: item.prompt,
        }
      })
      tempPromptDescription.value = JSON.stringify(newJsonData)
    }
    if ('key' in jsonData[0] && 'key' in jsonData[0]) {
      const newJsonData = jsonData.map((item: { key: string, value: string }) => {
        return {
          title: item.key,
          description: item.value,
        }
      })
      tempPromptDescription.value = JSON.stringify(newJsonData)
    }
    importPromptTemplate()
    downloadURL.value = ''
  }
  catch {
    ms.error(t('store.downloadError'))
    downloadURL.value = ''
  }
  finally {
    importLoading.value = false
  }
}

// 移动端自适应相关
function renderTemplate() {
  const [titleLimit, descriptionLimit] = isMobile.value ? [10, 30] : [15, 50]

  return promptList.value.map((item: Prompt) => {
    return {
      id: item.id,
      renderIcon: item.icon,
      renderTitle: item.title.length <= titleLimit ? item.title : `${item.title.substring(0, titleLimit)}...`,
      renderDescription: item.description.length <= descriptionLimit ? item.description : `${item.description.substring(0, descriptionLimit)}...`,
      icon: item.icon,
      title: item.title,
      description: item.description,
      greetings: item.greetings,
    }
  })
}

// table相关
function createColumns(): DataTableColumns<DataProps> {
  return [
    {
      title: t('store.icon'),
      key: 'renderIcon',
    },
    {
      title: t('store.title'),
      key: 'renderTitle',
    },
    {
      title: t('store.description'),
      key: 'renderDescription',
    },
    {
      title: t('common.action'),
      key: 'actions',
      width: 100,
      align: 'center',
      render(row) {
        return h('div', { class: 'flex items-center flex-col gap-2' }, {
          default: () => [h(
            NButton,
            {
              tertiary: true,
              size: 'small',
              type: 'info',
              onClick: () => changeShowModal('modify', row),
            },
            { default: () => t('common.edit') },
          ), h(
            NButton,
            {
              tertiary: true,
              size: 'small',
              type: 'error',
              onClick: () => deletePromptTemplate(row),
            },
            { default: () => t('common.delete') },
          )],
        })
      },
    },
  ]
}

const columns = createColumns()

const dataSource = computed(() => {
  const data = renderTemplate()
  const value = searchValue.value
  if (value && value !== '') {
    return data.filter((item: DataProps) => {
      return item.renderTitle!.includes(value) || item.renderDescription!.includes(value)
    })
  }
  return data
})
</script>

<template>
  <NModal v-model:show="show" style="width: 90%; max-width: 900px;" preset="card">
    <div class="space-y-4">
      <NTabs type="segment">
        <NTabPane name="local" :tab="$t('store.local')">
          <div
            class="flex gap-3 mb-4"
            :class="[isMobile ? 'flex-col' : 'flex-row justify-between']"
          >
            <div class="flex items-center space-x-4">
              <NButton
                type="primary"
                size="small"
                @click="changeShowModal('add')"
              >
                {{ $t('common.add') }}
              </NButton>
              <NButton
                size="small"
                @click="changeShowModal('local_import')"
              >
                {{ $t('common.import') }}
              </NButton>
              <NButton
                size="small"
                :loading="exportLoading"
                @click="exportPromptTemplate()"
              >
                {{ $t('common.export') }}
              </NButton>
              <!-- <NPopconfirm @positive-click="clearPromptTemplate">
                <template #trigger>
                  <NButton size="small">
                    {{ $t('common.clear') }}
                  </NButton>
                </template>
                {{ $t('store.clearStoreConfirm') }}
              </NPopconfirm> -->
            </div>
            <div class="flex items-center">
              <NInput v-model:value="searchValue" style="width: 100%" />
            </div>
          </div>
          <NDataTable
            v-if="!isMobile"
            remote
            :max-height="400"
            :columns="columns"
            :data="dataSource"
            :pagination="pagination"
            :bordered="false"
            @update:page="handlePageChange"
          />
          <NList v-if="isMobile" style="max-height: 400px; overflow-y: auto;">
            <NListItem v-for="(item, index) of dataSource" :key="index">
              <NThing :title="item.renderTitle" :description="item.renderDescription" />
              <template #suffix>
                <div class="flex flex-col items-center gap-2">
                  <NButton tertiary size="small" type="info" @click="changeShowModal('modify', item)">
                    {{ $t('common.edit') }}
                  </NButton>
                  <NButton tertiary size="small" type="error" @click="deletePromptTemplate(item)">
                    {{ $t('common.delete') }}
                  </NButton>
                </div>
              </template>
            </NListItem>
          </NList>
        </NTabPane>
        <NTabPane name="download" :tab="$t('store.online')">
          <p class="mb-4">
            {{ $t('store.onlineImportWarning') }}
          </p>
          <div class="flex items-center gap-4">
            <NInput v-model:value="downloadURL" placeholder="" />
            <NButton
              strong
              secondary
              :disabled="downloadDisabled"
              :loading="importLoading"
              @click="downloadPromptTemplate()"
            >
              {{ $t('common.download') }}
            </NButton>
          </div>
          <NDivider />
          <div class="max-h-[360px] overflow-y-auto space-y-4">
            <NCard
              v-for="info in promptRecommendList"
              :key="info.key" :title="info.key"
              :bordered="true"
              embedded
            >
              <p
                class="overflow-hidden text-ellipsis whitespace-nowrap"
                :title="info.desc"
              >
                {{ info.desc }}
              </p>
              <template #footer>
                <div class="flex items-center justify-end space-x-4">
                  <NButton text>
                    <a
                      :href="info.url"
                      target="_blank"
                    >
                      <SvgIcon class="text-xl" icon="ri:link" />
                    </a>
                  </NButton>
                  <NButton text @click="setDownloadURL(info.downloadUrl) ">
                    <SvgIcon class="text-xl" icon="ri:add-fill" />
                  </NButton>
                </div>
              </template>
            </NCard>
          </div>
        </NTabPane>
      </NTabs>
    </div>
  </NModal>

  <NModal v-model:show="showModal" style="width: 90%; max-width: 600px;" preset="card">
    <NSpace v-if="modalMode === 'add' || modalMode === 'modify'" vertical>
      {{ $t('store.icon') }}
      <NInput v-model:value="tempPromptIcon" />
      {{ $t('store.title') }}
      <NInput v-model:value="tempPromptTitle" />
      {{ $t('store.description') }}
      <NInput v-model:value="tempPromptDescription" type="textarea" />
      {{ $t('store.greetings') }}
      <NInput v-model:value="tempPromptGreetings" type="textarea" />
      {{ $t('store.category') }}
      <NInput v-model:value="tempPromptCategory" type="textarea" />
      <NButton
        block
        type="primary"
        :disabled="inputStatus"
        @click="() => { modalMode === 'add' ? addPromptTemplate() : modifyPromptTemplate() }"
      >
        {{ $t('common.confirm') }}
      </NButton>
    </NSpace>
    <NSpace v-if="modalMode === 'local_import'" vertical>
      <NInput
        v-model:value="tempPromptDescription"
        :placeholder="t('store.importPlaceholder')"
        :autosize="{ minRows: 3, maxRows: 15 }"
        type="textarea"
      />
      <NButton
        block
        type="primary"
        :disabled="inputStatus"
        @click="() => { importPromptTemplate('local') }"
      >
        {{ $t('common.import') }}
      </NButton>
    </NSpace>
  </NModal>
</template>
