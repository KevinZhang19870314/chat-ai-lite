<script lang="ts" setup>
import { NCard, NGrid, NGridItem, NModal, NSpace, useMessage } from 'naive-ui'
import { ref } from 'vue'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import questions from '@/assets/questions.json'
import { SvgIcon } from '@/components/common'
import { useAppStore, useChatStore } from '@/store'
import { AiMode } from '@/models/chat.model'
import { generateSessionId } from '@/utils/functions'
import Advanced from '@/components/common/Setting/Advanced.vue'
import { t } from '@/locales'

export type Question = typeof questions[0]

const appStore = useAppStore()
const chatStore = useChatStore()
const ms = useMessage()
const showModal = ref(false)
const { isMobile } = useBasicLayout()

const items = questions.filter((item: Question) => !item.top)
const top1: Question = questions.find((item: Question) => item.top === 1)!
const top2: Question = questions.find((item: Question) => item.top === 2)!
const top3: Question = questions.find((item: Question) => item.top === 3)!
const randomCount = 6

chatStore.setAIMode(AiMode.ChatLLM)

function getRandomItems(list: Question[], count: number) {
  const shuffled = list.sort(() => 0.5 - Math.random())
  return shuffled.slice(0, count)
}

const questionsList = ref<Question[]>([top1, top2, top3])
questionsList.value = [...questionsList.value, ...getRandomItems(items, randomCount)]

function handleRefresh() {
  questionsList.value = [top1, top2, top3, ...getRandomItems(items, randomCount)]
}

// function handleSettings() {
//   showModal.value = !showModal.value
// }

async function handleChat(question: Question) {
  chatStore.setSiderLoading(true)
  try {
    await chatStore.addHistory({
      title: question.desc.substring(0, 20),
      icon: 'ri:message-3-line',
      ai_mode: AiMode.ChatLLM,
      uuid: generateSessionId(),
      isEdit: false,
    })
    if (isMobile.value)
      appStore.setSiderCollapsed(true)

    await chatStore.fetchHistory()
    chatStore.setPrompt(question.desc)
  }
  catch (error) {
    ms.error(`${error}`)
  }
  finally {
    chatStore.setSiderLoading(false)
  }
}

function genSayHi() {
  const currentHour = new Date().getHours()
  let greeting

  if (currentHour < 12)
    greeting = t('common.goodMorning')
  else if (currentHour < 18)
    greeting = t('common.goodAfternoon')
  else
    greeting = t('common.goodEvening')

  return greeting
}
</script>

<template>
  <div class="max-w-screen-lg flex flex-col justify-center items-center m-auto" :class="[isMobile ? 'p-2' : 'p-4']">
    <NSpace class="py-4 w-full" vertical>
      <div class="text-4xl py-2 pb-4 font-extrabold">
        👋
        <span class="ml-2">{{ genSayHi() }}</span>
      </div>
      <div class="text-xl pb-8 font-semibold">
        {{ $t('chat.chatGPTIntro') }}
      </div>
      <div class="flex justify-between">
        <span>{{ $t('chat.tryAsk') }}</span>
        <div class="flex gap-4 items-center">
          <div class="flex items-center cursor-pointer hover:text-orange-500" @click="handleRefresh">
            <SvgIcon icon="material-symbols:refresh" class="text-xl" />
            <span>{{ $t('chat.exchange') }}</span>
          </div>
          <!-- <div class="flex items-center cursor-pointer hover:text-orange-500" @click="handleSettings">
            <SvgIcon icon="ri:list-settings-fill" class="text-xl" />
            <span>{{ $t('setting.chatGPTParameterSettings') }}</span>
          </div> -->
        </div>
      </div>
    </NSpace>
    <NGrid
      x-gap="24"
      y-gap="24"
      cols="1 s:1 m:1 l:3 xl:3 2xl:3"
      responsive="screen"
    >
      <NGridItem v-for="(item, index) of questionsList" :key="index" @click="handleChat(item)">
        <NCard class="cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800" hoverable>
          <template #header>
            <div class="flex items-center">
              <SvgIcon v-if="[1, 2, 3].indexOf(+item.top!) > -1" icon="mdi:hot" class="text-xl text-red-500" />
              {{ item.category }}
            </div>
          </template>
          <div class="line-clamp-2 mb-4">
            {{ item.desc }}
          </div>
          <div class="absolute bottom-1 right-1">
            <SvgIcon icon="majesticons:arrow-right" class="text-2xl text-gray-500" />
          </div>
        </NCard>
      </NGridItem>
    </NGrid>
  </div>
  <NModal v-model:show="showModal" :title="$t('setting.chatGPTSettings')" preset="card" style="max-width: 640px">
    <div>
      <Advanced />
    </div>
  </NModal>
</template>
