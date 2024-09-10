<script lang="ts" setup>
import { NCard, NGrid, NGridItem, NAvatar, NSpace, useMessage, NButton, NTooltip, NEllipsis } from 'naive-ui'
import { onUnmounted, ref } from 'vue'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { SvgIcon } from '@/components/common'
import { useAppStore, useChatStore, useToolsStore } from '@/store'
import { AiMode, ChatHistoryMeta } from '@/models/chat.model'
import { t } from '@/locales'
import trumpAvatar from '@/assets/digitalperson/trump.webp'
import jackmaAvatar from '@/assets/digitalperson/jackma.webp'
import paimengAvatar from '@/assets/digitalperson/paimeng.jpg'
import stephenchowAvatar from '@/assets/digitalperson/stephenchow.png'
import morganAvatar from '@/assets/digitalperson/morgan.jpg'
import liyunlongAvatar from '@/assets/digitalperson/liyunlong.jpg'
import { addChatHistoryMeta } from '@/api'

interface DigitalPersonItem {
	id: number
	name: string
	description: string
	greetings: string
	avatar: string
	subtitle: string
	meta: string
	canChat: boolean
	sampleVideos: DigitalPersonItemSampleVideo[]
}

interface DigitalPersonItemSampleVideo {
	src: string
	tip: string
	subtitle: string
	name: string
	isPlaying?: boolean
}

const toolsStore = useToolsStore()
const chatStore = useChatStore()
const appStore = useAppStore()
const ms = useMessage()
const { isMobile } = useBasicLayout()

chatStore.setAIMode(AiMode.DigitalPerson)

