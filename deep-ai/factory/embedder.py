from typing import Type

from langchain_community.embeddings import FakeEmbeddings, CohereEmbeddings, HuggingFaceHubEmbeddings, \
	DeepInfraEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings
from pydantic import ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


# Base class to manage LLM configuration.
class EmbedderSettings(BaseSettings):
	# class instantiating the embedder
	_pyclass: None

	# instantiate an Embedder from configuration
	@classmethod
	def get_embedder_from_config(cls, config):
		if cls._pyclass is None:
			raise Exception(
				"Embedder configuration class has self._pyclass = None. Should be a valid Embedder class"
			)
		return cls._pyclass.default(**config)


class EmbedderFakeConfig(EmbedderSettings):
	size: int = 1536
	_pyclass: Type = FakeEmbeddings
	model_config = SettingsConfigDict(json_schema_extra={
		"name_human_readable": "Default Embedder",
		"description": "Configuration for default embedder. It just outputs random numbers XD",
	})


class EmbedderOpenAIConfig(EmbedderSettings):
	openai_api_key: str
	model: str = "text-embedding-3-small"
	_pyclass: Type = OpenAIEmbeddings
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "OpenAI Embedder",
		"description": "Configuration for OpenAI embeddings",
	})


# https://python.langchain.com/en/latest/_modules/langchain/embeddings/openai.html#OpenAIEmbeddings
class EmbedderAzureOpenAIConfig(EmbedderSettings):
	openai_api_key: str
	model: str
	openai_api_base: str
	api_type: str
	api_version: str
	deployment: str

	_pyclass: Type = AzureOpenAIEmbeddings
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "Azure OpenAI Embedder",
		"description": "Configuration for Azure OpenAI embeddings",
	})


class EmbedderCohereConfig(EmbedderSettings):
	cohere_api_key: str
	model: str = "embed-multilingual-v2.0"
	_pyclass: Type = CohereEmbeddings
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "Cohere Embedder",
		"description": "Configuration for Cohere embeddings",
	})


class EmbedderHuggingFaceHubConfig(EmbedderSettings):
	repo_id: str = "sentence-transformers/all-mpnet-base-v2"
	huggingfacehub_api_token: str
	_pyclass: Type = HuggingFaceHubEmbeddings
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "HuggingFace Hub Embedder",
		"description": "Configuration for HuggingFace Hub embeddings",
	})


class EmbedderGoogleGeminiProConfig(EmbedderSettings):
	openai_api_key: str
	model: str = "models/embedding-001"
	_pyclass: Type = GoogleGenerativeAIEmbeddings
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "Google Gemini Pro Embedder",
		"description": "Configuration for Google Gemini Pro embeddings",
	})


class EmbedderDeepInfraConfig(EmbedderSettings):
	# model_id: str = "sentence-transformers/clip-ViT-B-32"
	_pyclass: Type = DeepInfraEmbeddings
	model_config = ConfigDict(json_schema_extra={
		"name_human_readable": "DeepInfra Embedder",
		"description": "Configuration for DeepInfra embeddings",
	})


SUPPORTED_EMBEDDING_MODELS = [
	EmbedderFakeConfig,
	EmbedderOpenAIConfig,
	EmbedderAzureOpenAIConfig,
	EmbedderCohereConfig,
	EmbedderHuggingFaceHubConfig,
	EmbedderGoogleGeminiProConfig,
	EmbedderDeepInfraConfig,
]

# EMBEDDER_SCHEMAS contains metadata to let any client know which fields are required to create the language embedder.
EMBEDDER_SCHEMAS = {}
for config_class in SUPPORTED_EMBEDDING_MODELS:
	schema = config_class.schema()

	# useful for clients in order to call the correct config endpoints
	schema["languageEmbedderName"] = schema["title"]
	EMBEDDER_SCHEMAS[schema["title"]] = schema
