<script setup lang="ts">
import type { CountdownInst, CountdownProps, FormInst, FormItemInst, FormItemRule, FormRules } from 'naive-ui'
import { NButton, NCol, NCountdown, NForm, NFormItem, NInput, NRow, useMessage } from 'naive-ui'

import { computed, h, ref } from 'vue'
import bcrypt from 'bcryptjs'
import { useAppStore, useAuthStore } from '@/store'
import { registerUser, sendSMTPVerificationCode } from '@/api'
import { t } from '@/locales'

const emit = defineEmits(['onLogin'])

interface SignUpModelType {
	email: string | null
	password: string | null
	reenteredPassword: string | null
	verificationCode: string | null
	termsOfService: boolean | null
}

const appStore = useAppStore()
const authStore = useAuthStore()
const ms = useMessage()
const loading = ref(false)
const formRef = ref<FormInst | null>(null)
const rPasswordFormItemRef = ref<FormItemInst | null>(null)
const modelRef = ref<SignUpModelType>({
	email: null,
	password: null,
	reenteredPassword: null,
	verificationCode: null,
	termsOfService: false,
})

const isDark = computed(() => appStore.theme === 'dark')
const countdownDuration = 60 * 1000
const countdownRef = ref<CountdownInst | null>()
const isVerificationCodeActive = ref(false)
const countdownButtonLoading = ref(false)
const renderCountdown: CountdownProps['render'] = ({ minutes, seconds }) => {
	return h(NButton, {
		type: 'default',
		size: 'large',
		disabled: isVerificationCodeActive.value,
		loading: countdownButtonLoading.value,
		onClick: () => {
			formRef.value?.validate(
				async (errors) => {
					countdownButtonLoading.value = true
					if (!errors) {
						const email = modelRef.value.email?.trim()
						const res = await sendSMTPVerificationCode(email!)
						if (res.status === 'Error')
							ms.error(`${res.message}`)

						countdownButtonLoading.value = false
						if (!isVerificationCodeActive.value)
							isVerificationCodeActive.value = true
					}
					else {
						countdownButtonLoading.value = false
					}
				},
				(rule) => {
					return rule?.key !== 'verificationCodeRequired'
				},
			)
		},
	}, {
		default: () => {
			if (minutes === 1)
				seconds = 60

			return isVerificationCodeActive.value ? t('auth.resendAfterSeconds', { seconds }) : t('auth.sendVerificationCode')
		},
	})
}

function validatePasswordStartWith(
	rule: FormItemRule,
	value: string,
): boolean {
	return (
		!!modelRef.value.password
		&& modelRef.value.password.startsWith(value)
		&& modelRef.value.password.length >= value.length
	)
}
function validatePasswordSame(rule: FormItemRule, value: string): boolean {
	return value === modelRef.value.password
}

const rules: FormRules = {
	email: [
		{
			key: 'emailRequired',
			required: true,
			validator(rule: FormItemRule, value: string) {
				if (!value)
					// eslint-disable-next-line unicorn/error-message
					return new Error('')
				else if (!/^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/.test(value))
					// eslint-disable-next-line unicorn/error-message
					return new Error('')

				return true
			},
			trigger: ['input', 'blur'],
		},
	],
	password: [
		{
			key: 'passwordRequired',
			required: true,
			message: '',
			trigger: ['input', 'blur'],
		},
	],
	reenteredPassword: [
		{
			key: 'reenteredPasswordRequired',
			required: true,
			message: '',
			trigger: ['input', 'blur'],
		},
		{
			key: 'reenteredPasswordStartWith',
			validator: validatePasswordStartWith,
			message: '',
			trigger: 'input',
		},
		{
			key: 'reenteredPasswordSame',
			validator: validatePasswordSame,
			message: '',
			trigger: ['blur', 'password-input'],
		},
	],
	verificationCode: [
		{
			key: 'verificationCodeRequired',
			required: true,
			message: '',
			trigger: ['input', 'blur'],
		},
	],
}

