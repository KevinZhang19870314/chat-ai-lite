<script setup lang='ts'>
import { computed, defineAsyncComponent, ref } from 'vue'
import { HoverButton, SvgIcon, UserAvatar } from '@/components/common'
import { useAppStore, useUserStore } from '@/store'

const Setting = defineAsyncComponent(() => import('@/components/common/Setting/index.vue'))
const appStore = useAppStore()
const userStore = useUserStore()

const collapsed = computed(() => appStore.siderCollapsed)
const show = ref(false)
</script>

<template>
  <footer class="flex items-center justify-between min-w-0 overflow-hidden border-t dark:border-neutral-800" :class="[collapsed ? 'p-2' : 'p-4']">
    <div class="flex-1 flex-shrink-0 overflow-hidden">
      <UserAvatar />
    </div>

    <HoverButton v-if="!collapsed && userStore.isSuperAdmin" @click="show = true">
      <span class="text-xl text-[#4f555e] dark:text-white">
        <SvgIcon icon="ri:settings-4-line" />
      </span>
    </HoverButton>

    <Setting v-if="show" v-model:visible="show" />
  </footer>
</template>
