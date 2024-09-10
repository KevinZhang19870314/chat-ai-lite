<script lang="ts" setup>
import { useDialog } from 'naive-ui'
import { HoverButton, SvgIcon } from '@/components/common'
import { t } from '@/locales'
import { useChatStore } from '@/store'

interface Props {
  loading: boolean
  uuid: string
}

const props = defineProps<Props>()

const chatStore = useChatStore()
const dialog = useDialog()

function handleClear() {
  if (props.loading)
    return

  dialog.warning({
    title: t('chat.clearChat'),
    content: t('chat.clearChatConfirm'),
    positiveText: t('common.yes'),
    negativeText: t('common.no'),
    onPositiveClick: () => {
      chatStore.clearChatByUuid(+props.uuid)
    },
  })
}
</script>

<template>
  <HoverButton :tooltip="t('chat.clearChat')" @click="handleClear">
    <span class="text-xl text-[#4f555e] dark:text-white">
      <SvgIcon icon="ri:delete-bin-line" />
    </span>
  </HoverButton>
</template>
