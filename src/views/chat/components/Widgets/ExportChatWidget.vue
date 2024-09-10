<script lang="ts" setup>
import { useDialog, useMessage } from 'naive-ui'
import html2canvas from 'html2canvas'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { t } from '@/locales'
import { HoverButton, SvgIcon } from '@/components/common'

interface Props {
  loading: boolean
  show: boolean
}

const props = defineProps<Props>()

const ms = useMessage()
const dialog = useDialog()
const { isMobile } = useBasicLayout()

function handleExport() {
  if (props.loading)
    return

  const d = dialog.warning({
    title: t('chat.exportImage'),
    content: t('chat.exportImageConfirm'),
    positiveText: t('common.yes'),
    negativeText: t('common.no'),
    onPositiveClick: async () => {
      try {
        d.loading = true
        const ele = document.getElementById('image-wrapper')
        const canvas = await html2canvas(ele as HTMLDivElement, {
          useCORS: true,
        })
        const imgUrl = canvas.toDataURL('image/png')
        const tempLink = document.createElement('a')
        tempLink.style.display = 'none'
        tempLink.href = imgUrl
        tempLink.setAttribute('download', 'chat-shot.png')
        if (typeof tempLink.download === 'undefined')
          tempLink.setAttribute('target', '_blank')

        document.body.appendChild(tempLink)
        tempLink.click()
        document.body.removeChild(tempLink)
        window.URL.revokeObjectURL(imgUrl)
        d.loading = false
        ms.success(t('chat.exportSuccess'))
        Promise.resolve()
      }
      catch (error: any) {
        ms.error(t('chat.exportFailed'))
      }
      finally {
        d.loading = false
      }
    },
  })
}
</script>

<template>
  <HoverButton v-if="show" :tooltip="isMobile ? '' : t('chat.exportImage')" @click="handleExport">
    <span class="text-xl text-[#4f555e] dark:text-white">
      <SvgIcon icon="ri:download-2-line" />
    </span>
  </HoverButton>
</template>
