from typing import Dict, Any, List

import tiktoken
from langchain_community.callbacks.openai_info import standardize_model_name, get_openai_token_cost_for_model
from langchain_core.callbacks import BaseCallbackHandler

enc = tiktoken.encoding_for_model("gpt-3.5-turbo-instruct")


class TokenMetricsCallbackHandler(BaseCallbackHandler):
	"""
	Callback Handler for keeping detailed metrics on prompts.
	"""
	prompt_tokens = 0
	completion_tokens = 0
	completion_cost = 0
	prompt_cost = 0
	total_cost = 0.0

	# construct with the model name
	def __init__(self, model: str):
		if model.lower() == 'azure-jp-gpt3':
			model = 'gpt-3.5-turbo'
		self.model = model

	def __repr__(self) -> str:
		return (
			f"Tokens Used: {self.prompt_tokens + self.completion_tokens}\n"
			f"\tPrompt Tokens: {self.prompt_tokens}\n"
			f"\tCompletion Tokens: {self.completion_tokens}\n"
			f"Total Cost (USD): ${self.total_cost:f}\n"
			f"\tPrompt Cost (USD): ${self.prompt_cost:f}\n"
			f"\tCompletion Cost (USD): ${self.completion_cost:f}"
		)

	async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
		"""Count prompt token length."""
		self.prompt_tokens += len(enc.encode(prompts[0]))

	async def on_llm_new_token(self, token: str, **kwargs):
		"""Count output tokens."""
		self.completion_tokens += 1

	async def on_llm_end(self, response, **kwargs: Any) -> None:
		"""Calculate total token costs."""
		# model_name = standardize_model_name(response.llm_output.get("model_name", ""))
		# print(f"model_name: {model_name}")
		model_name = standardize_model_name(self.model)
		self.prompt_cost += get_openai_token_cost_for_model(model_name, self.prompt_tokens)
		self.completion_cost += get_openai_token_cost_for_model(model_name, self.completion_tokens, is_completion=True)
		self.total_cost = self.prompt_cost + self.total_cost
