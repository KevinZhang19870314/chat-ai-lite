<script setup lang="ts">
import { computed, ref } from 'vue'
import { NAvatar, NButton, NPopselect, NSpace } from 'naive-ui'
import SignUpForm from './SignUpForm.vue'
import SignInForm from './SignInForm.vue'
import { feishuAuth, githubAuth } from '@/api'
import { useAppStore } from '@/store'
import { SvgIcon } from '@/components/common'
import type { Language } from '@/store/modules/app/helper'
import feishuLogo from '@/assets/feishu.png'

const isSignUpActive = ref(false)
const appStore = useAppStore()
const theme = computed(() => appStore.theme)
const options = [
	{ label: '中文', key: 'zh-CN', value: 'zh-CN' },
	{ label: 'EN', key: 'en-US', value: 'en-US' },
	{ label: '日本語', key: 'ja-JP', value: 'ja-JP' },
]

const language = computed({
	get() {
		return appStore.language
	},
	set(value: Language) {
		appStore.setLanguage(value)
	},
})

const selectLang = computed(() => options.find((item: any) => item.key === appStore.language)!.label)

function handleLangSelect(key: Language) {
	appStore.setLanguage(key)
}

function activateSignUp() {
	isSignUpActive.value = true
}
function activateSignIn() {
	isSignUpActive.value = false
}

async function handleFeishuLogin() {
	const res = await feishuAuth<any>()
	const authorizeUrl = res.data.authorize_url
	window.location.href = authorizeUrl
}

async function handleGithubLogin() {
	const res = await githubAuth<any>()
	const authorizeUrl = res.data.authorize_url
	window.location.href = authorizeUrl
}
</script>

<template>
	<div class="flex items-center justify-center relative h-screen text-gray-800 dark:text-white">
		<div class="flex flex-wrap items-center gap-4 absolute top-4 right-4">
			<!-- 主题 -->
			<NButton v-if="theme === 'light'" size="medium" circle type="primary" @click="appStore.setTheme('dark')">
				<template #icon>
					<SvgIcon icon="ri:sun-foggy-line" />
				</template>
			</NButton>
			<NButton v-else size="medium" circle type="default" @click="appStore.setTheme('light')">
				<template #icon>
					<SvgIcon icon="ri:moon-foggy-line" />
				</template>
			</NButton>
			<!-- 多语言 -->
			<NPopselect v-model:value="language" trigger="hover" placement="bottom-start" :options="options"
				@select="handleLangSelect">
				<NButton round size="medium">
					{{ selectLang }}
				</NButton>
			</NPopselect>
		</div>
		<div id="container" :class="{ 'right-panel-active': isSignUpActive }" class="container bg-white dark:bg-gray-800">
			<div class="form-container sign-up-container h-[480px]">
				<NSpace vertical class="w-full">
					<div class="text-4xl font-bold mb-8">
						{{ $t('auth.createAccount') }}
					</div>
				</NSpace>
				<SignUpForm @on-login="activateSignIn" />
			</div>
			<div class="form-container sign-in-container h-[480px]">
				<NSpace vertical class="w-full">
					<div class="text-4xl font-bold mb-4">
						{{ $t('common.login') }}
					</div>
					<div class="flex items-center justify-center gap-4">
						<NAvatar class="cursor-pointer hover:shadow-lg" round size="large" :src="feishuLogo"
							@click="handleFeishuLogin" />
						<NAvatar class="cursor-pointer hover:shadow-lg bg-gray-200 dark:bg-gray-500" round color="transparent"
							size="large" @click="handleGithubLogin">
							<SvgIcon icon="mdi:github" class="text-9xl text-black" />
						</NAvatar>
					</div>
					<div class="my-2">
						{{ $t('common.orUseYourAccount') }}
					</div>
				</NSpace>
				<SignInForm />
			</div>
			<div class="overlay-container h-[480px]">
				<div class="overlay" :class="{
					'bg-gradient-to-bl from-[#38cacc] from-15% via-[#38bdcc] via-35% to-[#38AACC] to-95%': isSignUpActive,
					'bg-gradient-to-tr from-[#38cacc] from-15% via-[#38bdcc] via-35% to-[#38AACC] to-95%': !isSignUpActive,
				}">
					<div class="overlay-panel overlay-left gap-2">
						<h1 class="text-4xl font-bold">
							{{ $t('auth.signInTitle') }}
						</h1>
						<p class="text-base mt-4 mb-8 font-thin">
							{{ $t('auth.signInSubTitle') }}
						</p>
						<NButton tertiary strong round size="large" style="width: 140px" @click="activateSignIn">
							<span class="text-sm font-bold">{{ $t('auth.signInBtn') }}</span>
						</NButton>
					</div>
					<div class="overlay-panel overlay-right gap-2">
						<h1 class="text-4xl font-bold">
							{{ $t('auth.signUpTitle') }}
						</h1>
						<p class="text-base mt-4 mb-8 font-thin">
							{{ $t('auth.signUpSubTitle') }}
						</p>
						<NButton tertiary strong round size="large" style="width: 140px" @click="activateSignUp">
							<span class="text-sm font-bold">{{ $t('auth.signUpBtn') }}</span>
						</NButton>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style lang="less" scoped>