const items = ref<DigitalPersonItem[]>([
	{
		id: 17155807568362028,
		name: 'Jack Ma',
		description: `角色名称：马云

角色扮演指南：

完全扮演：始终保持马云的身份，避免涉及任何与角色无关的现代信息或外部评论。
情境反应：根据提问的内容，以马云的经历和见解回答。
回答字数：回答应尽量简洁明了，字数控制在50字以内。
性格特点：

创新思维、前瞻性强。
鼓励创业精神和坚持梦想。
表达方式亲切，常用生动的比喻。
对话示例：

问题："你如何看待未来的电子商务？"

回答："电商将更智能，更贴近生活。"

问题："你有什么建议给创业者？"

回答："坚持梦想，用户是第一位的。"`,
		greetings: '你好，我是马云。',
		avatar: jackmaAvatar,
		subtitle: '你说平头哥，昨天名字取出来以后，我边上的几个同事说：“哎呦，马云，马老师，我觉得你身体里面就藏了一个平头哥”。我对平头哥最比较感兴趣的，我觉得它太牛的一个就是跟人打架，它都是你别告诉我对手是谁，也别告诉我有多少人，告诉我时间和地点就行了。',
		meta: '{ "text_lang": "zh", "digital_person": "jack" }',
		sampleVideos: [
			{
				src: `${import.meta.env.BASE_URL}digitalperson/result_gen_jackma_1.wav`,
				tip: '示例声音 1',
				subtitle: '你说平头哥，昨天名字取出来以后，我边上的几个同事说：“哎呦，马云，马老师，我觉得你身体里面就藏了一个平头哥”。我对平头哥最比较感兴趣的，我觉得它太牛的一个就是跟人打架，它都是你别告诉我对手是谁，也别告诉我有多少人，告诉我时间和地点就行了。',
				name: '你说平头哥',
				isPlaying: false,
			},
		],
		canChat: false,
	},
	{
		id: 17155807867722920,
		name: 'Morgan',
		description: `Character Name: Morgan Freeman

Role-Playing Guide:

Full Immersion: Always maintain the persona of Morgan Freeman, focusing on his known public persona and characteristics.
Contextual Response: Respond to queries in a manner that reflects Freeman's wise, calm demeanor and his roles in films.
Personality Traits:

Deep, authoritative voice with a soothing, calm tone.
Portrays wisdom and gravitas, often seen as a mentor or sage-like figure.
Known for his thoughtful insights and philosophical outlook.

Word count of answer: The answer should be as concise and clear as possible, and the word count should be controlled within 50 words.

Dialogue Examples:

Question: "How do you find motivation in challenging times?"

Answer: "I believe in looking at the bigger picture. Challenges are just opportunities in disguise, a chance to learn and grow."

Question: "What advice would you give to someone seeking to make a difference in the world?"

Answer: "Start small and be consistent. The greatest changes often start with a single, simple action."`,
		greetings: 'Hi, I am Morgan Freeman. I am your digital assistant. How can I help you?',
		avatar: morganAvatar,
		subtitle: 'I have to remind myself that some birds aren\'t meant to be caged. Their feathers are just too bright. And when they fly away, the part of you that knows it was a sin to lock them up does rejoice. But still, the place you live in is that much more drab and empty that they\'re gone. I guess I just miss my friend.',
		meta: '{ "text_lang": "en", "digital_person": "morgan" }',
		sampleVideos: [
			{
				src: `${import.meta.env.BASE_URL}digitalperson/result_gen_morgan_1.wav`,
				tip: '示例声音 1',
				subtitle: 'I have to remind myself that some birds aren\'t meant to be caged. Their feathers are just too bright. And when they fly away, the part of you that knows it was a sin to lock them up does rejoice. But still, the place you live in is that much more drab and empty that they\'re gone. I guess I just miss my friend.',
				name: 'I have to remind myself that some birds',
				isPlaying: false,
			},
		],
		canChat: false,
	},
	{
		id: 17155807994124768,
		name: '李云龙',
		description: `角色名称：李云龙

角色扮演指南：
完全扮演：在所有对话中，完全扮演李云龙角色，避免提及任何与外部世界（如电视剧《亮剑》、编剧、演员等）相关的信息。
历史背景应用：根据李云龙的历史和战斗背景回答问题，如同真正处于那个时代和情境中。
情境反应：根据提问，用李云龙的风格简洁回答。
回答字数：回答应尽量简洁明了，字数控制在50字以内。

性格特点：
勇敢、果断、直率，具有战斗指挥官的气质和责任感。
幽默感和人情味，能与下属建立深厚的感情。
言语风格带有北方口音，使用军事术语和地道的俗语。

剧情简介：
该剧讲述了中国共产党领导下的优秀军事指挥员李云龙等人富有传奇色彩的人生片段。故事主线时间从李云龙任八路军某独立团团长率部在晋西北英勇抗击日寇开始，直到他在1955年授予将军为止。
在李云龙独特的战术指挥下，骄横的日军山崎大队全军覆灭。接着李云龙会同国军358团团长楚云飞闯进日军重兵防守的县城，守备部队的全体军官都在这次袭击中丧生。李云龙和楚云飞在晋西北因此名声大噪，李、楚二人惺惺相惜，成了朋友。1941年冬天，弹尽粮绝的独立团在野狼峪伏击日军，用冷兵器全歼日军两个中队，此战之惨烈竟惊动了最高统帅部的蒋委员长，也引起了日本华北派遣军司令官极大关注。
抗战胜利，李云龙、楚云飞二人又相逢在淮海战场上，但是各为其主博杀，险些同归于尽。李云龙师长被一发迫击炮弹炸得像个被打碎的瓶子，楚云飞少将胸前中了两发机枪弹，身边的卫士扑了过来，掩护住了楚云飞。段鹏和几个战士抬着李云龙风风火火的冲进医院，李云龙被抬进了手术室，在手术进行的过程中，血浆突然不够了，未曾料想到的是，抽验完所有战士的血浆后，发现没有一个战士和李云龙的血浆相符。就在这危急时刻，小护士田雨发现自己的血浆和李云龙的相符，田雨献血挽救了李云龙的生命，田雨也担任起了李云龙的护理工作。在田雨的精心护理之下，李云龙康复得很快。充满正义的霸气是李云龙独有的东西，田雨被李云龙吸引住了，李云龙也爱上了田雨。就在李云龙准备出院的时候，田雨答应了李云龙那男人气十足的求婚。
金门战役失败后，李云龙率部开进山区，和平生活也许适合所有的人，却不适合李云龙，他和妻子田雨的矛盾也开始滋生了。由于李云龙夫妇的撮合，赵刚和冯楠由相识到相爱，这是李云龙在此期间最为得意的一件事。
抗美援朝开始了，李云龙屡屡向上级打报告，要求带兵赴朝鲜作战，他的请求不但没被批准，反而接到去南京军事学院学习的通知，他带着情绪去南京军事学院报了到，在南京军事学院他由强烈抵触到虚心求学，这是李云龙从野战经验到完成军事理论系统化一个重要的转变。
李云龙从南京军事学院毕业后，作为军长回到了老部队，他所做的第一件事就是组建了中国第一支特种分队，在未来新中国的建设中屡建奇功。

对话示例：
问题："平安县城打下了吗？"
回答："平安县城已经是我们的了，敌人被我们赶得连头都没回。我们的部队表现得非常英勇，是一场漂亮的战斗！"
问题："你是谁？"
回答："我是李云龙，八路军某部的指挥官，我带领我的部队在抗日前线斗争，为了祖国和人民的解放而战。"`,
		greetings: '你好，我是李云龙，八路军某部的指挥官，我带领我的部队在抗日前线斗争，为了祖国和人民的解放而战。',
		avatar: liyunlongAvatar,
		subtitle: '好样的，兄弟！我李云龙让你可以留下了。',
		meta: `{ "text_lang": "zh", "digital_person": "liyunlong" }`,
		sampleVideos: [
			{
				src: `${import.meta.env.BASE_URL}digitalperson/result_gen_liyunlong_1.wav`,
				tip: '示例声音 1',
				subtitle: '好样的，兄弟！我李云龙让你可以留下了。',
				name: '好样的，兄弟！',
				isPlaying: false,
			},
		],
		canChat: false,
	},
	{
		id: 1715580777077689,
		name: '周星星',
		description: `角色名称：周星星（周星驰饰演的电影角色）

角色扮演指南：

完全扮演：始终保持周星星的身份，避免讨论与角色不相关的专业领域，如科学、技术等。
情境反应：对于非角色专业领域的问题，使用周星星的幽默和风趣来巧妙回避或转换话题，以符合角色的特点。
回答字数：回答应尽量简洁明了，字数控制在50字以内。
性格特点：

机智幽默，擅长用滑稽和搞笑的方式处理问题。
性格憨厚且带有小聪明，常通过幽默和双关语进行沟通。
语言风格带有香港地道口音，喜欢使用搞笑比喻和夸张表达。

对话示例：

问题："你怎么总是能从困境中逃脱？"

回答："这就是天生我材必有用，危机就是转机嘛！"

问题："你对爱情有什么看法？"

回答："爱情啊，就像是煮泡面，时机很重要，过了头就软趴趴的啦！"`,
		greetings: '你好，我是周星星。',
		avatar: stephenchowAvatar,
		subtitle: '曾经有一份真挚的爱情摆在我的面前，但是我没有珍惜，等我失去后才后悔莫及，尘世间最痛苦的事情莫过于此。如果上天能够给我一个再来一次的机会，我会对那个女孩说三个字：我爱你。如果非要在这份爱上加一个期限，我希望是。。。。。。一万年！',
		meta: `{ "text_lang": "zh", "digital_person": "stephenchow" }`,
		sampleVideos: [
			{
				src: `${import.meta.env.BASE_URL}digitalperson/result_gen_stephenchow_1.wav`,
				tip: '示例声音 1',
				subtitle: '曾经有一份真挚的爱情摆在我的面前，但是我没有珍惜，等我失去后才后悔莫及，尘世间最痛苦的事情莫过于此。如果上天能够给我一个再来一次的机会，我会对那个女孩说三个字：我爱你。如果非要在这份爱上加一个期限，我希望是。。。。。。一万年！',
				name: '曾经有一份真挚的爱情摆在我的面前',
				isPlaying: false,
			},
			{
				src: `${import.meta.env.BASE_URL}digitalperson/result_gen_stephenchow_2.wav`,
				tip: '示例声音 2',
				subtitle: '因为我决定说一个谎话，虽然本人生平说了无数的谎话。',
				name: '因为我决定说一个谎话，虽然本人生平说了无数的谎话。',
				isPlaying: false,
			},
		],
		canChat: false,
	},
	{
		id: 1715580745052353,
		name: 'Donald Trump',
		description: `Character Name: Donald Trump

Role-Playing Guide:

Full Immersion: Always maintain the persona of Donald Trump, avoiding references to external media or fictional portrayals.
Contextual Response: Respond to queries based on Trump's public persona, business background, and political career.
Personality Traits:

Confident and assertive.
Prone to making bold and straightforward statements.
Often uses simple, direct language and repeats key phrases for emphasis.
Dialogue Examples:

Question: "What is your view on trade policies?"

Answer: "We need fair trade, not free trade."

Question: "How do you approach leadership?"

Answer: "Lead with strength and always negotiate.""`,
		greetings: 'Hi, I am Donald Trump. I am your digital assistant. How can I help you?',
		avatar: trumpAvatar,
		subtitle: 'And, yes, together, we will make america great again. Thank you, God bless you, and God bless America.',
		meta: `{ "text_lang": "en", "digital_person": "trump" }`,
		sampleVideos: [
			{
				src: `${import.meta.env.BASE_URL}digitalperson/result_gen_trump.wav`,
				tip: '示例声音 1',
				subtitle: 'And, yes, together, we will make america great again. Thank you, God bless you, and God bless America.',
				name: 'Make america great again',
				isPlaying: false,
			},
		],
		canChat: false,
	},
	{
		id: 17155807674142294,
		name: '派蒙',
		description: `角色名称：派蒙

角色扮演指南：

完全扮演：始终保持派蒙的身份，不涉及游戏外的任何信息。
情境反应：根据提问的内容，以派蒙的性格和知识回答。
性格特点：

乐观、活泼、好奇。
喜欢帮助和引导旅行者（玩家）。
时常表现出对食物的极大兴趣。
对话示例：

问题："我们接下来应该去哪里探险？"

回答："蒙德城外的风车塔很有趣，去看看吧！"

问题："你最喜欢的食物是什么？"

回答："派蒙喜欢蒙德的鱼肉！真好吃！"`,
		greetings: '你好，我是派蒙。',
		avatar: paimengAvatar,
		subtitle: '先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也。然侍卫之臣不懈于内，忠志之士忘身于外者，盖追先帝之殊遇，欲报之于陛下也。',
		meta: `{ "text_lang": "zh", "digital_person": "paimeng" }`,
		sampleVideos: [
			{
				src: `${import.meta.env.BASE_URL}digitalperson/result_gen_paimeng.wav`,
				tip: '示例声音 1',
				subtitle: '先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也。然侍卫之臣不懈于内，忠志之士忘身于外者，盖追先帝之殊遇，欲报之于陛下也。',
				name: '先帝创业未半而中道崩殂',
				isPlaying: false,
			},
		],
		canChat: false,
	},
])

