import dataclasses
from typing import Optional

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

DEFAULT_SYSTEM_PROMPT = "You are ChatGPT, a large language model trained by OpenAI. Follow the user's instructions carefully. Respond using markdown."


class UserRole:
	AI = "AI"
	HUMAN = "Human"


class ChatHistory(BaseModel):
	who: str
	message: str


class UserMessage(BaseModel):
	text: str
	knowledge_base_id: str
	chat_history: list[ChatHistory]


class OpenAIRole:
	SYSTEM = "system"
	ASSISTANT = "assistant"
	USER = "user"


class GeminiRole:
	MODEL = "model"
	USER = "user"


# class Message(BaseModel):
# 	role: constr(regex=f"^({Role.ASSISTANT}|{Role.USER}|{Role.SYSTEM})$")
# 	content: str


class OpenAIChatRequest(BaseModel):
	messages: list[ChatCompletionMessageParam]
	max_tokens: int
	temperature: float
	model: Optional[str] = None
	uuid: Optional[int] = None
	top_p: Optional[int] = None
	presence_penalty: Optional[int] = None
	frequency_penalty: Optional[int] = None
	ai_mode: Optional[str] = None


class GeminiChatRequest(BaseModel):
	messages: list | None = None


class UpdatePayload(BaseModel):
	id: str
	fields: dict


class PandasAIMessage(BaseModel):
	is_user: Optional[bool] = None
	message: str


class PandasAIChatRequest(BaseModel):
	filename: str
	messages: list[PandasAIMessage]
	model: Optional[str] = None
	max_tokens: Optional[int] = None
	temperature: Optional[float] = None
	uuid: Optional[int] = None
	top_p: Optional[int] = None
	presence_penalty: Optional[int] = None
	frequency_penalty: Optional[int] = None


class ChatWithPageRequest(BaseModel):
	model: Optional[str] = None
	text: str
	query: str


class SummarizeWithPageRequest(BaseModel):
	model: Optional[str] = None
	text: str


@dataclasses.dataclass
class TextToVideoPayload(BaseModel):
	video_subject: str
	is_global: Optional[bool] = None
	video_script: Optional[str] = ""
	video_terms: Optional[str] = None
	video_aspect: Optional[str] = "9:16"
	video_concat_mode: Optional[str] = "random"
	video_clip_duration: Optional[int] = 5
	video_count: Optional[int] = 1
	video_language: Optional[str] = ""
	voice_name: Optional[str] = ""
	voice_volume: Optional[int] = 1
	bgm_type: Optional[str] = "random"
	bgm_file: Optional[str] = ""
	bgm_volume: Optional[float] = 0.2
	subtitle_enabled: Optional[bool] = True
	subtitle_position: Optional[str] = "bottom"
	font_name: Optional[str] = "STHeitiMedium.ttc"
	text_fore_color: Optional[str] = "#FFFFFF"
	text_background_color: Optional[str] = "transparent"
	font_size: Optional[int] = 60
	stroke_color: Optional[str] = "#000000"
	stroke_width: Optional[float] = 1.5
	n_threads: Optional[int] = 2
	paragraph_number: Optional[int] = 1


class GPTSoVITSTTSRequest(BaseModel):
	text: str = None
	text_lang: str = None
	ref_audio_path: str = None
	prompt_lang: str = None
	prompt_text: str = ""
	top_k: int = 5
	top_p: float = 1
	temperature: float = 1
	text_split_method: str = "cut5"
	batch_size: int = 1
	batch_threshold: float = 0.75
	split_bucket: bool = True
	speed_factor: float = 1.0
	fragment_interval: float = 0.3
	seed: int = -1
	media_type: str = "wav"
	streaming_mode: bool = False
	parallel_infer: bool = True
	repetition_penalty: float = 1.35
	tts_infer_yaml_path: str = "GPT_SoVITS/configs/tts_infer.yaml"
	"""推理时需要加载的声音模型的yaml配置文件路径，如：GPT_SoVITS/configs/tts_infer.yaml"""


class GPTSoVITSTTSPayload(BaseModel):
	text: str = None
	text_lang: str = None
	digital_person: str = None
	"""目前支持：jack，liyunlong，morgan"""


class TextToImagePayload(BaseModel):
	model: str
	query: str
	size: Optional[str] = None
	is_global: Optional[bool] = True