.container {
	border-radius: 10px;
	box-shadow: 0 14px 28px rgba(0, 0, 0, .2), 0 10px 10px rgba(0, 0, 0, .2);
	position: relative;
	overflow: hidden;
	width: 768px;
	max-width: 100%;
	min-height: 480px;
	margin: auto;
}

.form-container {
	display: flex;
	flex-direction: column;
	padding: 0 50px;
	height: 100%;
	justify-content: center;
	align-items: center;
	text-align: center;
}

.social-container {
	margin: 20px 0;
}

.form-container input {
	background: #eee;
	border: none;
	padding: 12px 15px;
	margin: 8px 0;
	width: 100%;
}

button {
	letter-spacing: 1px;
	text-transform: uppercase;
	transition: transform 80ms ease-in;
}

button:active {
	transform: scale(.95);
}

button:focus {
	outline: none;
}

.form-container {
	position: absolute;
	top: 0;
	height: 100%;
	transition: all .6s ease-in-out;
}

.sign-in-container {
	left: 0;
	width: 50%;
	z-index: 2;
}

.sign-up-container {
	left: 0;
	width: 50%;
	z-index: 1;
	opacity: 0;
}

.overlay-container {
	position: absolute;
	top: 0;
	left: 50%;
	width: 50%;
	height: 100%;
	overflow: hidden;
	transition: transform .5s ease-in-out;
	z-index: 100;
}

.overlay {
	position: relative;
	left: -100%;
	height: 100%;
	width: 200%;
	transform: translateY(0);
	transition: transform .5s ease-in-out;
}

.overlay-panel {
	position: absolute;
	top: 0;
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	padding: 0 40px;
	height: 100%;
	width: 50%;
	text-align: center;
	transform: translateY(0);
	transition: transform .5s ease-in-out;
}

.overlay-right {
	right: 0;
	transform: translateY(0);
}

.overlay-left {
	transform: translateY(-20%);
}

/* Move signin to right */
.container.right-panel-active .sign-in-container {
	transform: translateY(100%);
}

/* Move overlay to left */
.container.right-panel-active .overlay-container {
	transform: translateX(-100%);
}

/* Bring signup over signin */
.container.right-panel-active .sign-up-container {
	transform: translateX(100%);
	opacity: 1;
	z-index: 5;
}

/* Move overlay back to right */
.container.right-panel-active .overlay {
	transform: translateX(50%);
}

/* Bring back the text to center */
.container.right-panel-active .overlay-left {
	transform: translateY(0);
}

/* Same effect for right */
.container.right-panel-active .overlay-right {
	transform: translateY(20%);
}
</style>
