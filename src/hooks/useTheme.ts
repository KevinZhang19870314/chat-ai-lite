import type { GlobalThemeOverrides } from 'naive-ui'
import { computed, watch } from 'vue'
import { darkTheme, useOsTheme } from 'naive-ui'
import { useAppStore } from '@/store'

export function useTheme() {
	const appStore = useAppStore()

	const OsTheme = useOsTheme()

	const isDark = computed(() => {
		if (appStore.theme === 'auto')
			return OsTheme.value === 'dark'
		else
			return appStore.theme === 'dark'
	})

	const theme = computed(() => {
		return isDark.value ? darkTheme : undefined
	})

	const themeOverrides = computed<GlobalThemeOverrides>(() => {
		return {
			common: {
				primaryColor: '#38AACC',
				primaryColorHover: '#4FB3D2', // Lighter variation of '#38AACC'
				primaryColorPressed: '#299AB4', // Darker variation of '#38AACC'
				primaryColorSuppl: '#38AACC',
				successColor: '#22C55E',
				successColorHover: '#16A34A',
				errorColor: '#d03050',
				errorColorHover: '#de576d',
				warningColor: '#F59E0B',
				warningColorHover: '#D97706',
				infoColor: '#82C0CC', // A lighter variant of primary color for informational color
				infoColorHover: '#A3D3E0', // Even lighter variant for hover state
			},
			Switch: {
				railColorActive: '#38AACC',
			},
			Slider: {
				fillColor: '#38AACC',
				fillColorHover: '#4FB3D2',
				dotBorderActive: '#38AACC',
				dotColor: '#38AACC',
			},
			Message: {
				iconColorSuccess: '#22C55E', // Assuming the iconColorSuccess is meant to be success color
			},
		}
	})

	watch(
		() => isDark.value,
		(dark) => {
			if (dark)
				document.documentElement.classList.add('dark')
			else
				document.documentElement.classList.remove('dark')
		},
		{ immediate: true },
	)

	return { theme, themeOverrides }
}
