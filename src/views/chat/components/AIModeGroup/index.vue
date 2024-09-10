<script lang="ts" setup>
import AIModeButtonWidget from '../Widgets/AIModeButtonWidget.vue'
import { useAIMode } from '../../hooks/useAIMode'
import { AiMode } from '@/models/chat.model'
import { useChatStore, useUserStore } from '@/store'

const { setAIMode } = useAIMode()
const chatStore = useChatStore()
const userStore = useUserStore()
const mode = AiMode

function handleSelected(mode: AiMode) {
	setAIMode(mode)
	chatStore.setActive(0)
	chatStore.toMainPage()
}
</script>

<template>
	<div class="flex flex-col w-[60px] p-2 space-y-4 mt-2">
		<AIModeButtonWidget :mode="mode.ChatLLM" bg-color="#38AACC" icon="hugeicons:ai-chat-02" :tooltip="$t('common.chat')"
			@selected="handleSelected(mode.ChatLLM)" />
		<AIModeButtonWidget :mode="mode.KnowledgeBase" bg-color="#38AACC" icon="tdesign:app" :tooltip="$t('chat.localAI')"
			@selected="handleSelected(mode.KnowledgeBase)" />
		<AIModeButtonWidget :mode="mode.MyFavorites" bg-color="#38AACC" icon="teenyicons:box-solid"
			:tooltip="$t('chat.myFavorites')" @selected="handleSelected(mode.MyFavorites)" />
		<AIModeButtonWidget :mode="mode.TextToImage" bg-color="#38AACC" icon="ion:image" :tooltip="$t('common.textToImage')"
			@selected="handleSelected(mode.TextToImage)" />
		<AIModeButtonWidget :mode="mode.DigitalPerson" bg-color="#38AACC" icon="bi:robot" :tooltip="$t('digitalPerson.title')"
			@selected="handleSelected(mode.DigitalPerson)" />
		<AIModeButtonWidget v-if="userStore.isAdminAndAbove" :mode="mode.Admin" bg-color="#38AACC"
			icon="clarity:administrator-solid" :tooltip="$t('common.admin')" @selected="handleSelected(mode.Admin)" />
	</div>
</template>