function handlePasswordInput() {
	if (modelRef.value.reenteredPassword)
		rPasswordFormItemRef.value?.validate({ trigger: 'password-input' })
}

function hashPassword(password: string) {
	const decodedSalt = window.atob(import.meta.env.VITE_JWT_SALT_BASE64)
	const hashedPwd = bcrypt.hashSync(password, decodedSalt)

	return hashedPwd
}

function handleSignUp() {
	formRef.value?.validate((errors) => {
		if (modelRef.value.termsOfService === false) {
			ms.error(t('common.termsOfServiceRequired'))
			return
		}

		if (!errors)
			signUp()
	})
}

async function signUp() {
	const email = modelRef.value.email?.trim()
	const password = modelRef.value.password?.trim()
	const reenteredPassword = modelRef.value.reenteredPassword?.trim()
	const verificationCode = modelRef.value.verificationCode

	if (!email || !password || !reenteredPassword || !verificationCode)
		return

	try {
		loading.value = true
		const res: any = await registerUser<any>(email, hashPassword(password), +verificationCode)
		if (res.status === 'Fail' || res.status === 'Error')
			throw new Error(`${res.message}`)

		authStore.setToken(res.access_token)
		authStore.setRefreshToken(res.refresh_token)
		ms.success(t('chat.registerSuccess'))
		emit('onLogin')
	}
	catch (error: any) {
		ms.error(error.message ?? 'error')
		authStore.removeToken()
		// reset fields
		modelRef.value = {
			email: modelRef.value.email,
			password: null,
			reenteredPassword: null,
			verificationCode: null,
			termsOfService: false,
		}
	}
	finally {
		loading.value = false
	}
}

function handleVerificationCodeFinished() {
	isVerificationCodeActive.value = false
	countdownRef.value?.reset()
}
</script>

<template>
	<NForm ref="formRef" class="w-full" label-placement="left" label-width="auto" :model="modelRef" :rules="rules">
		<NFormItem path="email" :show-label="false">
			<NInput v-model:value="modelRef.email" class="text-left" :class="{ 'dark-input': isDark }" size="large"
				:placeholder="$t('setting.email')" @keydown.enter.prevent />
		</NFormItem>
		<NFormItem path="password" :show-label="false">
			<NInput v-model:value="modelRef.password" class="text-left" :class="{ 'dark-input': isDark }"
				show-password-on="mousedown" size="large" :placeholder="$t('setting.password')" type="password"
				@input="handlePasswordInput" @keydown.enter.prevent />
		</NFormItem>
		<NFormItem ref="rPasswordFormItemRef" first path="reenteredPassword" :show-label="false">
			<NInput v-model:value="modelRef.reenteredPassword" class="text-left" :class="{ 'dark-input': isDark }"
				show-password-on="mousedown" size="large" :placeholder="$t('setting.confirmPassword')"
				:disabled="!modelRef.password" type="password" @keydown.enter.prevent />
		</NFormItem>
		<NFormItem path="verificationCode" :show-label="false">
			<div class="flex justify-between w-full gap-4">
				<NInput v-model:value="modelRef.verificationCode" class="text-left" :class="{ 'dark-input': isDark }" size="large"
					:placeholder="$t('auth.verificationCode')" @keydown.enter.prevent />
				<NCountdown ref="countdownRef" :render="renderCountdown" :duration="countdownDuration"
					:active="isVerificationCodeActive" :on-finish="handleVerificationCodeFinished" />
			</div>
		</NFormItem>
		<NRow :gutter="[0, 24]">
			<NCol :span="24">
				<div class="flex justify-center">
					<NButton round quaternary size="large" style="width: 140px" :loading="loading"
						class="bg-gradient-to-bl from-[#38cacc] from-15% via-[#38bdcc] via-35% to-[#38AACC] to-95%"
						@click="handleSignUp">
						<span class="text-sm">{{ $t('auth.signUpBtn') }}</span>
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
