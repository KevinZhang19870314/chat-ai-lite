"""Hooks to modify the bot's language and embedding models.

Here is a collection of methods to hook into the settings of the Large Language Model and the Embedder.

"""
import os
from typing import Dict

from langchain.llms.base import BaseLLM
from langchain_community.llms import Cohere, OpenAI, AzureOpenAI, HuggingFaceHub
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI, AzureChatOpenAI

import factory.embedder as embedders
import factory.llm as llms
from mad_hatter.decorators import hook


class Settings:
	def __init__(self, name: str, value: Dict):
		self.name = name
		self.value = value


@hook(priority=0)
def get_language_model(model_name: str, bot) -> BaseLLM:
	if model_name.lower().startswith('gpt-'):
		selected_llm = Settings(name="llm_selected", value={"name": "LLMOpenAIChatConfig"})
		selected_llm_class = selected_llm.value["name"]
		selected_llm_config = Settings(
			name=selected_llm_class,
			value={
				"model_name": model_name,
			}
		)
	elif model_name.lower().startswith("azure-"):
		selected_llm = Settings(name="llm_selected", value={"name": "LLMAzureChatOpenAIConfig"})
		selected_llm_class = selected_llm.value["name"]
		selected_llm_config = Settings(
			name=selected_llm_class,
			value={
				"azure_deployment": f"{model_name[6:]}",
				"api_version": "2023-05-15",
			}
		)
	elif model_name.lower() == 'gemini-pro':
		selected_llm = Settings(name="llm_selected", value={"name": "LLMGoogleGeminiProConfig"})
		selected_llm_class = selected_llm.value["name"]
		selected_llm_config = Settings(
			name=selected_llm_class,
			value={
				"model": model_name,
				"google_api_key": os.getenv('GEMINI_API_KEY'),
				# "convert_system_message_to_human": True,
				# "transport": 'rest',
				# "client_options": {"api_endpoint": os.getenv('GEMINI_API_ENDPOINT')},
			}
		)
	elif model_name.lower().startswith("mistralai"):
		selected_llm = Settings(name="llm_selected", value={"name": "LLMDeepInfraConfig"})
		selected_llm_class = selected_llm.value["name"]
		selected_llm_config = Settings(
			name=selected_llm_class,
			value={
				"openai_api_key": os.getenv('DEEPINFRA_API_TOKEN'),
				"openai_api_base": "https://api.deepinfra.com/v1/openai",
				"model_name": model_name,
				"temperature": 0.7,
				"model_kwargs": {"top_p": 0.9},
				"max_tokens": 4096,
			}
		)
	elif model_name.lower().startswith("moonshot"):
		selected_llm = Settings(name="llm_selected", value={"name": "LLMMoonShotConfig"})
		selected_llm_class = selected_llm.value["name"]
		selected_llm_config = Settings(
			name=selected_llm_class,
			value={
				"openai_api_key": os.getenv('MOONSHOT_API_KEY'),
				"openai_api_base": "https://api.moonshot.cn/v1",
				"model_name": model_name,
				"temperature": 0.7,
				"model_kwargs": {"top_p": 0.9},
				"max_tokens": 4096,
			}
		)
	elif model_name.lower().startswith("hf/") and len(model_name) > 3:
		selected_llm = Settings(name="llm_selected", value={"name": "LLMHuggingFaceEndpointConfig"})
		selected_llm_class = selected_llm.value["name"]
		selected_llm_config = Settings(
			name=selected_llm_class,
			value={
				"endpoint_url": f"https://api-inference.huggingface.co/models/{model_name[3:]}",
				"huggingfacehub_api_token": os.getenv("HUGGINGFACEHUB_API_TOKEN"),
				"max_new_tokens": 1024,
				"top_k": 10,
				"top_p": 0.95,
				"typical_p": 0.95,
				"temperature": 0.01,
				"repetition_penalty": 1.03,
			}
		)
	elif model_name.lower().startswith("claude-"):
		selected_llm = Settings(name="llm_selected", value={"name": "LLMAnthropicConfig"})
		selected_llm_class = selected_llm.value["name"]
		selected_llm_config = Settings(
			name=selected_llm_class,
			value={
				"model_name": model_name,
			}
		)
	elif model_name.lower().startswith("qwen-"):
		selected_llm = Settings(name="llm_selected", value={"name": "LLMTongyiQwenConfig"})
		selected_llm_class = selected_llm.value["name"]
		selected_llm_config = Settings(
			name=selected_llm_class,
			value={
				"model_name": model_name,
			}
		)
	else:
		selected_llm = Settings(name="llm_selected", value={"name": "LLMOpenAIChatConfig"})
		selected_llm_class = selected_llm.value["name"]
		selected_llm_config = Settings(
			name=selected_llm_class,
			value={
				"model_name": model_name,
			}
		)

	# get LLM factory class
	FactoryClass = getattr(llms, selected_llm_class)

	llm = FactoryClass.get_llm_from_config(selected_llm_config.value)

	return llm


@hook(priority=0)
def get_language_embedder(bot):
	# Embedding LLM
	# OpenAI embedder
	if type(bot.llm) in [OpenAI, ChatOpenAI]:
		if bot.llm.model_name.startswith("mistralai"):
			embedder = embedders.EmbedderDeepInfraConfig.get_embedder_from_config(
				{
						"model_id": "BAAI/bge-base-en-v1.5",
						"deepinfra_api_token": os.getenv('DEEPINFRA_API_TOKEN'),
				}
			)
		else:
			embedder = embedders.EmbedderOpenAIConfig.get_embedder_from_config(
				{
					"openai_api_key": bot.llm.openai_api_key,
					# "model": "text-embedding-3-large",
					# "model": "text-embedding-3-small",
					"model": "text-embedding-ada-002",
				}
			)
	# Azure
	elif type(bot.llm) in [AzureOpenAI, AzureChatOpenAI]:
		embedder = embedders.EmbedderAzureOpenAIConfig.get_embedder_from_config(
			{
				"azure_deployment": "jp-ada",   # embeddings deployment name
				"api_version": "2023-05-15",
			}
		)
	# Cohere
	elif type(bot.llm) in [Cohere]:
		embedder = embedders.EmbedderCohereConfig.get_embedder_from_config(
			{
				"cohere_api_key": bot.llm.cohere_api_key,
				"model": "embed-multilingual-v2.0",
				# Now the best model for embeddings is embed-multilingual-v2.0
			}
		)
	# HuggingFace
	elif type(bot.llm) in [HuggingFaceHub]:
		embedder = embedders.EmbedderHuggingFaceHubConfig.get_embedder_from_config(
			{
				"huggingfacehub_api_token": bot.llm.huggingfacehub_api_token,
				"repo_id": "sentence-transformers/all-mpnet-base-v2",
			}
		)
	elif type(bot.llm) in [ChatGoogleGenerativeAI]:
		embedder = embedders.EmbedderGoogleGeminiProConfig.get_embedder_from_config(
			{
				"model": "models/embedding-001",
				"google_api_key": os.getenv('GEMINI_API_KEY'),
				"transport": 'rest',
				"client_options": {"api_endpoint": os.getenv('GEMINI_API_ENDPOINT')},
			}
		)
	else:
		embedder = embedders.EmbedderFakeConfig.get_embedder_from_config(
			{"size": 1536}  # mock openai embedding size
		)

	return embedder
