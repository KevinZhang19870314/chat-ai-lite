<script lang="ts" setup>
import { ref } from 'vue'
import { NButton, NInput, NInputNumber, NSlider, NTooltip, useMessage } from 'naive-ui'
import { useSettingStore } from '@/store'
import { t } from '@/locales'
import { SvgIcon } from '@/components/common'

const settingStore = useSettingStore()

const ms = useMessage()

const systemMessage = ref(settingStore.systemMessage ?? '')

const temperature = ref(settingStore.temperature ?? 0.5)

const top_p = ref(settingStore.top_p ?? 1)

const max_tokens = ref(settingStore.max_tokens ?? 1024)

const presence_penalty = ref(settingStore.presence_penalty ?? 0)

const frequency_penalty = ref(settingStore.frequency_penalty ?? 0)

const historyCount = ref(settingStore.historyCount ?? 8)

function handleReset() {
  settingStore.resetSetting()
  ms.success(t('common.success'))
  window.location.reload()
}

function handleSave() {
  settingStore.updateSetting(
    {
      systemMessage: systemMessage.value,
      temperature: temperature.value,
      top_p: top_p.value,
      max_tokens: max_tokens.value,
      presence_penalty: presence_penalty.value,
      frequency_penalty: frequency_penalty.value,
      historyCount: historyCount.value,
    },
  )
  ms.success(t('common.success'))
  window.location.reload()
}
</script>

<template>
  <div class="p-4 space-y-5 min-h-[200px]">
    <div class="space-y-6">
      <div class="flex items-center space-x-4">
        <span class="w-[120px]">{{ $t('setting.systemPromptMessage') }}</span>
        <div class="flex-1">
          <NInput v-model:value="systemMessage" type="textarea" :autosize="{ minRows: 1, maxRows: 4 }" />
        </div>
      </div>
      <div class="flex items-center space-x-4">
        <span class="w-[120px] flex items-center">
          <span class="mr-1">{{ $t('setting.temperature') }}</span>
          <NTooltip trigger="hover" class="max-w-xs">
            <template #trigger>
              <SvgIcon icon="ph:question-fill" class="text-xl cursor-pointer text-orange-500" />
            </template>
            {{ $t('setting.temperatureTip') }}
          </NTooltip>
        </span>
        <div class="flex-1">
          <NSlider v-model:value="temperature" :max="1" :min="0" :step="0.1" />
        </div>
        <span>{{ temperature }}</span>
      </div>
      <div class="flex items-center space-x-4">
        <span class="w-[120px] flex items-center">
          <span class="mr-1">{{ $t('setting.top_p') }}</span>
          <NTooltip trigger="hover" class="max-w-xs">
            <template #trigger>
              <SvgIcon icon="ph:question-fill" class="text-xl cursor-pointer text-orange-500" />
            </template>
            {{ $t('setting.top_pTip') }}
          </NTooltip>
        </span>
        <div class="flex-1">
          <NSlider v-model:value="top_p" :max="1" :min="0" :step="0.1" />
        </div>
        <span>{{ top_p }}</span>
      </div>
      <div class="flex items-center space-x-4">
        <span class="w-[120px] flex items-center">
          <span class="mr-1">{{ $t('setting.maxTokens') }}</span>
          <NTooltip trigger="hover" class="max-w-xs">
            <template #trigger>
              <SvgIcon icon="ph:question-fill" class="text-xl cursor-pointer text-orange-500" />
            </template>
            {{ $t('setting.maxTokensTip') }}
          </NTooltip>
        </span>
        <div class="flex-1">
          <NInputNumber v-model:value="max_tokens" :show-button="false" :min="1" :max="8192" />
        </div>
      </div>
      <div class="flex items-center space-x-4">
        <span class="w-[120px] flex items-center">
          <span class="mr-1">{{ $t('setting.presencePenalty') }}</span>
          <NTooltip trigger="hover" class="max-w-xs">
            <template #trigger>
              <SvgIcon icon="ph:question-fill" class="text-xl cursor-pointer text-orange-500" />
            </template>
            {{ $t('setting.presencePenaltyTip') }}
          </NTooltip>
        </span>
        <div class="flex-1">
          <NSlider v-model:value="presence_penalty" :max="2" :min="-2" :step="0.1" />
        </div>
        <span>{{ presence_penalty }}</span>
      </div>
      <div class="flex items-center space-x-4">
        <span class="w-[120px] flex items-center">
          <span class="mr-1">{{ $t('setting.frequencyPenalty') }}</span>
          <NTooltip trigger="hover" class="max-w-xs">
            <template #trigger>
              <SvgIcon icon="ph:question-fill" class="text-xl cursor-pointer text-orange-500" />
            </template>
            {{ $t('setting.frequencyPenaltyTip') }}
          </NTooltip>
        </span>
        <div class="flex-1">
          <NSlider v-model:value="frequency_penalty" :max="2" :min="-2" :step="0.1" />
        </div>
        <span>{{ frequency_penalty }}</span>
      </div>
      <div class="flex items-center space-x-4">
        <span class="w-[120px] flex items-center">
          <span class="mr-1">{{ $t('setting.historyCount') }}</span>
          <NTooltip trigger="hover" class="max-w-xs">
            <template #trigger>
              <SvgIcon icon="ph:question-fill" class="text-xl cursor-pointer text-orange-500" />
            </template>
            {{ $t('setting.historyCountTip') }}
          </NTooltip>
        </span>
        <div class="flex-1">
          <NSlider v-model:value="historyCount" :max="100" :min="0" :step="1" />
        </div>
        <span>{{ historyCount }}</span>
      </div>

      <div class="flex justify-end items-center gap-4">
        <NButton size="small" @click="handleReset">
          {{ $t('common.reset') }}
        </NButton>
        <NButton size="small" type="primary" @click="handleSave">
          {{ $t('common.save') }}
        </NButton>
      </div>
    </div>
  </div>
</template>
