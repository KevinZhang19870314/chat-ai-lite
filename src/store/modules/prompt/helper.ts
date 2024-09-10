import type { Prompt } from '@/models/chat.model'
import { ss } from '@/utils/storage'

const LOCAL_NAME = 'promptStore'

export interface PromptStore {
  promptList: Prompt[]
}

export function getLocalPromptList(): PromptStore {
  const promptStore: PromptStore | undefined = ss.get(LOCAL_NAME)
  return promptStore ?? { promptList: [] }
}

export function setLocalPromptList(promptStore: PromptStore): void {
  ss.set(LOCAL_NAME, promptStore)
}
