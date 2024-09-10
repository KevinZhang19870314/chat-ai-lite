import json
from typing import Type

from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.llms import OpenAI, AzureOpenAI, Cohere, HuggingFaceHub, GooglePalm
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from pydantic import ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

from factory.custom_llm import LLMDefault, LLMCustom


# Base class to manage LLM configuration.
class LLMSettings(BaseSettings):
	# class instantiating the model
	_pyclass: Type = None

	# instantiate an LLM from configuration
	@classmethod
	def get_llm_from_config(cls, config):
		if cls._pyclass is None:
			raise Exception(
				"Language model configuration class has self._pyclass = None. "
				"Should be a valid LLM class"
			)
		return cls._pyclass.default(**config)


class LLMDefaultConfig(LLMSettings):
	_pyclass: Type = LLMDefault
	model_config = SettingsConfigDict(json_schema_extra={
		"name_human_readable": "Default Language Model",
		"description":
			"A dumb LLM just telling that the Bot is not configured. "
			"There will be a nice LLM here "
			"once consumer hardware allows it.",
	})


class LLMCustomConfig(LLMSettings):
	url: str
	auth_key: str = "optional_auth_key"
	options: str = "{}"
	_pyclass: Type = LLMCustom

	# instantiate Custom LLM from configuration
	@classmethod
	def get_llm_from_config(cls, config):
		options = config["options"]
		# options are inserted as a string in the admin
		if isinstance(options, str):
			if options != "":
				config["options"] = json.loads(options)
			else:
				config["options"] = {}

		return cls._pyclass.default(**config)

	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "Custom LLM",
		"description": "LLM on a custom endpoint. see docs for examples.",
	})


class LLMOpenAIChatConfig(LLMSettings):
	# openai_api_key: str
	# model_name: str = "gpt-3.5-turbo"
	_pyclass: Type = ChatOpenAI
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "OpenAI ChatGPT",
		"description": "Chat model from OpenAI",
	})


class LLMOpenAIConfig(LLMSettings):
	openai_api_key: str
	# model_name: str = "text-davinci-003"
	_pyclass: Type = OpenAI
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "OpenAI GPT-3",
		"description": "OpenAI GPT-3. More expensive but also more flexible than ChatGPT.",
	})


# https://learn.microsoft.com/en-gb/azure/cognitive-services/openai/reference#chat-completions
class LLMAzureChatOpenAIConfig(LLMSettings):
	openai_api_key: str
	# model_name: str = "gpt-35-turbo"  # or gpt-4, use only chat models !
	openai_api_base: str
	openai_api_type: str = "azure"
	# Dont mix api versions https://github.com/hwchase17/langchain/issues/4775
	openai_api_version: str = "2023-05-15"

	deployment_name: str

	_pyclass: Type = AzureChatOpenAI
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "Azure OpenAI Chat Models",
		"description": "Chat model from Azure OpenAI",
	})


# https://python.langchain.com/en/latest/modules/models/llms/integrations/azure_openai_example.html
class LLMAzureOpenAIConfig(LLMSettings):
	openai_api_key: str
	openai_api_base: str
	api_type: str = "azure"
	# https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference#completions
	# Current supported versions 2022-12-01, 2023-03-15-preview, 2023-05-15
	# Don't mix api versions: https://github.com/hwchase17/langchain/issues/4775
	api_version: str = "2023-05-15"
	deployment_name: str = "text-davinci-003"
	# model_name: str = "text-davinci-003"  # Use only completion models !

	_pyclass: Type = AzureOpenAI
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "Azure OpenAI Completion models",
		"description": "Configuration for Cognitive Services Azure OpenAI",
	})


class LLMCohereConfig(LLMSettings):
	cohere_api_key: str
	model: str = "command"
	_pyclass: Type = Cohere
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "Cohere",
		"description": "Configuration for Cohere language model",
	})


class LLMHuggingFaceHubConfig(LLMSettings):
	# model_kwargs = {
	#    "generation_config": {
	#        "min_new_tokens": 10000
	#    }
	# }
	repo_id: str
	huggingfacehub_api_token: str
	_pyclass: Type = HuggingFaceHub
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "HuggingFace Hub",
		"description": "Configuration for HuggingFace Hub language models",
	})


class LLMHuggingFaceEndpointConfig(LLMSettings):
	endpoint_url: str
	huggingfacehub_api_token: str
	_pyclass: Type = HuggingFaceEndpoint
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "HuggingFace Endpoint",
		"description":
			"Configuration for HuggingFace Endpoint language models",
	})


class LLMAnthropicConfig(LLMSettings):
	anthropic_api_key: str
	model: str = "claude-3-sonnet-20240229"
	_pyclass: Type = ChatAnthropic
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "Anthropic",
		"description": "Configuration for Anthropic language Model",
	})


class LLMGooglePalmConfig(LLMSettings):
	google_api_key: str
	# model_name: str = "models/text-bison-001"
	_pyclass: Type = GooglePalm
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "Google PaLM",
		"description": "Configuration for Google PaLM language model",
	})


class LLMGoogleGeminiProConfig(LLMSettings):
	google_api_key: str
	model: str = "gemini-pro"
	_pyclass: Type = ChatGoogleGenerativeAI
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "Google Gemini Pro",
		"description": "Configuration for Google Gemini Pro language model",
	})


class LLMDeepInfraConfig(LLMSettings):
	google_api_key: str
	# model_id: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
	# DeepInfra offer OpenAI compatible API
	_pyclass: Type = ChatOpenAI
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "DeepInfra",
		"description": "Configuration for DeepInfra language model",
	})


class LLMMoonShotConfig(LLMSettings):
	# model_id: str = "moonshot-v1-8k"
	# MoonShot offer OpenAI compatible API
	_pyclass: Type = ChatOpenAI
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "MoonShot",
		"description": "Configuration for MoonShot language model",
	})


class LLMTongyiQwenConfig(LLMSettings):
	_pyclass: Type = ChatTongyi
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "Tongyi Qwen",
		"description": "Configuration for Tongyi Qwen language model",
	})


SUPPORTED_LANGUAGE_MODELS = [
	LLMDefaultConfig,
	LLMCustomConfig,
	LLMOpenAIChatConfig,
	LLMOpenAIConfig,
	LLMCohereConfig,
	LLMHuggingFaceHubConfig,
	LLMHuggingFaceEndpointConfig,
	LLMAzureOpenAIConfig,
	LLMAzureChatOpenAIConfig,
	LLMAnthropicConfig,
	LLMGooglePalmConfig,
	LLMGoogleGeminiProConfig,
	LLMDeepInfraConfig,
	LLMMoonShotConfig
]

# LLM_SCHEMAS contains metadata to let any client know
# which fields are required to create the language model.
LLM_SCHEMAS = {}
for config_class in SUPPORTED_LANGUAGE_MODELS:
	schema = config_class.schema()

	# useful for clients in order to call the correct config endpoints
	schema["languageModelName"] = schema["title"]
	LLM_SCHEMAS[schema["title"]] = schema
