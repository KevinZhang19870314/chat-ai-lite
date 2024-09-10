<script setup lang='ts'>
import { computed, ref } from 'vue'
import { NModal, NTabPane, NTabs } from 'naive-ui'
// import Payment from './Payment.vue'
import Account from './Account.vue'
import { useUserStore } from '@/store'
import { SvgIcon } from '@/components/common'

interface Props {
  visible: boolean
}

interface Emit {
  (e: 'update:visible', visible: boolean): void
}

const props = defineProps<Props>()

const emit = defineEmits<Emit>()

const userStore = useUserStore()

const active = ref('Account')

const show = computed({
  get() {
    return props.visible
  },
  set(visible: boolean) {
    emit('update:visible', visible)
  },
})
</script>

<template>
  <NModal v-model:show="show" :auto-focus="false" preset="card" style="width: 95%; max-width: 860px">
    <div>
      <NTabs v-model:value="active" type="line" animated>
        <NTabPane v-if="userStore.isAdminAndAbove" name="Account" tab="Account">
          <template #tab>
            <SvgIcon class="text-lg" icon="ri:account-box-line" />
            <span class="ml-2">{{ $t('setting.account') }}</span>
          </template>
          <Account />
        </NTabPane>
      </NTabs>
    </div>
  </NModal>
</template>
