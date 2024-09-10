<script lang="ts" setup>
import { computed, ref } from 'vue'
import { NPopover } from 'naive-ui'
import { useAIMode } from '../../hooks/useAIMode'
import { SvgIcon } from '@/components/common'
import type { AiMode } from '@/models/chat.model'
import { useAppStore } from '@/store'

interface Props {
  mode: AiMode
  icon: string
  bgColor: string
  tooltip: string
}

interface Emit {
  (ev: 'selected'): void
}

const props = withDefaults(defineProps<Props>(), {
  bgColor: 'greenyellow',
})
const emit = defineEmits<Emit>()

const isHover = ref(false)
const appStore = useAppStore()
const isDark = computed(() => appStore.theme === 'dark')

const { aiMode } = useAIMode()

const selected = computed(() => {
  return aiMode.value === props.mode
})

function toggleSelected() {
  emit('selected')
}
</script>

<template>
  <NPopover trigger="hover" placement="right">
    <template #trigger>
      <div
        class="rounded-lg w-[46px] h-[46px] flex justify-center items-center bg-transparent"
        :class="isDark ? 'text-neutral-300' : 'text-neutral-500'"
        :style="{ color: selected || isHover ? `${props.bgColor}` : '' }"
        @click="toggleSelected"
        @mouseover="isHover = true"
        @mouseleave="isHover = false"
      >
        <div
          class="p-2.5 rounded-lg flex justify-center items-center cursor-pointer"
        >
          <span
            class="flex items-center justify-center inner-span"
          >
            <SvgIcon :icon="props.icon" />
          </span>
        </div>
      </div>
    </template>
    <span>{{ props.tooltip }}</span>
  </NPopover>
</template>

<style scoped lang="less">
.inner-span>svg {
  width: 32px;
  height: 32px;
}
.border-3 {
  border-width: 3px;
}
</style>
