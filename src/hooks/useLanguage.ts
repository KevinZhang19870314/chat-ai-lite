import { computed } from 'vue'
import { enUS, jaJP, zhCN } from 'naive-ui'
import * as dayjs from 'dayjs'
import { useAppStore } from '@/store'
import { setLocale } from '@/locales'

export function useLanguage() {
  const appStore = useAppStore()

  const language = computed(() => {
    switch (appStore.language) {
      case 'en-US':
        setLocale('en-US')
        dayjs.locale('en')
        return enUS
      case 'zh-CN':
        setLocale('zh-CN')
        dayjs.locale('zh-cn')
        return zhCN
      case 'ja-JP':
        setLocale('ja-JP')
        dayjs.locale('ja')
        return jaJP
      default:
        setLocale('zh-CN')
        dayjs.locale('zh-cn')
        return zhCN
    }
  })

  return { language }
}