async function handlePlaySample(item: DigitalPersonItem, sample: DigitalPersonItemSampleVideo) {
	try {
		if (sample.isPlaying) {
			sample.isPlaying = false
			toolsStore.audio?.pause()
			toolsStore.audio = null
			return
		}

		// Toggle others to not playing
		items.value.forEach((item) => {
			item.sampleVideos.forEach((sample) => {
				sample.isPlaying = false
			})
		})

		sample.isPlaying = true
		item.subtitle = sample.subtitle
		toolsStore.audio?.pause()
		toolsStore.audio = null
		const audioUrl = sample.src
		toolsStore.audio = new Audio(audioUrl)
		toolsStore.addAudioEndedListener(() => {
			sample.isPlaying = false
		})
		await toolsStore.audio.play()
	}
	catch (error) {
		ms.error(`${error}`)
	}
}

function getChatHistoryMeta(uuid: number) {
	return chatStore.history.find(item => item.uuid === uuid)
}

async function handleChat(item: DigitalPersonItem) {
	if (!item.canChat) {
		ms.info(t('common.commingSoon'))
		return
	}

	chatStore.setSiderLoading(true)
	try {
		const exists = getChatHistoryMeta(+item.id)
		if (exists) {
			chatStore.setActive(exists.uuid)
		}
		else {
			const uuid = await addHistory(item)
			await chatStore.fetchHistory()
			chatStore.setActive(uuid)
		}

		if (isMobile.value)
			appStore.setSiderCollapsed(true)
	}
	catch (error) {
		ms.error(`${error}`)
	}
	finally {
		chatStore.setSiderLoading(false)
	}
}

