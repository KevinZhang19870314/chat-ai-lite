import type { App } from 'vue'
import type { RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHashHistory } from 'vue-router'
import { setupPageGuard } from './permission'
import { ChatLayout } from '@/views/chat/layout'
import { AdminLayout } from '@/views/admin/layout'
import Auth from '@/views/auth/index.vue'
import MyFavorites from '@/views/home/MyFavorites.vue'
import FeishuRedirect from '@/views/chat/FeishuRedirect.vue'
import GithubRedirect from '@/views/chat/GithubRedirect.vue'
import { TextToImageLayout } from '@/views/text-to-image/layout'

const routes: RouteRecordRaw[] = [
	{
		path: '/',
		name: 'Root',
		component: ChatLayout,
		redirect: '/my-favorites',
		children: [
			{
				path: 'chat/:uuid?',
				name: 'Chat',
				component: () => import('@/views/chat/index.vue'),
			},
			{
				path: 'my-favorites',
				name: 'My Favorites',
				component: MyFavorites,
			},
			{
				path: 'chatllm',
				name: 'ChatLLM',
				component: () => import('@/views/home/ChatLLM.vue'),
			},
			{
				path: 'ai-square',
				name: 'AI Square',
				component: () => import('@/views/home/AISquare.vue'),
			},
			{
				path: 'digital-person',
				name: 'Digital Person',
				component: () => import('@/views/home/DigitalPerson.vue'),
			},
			{
				path: '/text-to-image',
				name: 'TextToImage',
				component: TextToImageLayout,
				redirect: () => {
					return '/text-to-image/images-preview'
				},
				children: [
					{
						path: 'images-preview',
						name: 'Images Preview',
						component: () => import('@/views/text-to-image/ImagesPreview.vue'),
					},
					{
						path: 'gen-images',
						name: 'Generate Images',
						component: () => import('@/views/text-to-image/GenImages.vue'),
					},
				],
			},
			{
				path: '/admin',
				name: 'Admin',
				component: AdminLayout,
				redirect: () => {
					return '/admin/personal'
				},
				children: [
					{
						path: 'personal',
						name: 'Personal Center',
						component: () => import('@/views/admin/PersonalCenter.vue'),
					},
					{
						path: 'user',
						name: 'User Management',
						component: () => import('@/views/admin/User.vue'),
					},
					{
						path: 'ai-assistant',
						name: 'AI Assistant Management',
						component: () => import('@/views/admin/AIAssistant.vue'),
					},
				],
			},
		],
	},
	{
		path: '/authorize',
		name: 'authorize',
		component: Auth,
	},
	{
		path: '/redirect',
		name: 'redirect',
		component: () => import('@/views/chat/Redirect.vue'),
	},
	{
		path: '/feishu-redirect',
		name: 'feishu-redirect',
		component: FeishuRedirect,
	},
	{
		path: '/github-redirect',
		name: 'github-redirect',
		component: GithubRedirect,
	},
	{
		path: '/404',
		name: '404',
		component: () => import('@/views/exception/404/index.vue'),
	},
	{
		path: '/500',
		name: '500',
		component: () => import('@/views/exception/500/index.vue'),
	},
	{
		path: '/:pathMatch(.*)*',
		name: 'notFound',
		redirect: '/404',
	},
]

export const router = createRouter({
	history: createWebHashHistory(),
	routes,
	scrollBehavior: () => ({ left: 0, top: 0 }),
})
setupPageGuard(router)
export async function setupRouter(app: App) {
	app.use(router)
	await router.isReady()
}
