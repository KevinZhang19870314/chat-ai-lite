<script setup lang='ts'>
import { computed } from 'vue'
import { NLayout, NLayoutContent, useLoadingBar } from 'naive-ui'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { router } from '@/router'

const { isMobile } = useBasicLayout()

const getContainerClass = computed(() => {
  return [
    'h-full',
  ]
})

const loadingBar = useLoadingBar()

router.beforeEach(() => {
  loadingBar.start()
})

router.afterEach(() => {
  loadingBar.finish()
})
</script>

<template>
  <div class="h-full dark:bg-[#24272e] transition-all">
    <div class="h-full overflow-hidden">
      <NLayout class="z-40 transition" :class="getContainerClass" has-sider>
        <NLayoutContent class="h-full" :class="isMobile ? 'ml-[60px]' : ''">
          <RouterView v-slot="{ Component, route }">
            <component :is="Component" :key="route.fullPath" />
          </RouterView>
        </NLayoutContent>
      </NLayout>
    </div>
  </div>
</template>