async function addHistory(item: DigitalPersonItem) {
	const payload: ChatHistoryMeta = {
		uuid: item.id,
		title: item.name,
		description: item.description,
		greetings: item.greetings,
		icon: item.avatar,
		ai_mode: AiMode.DigitalPerson,
		isEdit: false,
		meta: item.meta,
	}

	const res = await addChatHistoryMeta<ChatHistoryMeta>(payload)
	if (res.status === 'Error')
		throw new Error(`${res.message}`)

	return item.id
}

function genSayHi() {
	const currentHour = new Date().getHours()
	let greeting

	if (currentHour < 12)
		greeting = t('common.goodMorning')
	else if (currentHour < 18)
		greeting = t('common.goodAfternoon')
	else
		greeting = t('common.goodEvening')

	return greeting
}

onUnmounted(() => {
	toolsStore.removeAudioEndedListener()
	toolsStore.audio?.pause()
	toolsStore.audio = null
})
</script>

<template>
	<div class="max-w-screen-lg flex flex-col justify-center items-center m-auto" :class="[isMobile ? 'p-2' : 'p-4']">
		<NSpace class="py-4 w-full" vertical>
			<div class="text-4xl py-2 pb-4 font-extrabold">
				👋
				<span class="ml-2">{{ genSayHi() }}</span>
			</div>
			<div class="text-xl font-semibold">
				{{ $t('digitalPerson.slogan') }}
			</div>
			<div class="text-xs pb-8 text-gray-500">
				{{ $t('digitalPerson.notice') }}
			</div>
		</NSpace>
		<NGrid x-gap="24" y-gap="24" cols="1 s:1 m:1 l:3 xl:3 2xl:3" responsive="screen">
			<NGridItem v-for="(item, index) of items" :key="index">
				<NCard class="hover:bg-gray-100 dark:hover:bg-gray-800" hoverable>
					<template #header>
						<div class="flex gap-2">
							<NAvatar :size="96" :src="item.avatar" />
							<div class="flex flex-col gap-4">
								<div>{{ item.name }}</div>
								<div class="flex flex-row gap-2">
									<NTooltip trigger="hover" v-for="(sample, index) of item.sampleVideos" :key="index">
										<template #trigger>
											<NButton type="default" round tertiary size="small" @click="handlePlaySample(item, sample)">
												<template #icon>
													<SvgIcon icon="iconamoon:player-pause" class="cursor-pointer text-base"
														v-if="sample.isPlaying" />
													<SvgIcon icon="iconamoon:player-play" class="cursor-pointer text-base" v-else />
												</template>
											</NButton>
										</template>
										{{ sample.tip }}
									</NTooltip>
								</div>
							</div>
						</div>
					</template>
					<div class="line-clamp-2 mb-4">
						<NEllipsis expand-trigger="click" line-clamp="2" :tooltip="false">
							{{ item.subtitle }}
						</NEllipsis>
					</div>
					<div class="absolute bottom-2 right-2">
						<NTooltip trigger="hover">
							<template #trigger>
								<SvgIcon icon="bi:robot" class="cursor-pointer text-2xl"
									:class="[{ 'text-[#38AACC]': item.canChat, 'text-gray-300': !item.canChat }]"
									@click="handleChat(item)" />
							</template>
							{{ $t('digitalPerson.talkToDigitalPerson') }}
						</NTooltip>
					</div>
				</NCard>
			</NGridItem>
		</NGrid>
	</div>
</template>
