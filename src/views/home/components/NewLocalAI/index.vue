<script setup lang="ts">
import type { VNodeChild } from 'vue'
import { computed, h, onMounted, ref, watch } from 'vue'

import type { SelectOption } from 'naive-ui'
import { NAvatar, NButton, NCheckbox, NImage, NInput, NModal, NSelect, NSpace, NSpin, useMessage } from 'naive-ui'

import { ICONS } from './icons'
import { t } from '@/locales'
import { useAISquareStore, useUserStore } from '@/store'
import type { AvailablePlugin, KnowledgeBase } from '@/models/chat.model'
import { AiMode } from '@/models/chat.model'
import SvgIcon from '@/components/common/SvgIcon/index.vue'

interface Props {
  visible: boolean
  mode: 'add' | 'modify'
}

interface Emit {
  (ev: 'update:visible', visible: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emit>()

const ms = useMessage()
const aiSquareStore = useAISquareStore()
const userStore = useUserStore()
const currentKnowledgeBase = computed(() => aiSquareStore.currentKnowledgeBase)

const loading = ref(false)

const showModal = computed({
  get() {
    return props.visible
  },
  set(value) {
    emit('update:visible', value)
  },
})

const defaultIcon = ICONS[0]
let knowledgeBase = ref<KnowledgeBase>({
  id: '',
  user_id: '',
  name: '',
  icon: defaultIcon,
  description: '',
  is_global: false,
  use_plugins: '',
  type: AiMode.LocalAI,
})

// define a usePlugins with computed getter and setter
const usePlugins = computed({
  get() {
    if (knowledgeBase && knowledgeBase.value && knowledgeBase.value.use_plugins)
      return knowledgeBase.value.use_plugins.split(',')

    return []
  },
  set(value: string[]) {
    if (value.length > 0)
      knowledgeBase.value.use_plugins = value.join(',')
    else
      knowledgeBase.value.use_plugins = ''
  },
})

const options: Array<SelectOption> = []
ICONS.forEach((icon: string) => {
  options.push({
    value: `${icon}`,
    label: '',
  })
})

const pluginsOptions = ref<Array<SelectOption>>([])

function renderIconLabel(option: SelectOption): VNodeChild {
  return [
    h(
      SvgIcon,
      {
        icon: `${option.value}`,
        class: 'text-xl',
      },
      {
        default: () => h('请选择'),
      },
    ),
  ]
}

watch(
  () => currentKnowledgeBase,
  () => {
    if (props.mode === 'modify') {
      if (currentKnowledgeBase.value) {
        knowledgeBase = ref<KnowledgeBase>({
          id: `${currentKnowledgeBase.value.id}`,
          name: `${currentKnowledgeBase.value.name}`,
          icon: `${currentKnowledgeBase.value.icon}`,
          description: `${currentKnowledgeBase.value.description}`,
          is_global: currentKnowledgeBase.value.is_global,
          user_id: `${currentKnowledgeBase.value.user_id}`,
          use_plugins: `${currentKnowledgeBase.value.use_plugins ? currentKnowledgeBase.value.use_plugins : ''}`,
          type: AiMode.LocalAI,
        })
      }
      else {
        knowledgeBase = ref<KnowledgeBase>({
          id: '',
          name: '',
          icon: defaultIcon,
          description: '',
          is_global: false,
          user_id: '',
          use_plugins: '',
          type: AiMode.LocalAI,
        })
      }
    }
  },
  {
    deep: true,
    immediate: true,
    flush: 'post',
  },
)

const disabled = computed(() => {
  return knowledgeBase.value.name.trim().length < 1
    || knowledgeBase.value.icon.trim().length < 1
    || knowledgeBase.value.description!.trim().length < 20
},
)

async function add() {
  loading.value = true
  try {
    await aiSquareStore.addKnowledgeBase(knowledgeBase.value)
    ms.success(`${t('common.addSuccess')}`)
    showModal.value = false
    reset()
    aiSquareStore.setCurrentKnowledgeBaseTab(AiMode.LocalAI)
    aiSquareStore.setRefreshMode(AiMode.LocalAI)
  }
  catch (error: any) {
    ms.error(`${error}`)
  }
  finally {
    loading.value = false
  }
}

async function modify() {
  loading.value = true
  try {
    await aiSquareStore.updateKnowledgeBase(knowledgeBase.value)
    ms.success(`${t('common.editSuccess')}`)
    showModal.value = false
    reset()
    aiSquareStore.setCurrentKnowledgeBaseTab(AiMode.LocalAI)
    aiSquareStore.setRefreshMode(AiMode.LocalAI)
  }
  catch (error) {
    ms.error(`${error}`)
  }
  finally {
    loading.value = false
  }
}

function reset() {
  knowledgeBase.value.id = ''
  knowledgeBase.value.user_id = ''
  knowledgeBase.value.name = ''
  knowledgeBase.value.description = ''
  knowledgeBase.value.icon = defaultIcon
  knowledgeBase.value.is_global = false
  knowledgeBase.value.use_plugins = ''
  knowledgeBase.value.type = AiMode.LocalAI
}

function renderPluginsLabel(option: SelectOption): VNodeChild {
  return [
    h('div', {
      class: 'flex items-center gap-2',
    }, {
      default: () => [
        option.thumb
          ? h(
            NImage,
            {
              width: '15',
              src: `${option.thumb}`,
            },
          )
          : h(
            NAvatar,
            {
              size: 15,
              class: 'bg-gradient-to-r from-green-400 to-blue-500 hover:from-pink-500 hover:to-yellow-500',
            },
            {
              default: () => [
                h(
                  'span',
                  {
                    class: 'text-base font-bold',
                  },
                  {
                    default: () => `${option.label}`.substring(0, 1).toUpperCase(),
                  },
                ),
              ],
            },
          ),
        option.label as string,
      ],
    }),
  ]
}

onMounted(async () => {
  try {
    await aiSquareStore.fetchActivePlugins()
    if (aiSquareStore.activePluginsList!.length > 0) {
      aiSquareStore.activePluginsList!.forEach((item: AvailablePlugin) => {
        pluginsOptions.value.push({
          value: item.id,
          label: item.name,
          thumb: item.thumb,
        })
      })
    }
  }
  catch (error) {
    ms.error(`${error}`)
  }
})
</script>

<template>
  <NModal v-model:show="showModal" :title="props.mode === 'add' ? $t('chat.newLocalAI') : `${currentKnowledgeBase?.name}`" style="max-width: 640px;" preset="card">
    <NSpin :show="loading">
      <NSpace vertical>
        {{ $t('store.icon') }}
        <NSelect
          v-model:value="knowledgeBase.icon" :options="options" :render-label="renderIconLabel"
          style="width: 50%;"
        />
        {{ $t('localAI.name') }}
        <NInput v-model:value="knowledgeBase.name" />
        {{ $t('localAI.description') }}
        <NInput v-model:value="knowledgeBase.description" type="textarea" minlength="20" maxlength="200" show-count />
        {{ $t('localAI.usePlugins') }}
        <NSelect
          v-model:value="usePlugins" multiple :options="pluginsOptions" max-tag-count="responsive"
          :render-label="renderPluginsLabel"
        />
        <NCheckbox v-if="userStore.isAdminAndAbove" v-model:checked="knowledgeBase.is_global">
          {{ $t('localAI.isGlobal') }}
        </NCheckbox>
        <NButton block type="primary" :disabled="disabled" @click="() => { props.mode === 'add' ? add() : modify() }">
          {{ $t('common.confirm') }}
        </NButton>
      </NSpace>
    </NSpin>
  </NModal>
</template>
