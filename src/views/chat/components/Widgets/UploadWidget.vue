<script lang="ts" setup>
import { defineAsyncComponent, ref } from 'vue'
import { HoverButton, SvgIcon } from '@/components/common'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { t } from '@/locales'

const UploadAIData = defineAsyncComponent(() => import('@/components/common/UploadAIData/index.vue'))

const { isMobile } = useBasicLayout()

const show = ref(false)

function handleUploadCommonAIData() {
  show.value = !show.value
}
</script>

<template>
  <HoverButton v-if="!isMobile" :tooltip="t('chat.uploadCommonAIData')" @click="handleUploadCommonAIData">
    <span class="text-xl text-[#4f555e] dark:text-white">
      <SvgIcon icon="ri:upload-2-line" />
    </span>
  </HoverButton>
  <UploadAIData v-if="show" v-model:visible="show" />
</template>
