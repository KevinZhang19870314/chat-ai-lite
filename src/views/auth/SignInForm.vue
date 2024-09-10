<script setup lang="ts">
import type { FormInst, FormRules } from 'naive-ui'
import { NButton, NCol, NForm, NFormItem, NInput, NRow, useMessage } from 'naive-ui'

import bcrypt from 'bcryptjs'
import { computed, ref } from 'vue'
import { login } from '@/api'
import { t } from '@/locales'
import { router } from '@/router'
import { useAppStore, useAuthStore } from '@/store'

interface SignInModelType {
	email: string | null
	password: string | null
}

const appStore = useAppStore()
const authStore = useAuthStore()
const ms = useMessage()
const loading = ref(false)
const formRef = ref<FormInst | null>(null)
const modelRef = ref<SignInModelType>({
	email: null,
	password: null,
})

const rules: FormRules = {
	email: [
		{
			required: true,
			message: '',
			trigger: ['input', 'blur'],
		},
	],
	password: [
		{
			required: true,
			message: '',
			trigger: ['input', 'blur'],
		},
	],
}

const isDark = computed(() => appStore.theme === 'dark')

function hashPassword(password: string) {
	const decodedSalt = window.atob(import.meta.env.VITE_JWT_SALT_BASE64)
	const hashedPwd = bcrypt.hashSync(password, decodedSalt)

	return hashedPwd
}

async function handleSignIn() {
	formRef.value?.validate((errors) => {
		if (!errors)
			signIn()
	})
}

async function signIn() {
	try {
		loading.value = true
		const email = modelRef.value.email?.trim()
		const password = modelRef.value.password?.trim()

		if (!email || !password)
			return

		const tokenData = await login(email, hashPassword(password))
		authStore.setToken((tokenData as any)?.access_token)
		authStore.setRefreshToken((tokenData as any)?.refresh_token)
		await authStore.getSession()
		router.push('/my-favorites')
		ms.success(t('auth.signInSuccess'))
	}
	catch (error) {
		ms.error(`${error}`)
	}
	finally {
		loading.value = false
	}
}

function handleForgotPassword() {
	ms.info(t('auth.contactAdmin'))
}

function handleEnter(event: KeyboardEvent) {
	event.preventDefault()
	handleSignIn()
}
</script>

<template>
	<NForm ref="formRef" class="w-full" label-placement="left" label-width="auto" :model="modelRef" :rules="rules">
		<NFormItem path="email" :show-label="false">
			<NInput v-model:value="modelRef.email" class="text-left email" :class="{ 'dark-input': isDark }" size="large"
				:placeholder="$t('setting.email')" @keyup.enter="handleEnter" />
		</NFormItem>
		<NFormItem path="password" :show-label="false">
			<NInput v-model:value="modelRef.password" class="text-left" :class="{ 'dark-input': isDark }"
				show-password-on="mousedown" size="large" :placeholder="$t('setting.password')" type="password"
				@keyup.enter="handleEnter" />
		</NFormItem>
		<a class="cursor-pointer my-2 inline-block underline underline-offset-2" @click="handleForgotPassword">{{
			$t('common.forgotYourPassword') }}</a>
		<NRow :gutter="[0, 24]">
			<NCol :span="24">
				<div class="flex justify-center">
					<NButton round quaternary size="large" style="width: 140px" :loading="loading"
						class="bg-gradient-to-bl from-[#38cacc] from-15% via-[#38bdcc] via-35% to-[#38AACC] to-95%"
						@click="handleSignIn">
						<span class="text-sm">{{ $t('common.signInBtn') }}</span>
					</NButton>
				</div>
			</NCol>
		</NRow>
	</NForm>
</template>

<style lang="less">
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

input:-webkit-autofill {
	-webkit-text-fill-color: #333639 !important;
	-webkit-box-shadow: 0 0 0px 1000px #fff inset !important;

	&:focus {
		-webkit-box-shadow: 0 0 0px 1000px #fff inset !important;
	}
}

.dark-input {
	input:-webkit-autofill {
		-webkit-text-fill-color: #fff !important;
		-webkit-box-shadow: 0 0 0px 1000px #363F4B inset !important;

		&:focus {
			-webkit-box-shadow: 0 0 0px 1000px #2B3D46 inset !important;
		}
	}
}
</style>
