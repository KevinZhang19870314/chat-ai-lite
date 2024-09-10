import { TextToImage } from "@/models/chat.model"

export interface TextToImageStore {
	imageUrl: string
	records: TextToImage[]
}
