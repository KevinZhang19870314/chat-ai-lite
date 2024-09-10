import path from 'node:path'
import process from 'node:process'
import type { PluginOption } from 'vite'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

function setupPlugins(env: ImportMetaEnv): PluginOption[] {
	return [
		vue(),
		env.VITE_GLOB_APP_PWA === 'true' && VitePWA({
			injectRegister: 'auto',
			manifest: {
				name: 'chatGPT',
				short_name: 'chatGPT',
				icons: [
					{ src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
					{ src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
				],
			},
		}),
	]
}

export default defineConfig((env) => {
	const viteEnv = loadEnv(env.mode, process.cwd()) as unknown as ImportMetaEnv

	return {
		resolve: {
			alias: {
				'@': path.resolve(process.cwd(), 'src'),
			},
		},
		plugins: setupPlugins(viteEnv),
		// assetsInclude: ['**/*.md', '**/*.mdx'],
		server: {
			host: '0.0.0.0',
			port: 1002,
			open: false,
			proxy: {
				'/deep-ai': {
					target: viteEnv.VITE_APP_DEEP_AI_API_BASE_URL,
					changeOrigin: true, // 允许跨域
				},
			},
		},
		build: {
			reportCompressedSize: false,
			sourcemap: false,
			commonjsOptions: {
				ignoreTryCatch: false,
			},
		},
	}
})
