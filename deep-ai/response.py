from enum import Enum


class Status(Enum):
	SUCCESS = "Success"
	ERROR = "Error"
	WARNING = "Warning"


class AiMode(Enum):
	MyFavorites = 'myfavorites'  # 收藏的Prompts等
	LocalAI = 'localai'
	OpenAIAssistants = 'openaiassistants'
	FeishuRag = 'feishu_rag'
	ToolsDocTranslator = 'toolsdoctranslator'
	Gemini = 'gemini'
	ChatExtChat = 'chatextchat'
	"""Chrome插件中的常规聊天，同ChatGPT"""
	ChatExtOnCallWithCSV = 'chatextoncall_csv'
	"""Chrome插件中的值班响应OnCall与csv聊天"""
	ChatExtOnCallWithFeishuRAG = 'chatextoncall_feishu_rag'
	"""Chrome插件中的值班响应OnCall，与FeishuRAG的文档知识库聊天"""
	ChatExtRead = 'chatextread'
	"""Chrome插件中的阅读，包括与页面聊天，总结页面摘要等"""
	ChatExtWrite= 'chatextwrite'
	"""Chrome插件中的写作撰写"""
	ChatLLM = 'chatllm'
	"""LLM大模型聊天，包括各种模型"""
	ChatExtGrammar = 'chatextgrammar'
	"""Chrome插件中的语法"""


class ApiResponse:
	def __init__(self, status: Status, message: str, data: object):
		self.status = status
		self.message = message
		self.data = data
