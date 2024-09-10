<script setup lang='ts'>
import { ref } from 'vue'
import { NButton } from 'naive-ui'
import List from '../List.vue'
import AddHistoryModal from '../modal/AddHistoryModal.vue'
import { PromptStore } from '@/components/common'
import { AiMode } from '@/models/chat.model'
import { useUserStore } from '@/store'
import SiderToolBar from '@/views/chat/components/SiderToolBar/index.vue'

const userStore = useUserStore()
const show = ref(false)
const showPromptStore = ref(false)
const searchValue = ref('')

function handleAdd() {
  show.value = !show.value
}
</script>

<template>
  <div class="flex flex-col w-[240px]">
    <SiderToolBar
      v-model:search="searchValue"
      :add-button-tips="$t('chat.newRoleButton')"
      @add="handleAdd"
    />
    <div class="flex-1 min-h-0 pb-4 pl-0 overflow-hidden">
      <List :ai-mode="AiMode.MyFavorites" :search="searchValue" />
    </div>
    <div v-if="userStore.isAdminAndAbove" class="p-4 pl-0 flex flex-col gap-2">
      <NButton block @click="showPromptStore = true">
        {{ $t('store.siderButton') }}
      </NButton>
    </div>
  </div>
  <AddHistoryModal v-model:show="show" mode="add" />
  <PromptStore v-model:visible="showPromptStore" />
</template>
