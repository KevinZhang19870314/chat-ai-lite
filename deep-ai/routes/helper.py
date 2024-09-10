import asyncio
import random
import string
from typing import List, Any, Dict

import tiktoken
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import LLMResult
from langchain_community.callbacks import get_openai_callback
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import ChatOpenAI

from deep_ai import DeepAI
from log import log
from memory.working_memory import WorkingMemory


async def get_ask_answer(
	question: str,
	db: FAISS,
	working_memory: WorkingMemory,
	session_id: str = None
):
	# If chat history exists, load history first
	if session_id == '' or session_id == 'null':
		session_id = None
	chat_history = []
	if session_id is not None and session_id in working_memory:
		chat_history = working_memory[session_id]

	# fetch_k: Number of Documents to fetch to pass to MMR algorithm.
	# k: Number of Documents to return. Defaults to 4.
	retriever = db.as_retriever(
		distance_metric='cos', fetch_k=20, maximal_marginal_relevance=True, k=4)
	model = ChatOpenAI(model_name='gpt-3.5-turbo')
	qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever, verbose=True)
	with get_openai_callback() as cb:
		# result = qa({"question": question, "chat_history": chat_history})
		result = await qa.acall({"question": question, "chat_history": chat_history}, callbacks=[MyCustomAsyncHandler()])
		print(cb)

	answer = result['answer']

	# add chat history per user chat session
	if session_id is not None:
		chat_history.append((question, answer))
		working_memory[session_id] = chat_history

	return answer


async def generate(answer: str, delay: float = 0.08):
	chunk_size = 10
	num_chunks = (len(answer) + chunk_size - 1) // chunk_size
	for i in range(num_chunks):
		chunk_start = i * chunk_size
		chunk_end = (i + 1) * chunk_size
		chunk = answer[chunk_start:chunk_end]
		response_body = f"{chunk}"
		yield response_body.encode()
		await asyncio.sleep(delay)


def get_bot(bot):
	if isinstance(bot, DeepAI):
		return bot
	else:
		raise Exception("Got DeepAI instance failed!")


# Reference: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
def num_tokens_from_messages(messages, completion=False, model="gpt-3.5-turbo"):
	"""Return the number of tokens used by a list of messages."""
	try:
		encoding = tiktoken.encoding_for_model(model)
	except KeyError:
		print("Warning: model not found. Using cl100k_base encoding.")
		encoding = tiktoken.get_encoding("cl100k_base")
	if model in {
		"gpt-3.5-turbo-0613",
		"gpt-3.5-turbo-16k-0613",
		"gpt-4-0314",
		"gpt-4-32k-0314",
		"gpt-4-0613",
		"gpt-4-32k-0613",
	}:
		tokens_per_message = 3
		tokens_per_name = 1
	elif model == "gpt-3.5-turbo-0301":
		tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
		tokens_per_name = -1  # if there's a name, the role is omitted
	elif "gpt-3.5-turbo" in model:
		print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
		return num_tokens_from_messages(messages, completion, model="gpt-3.5-turbo-0613")
	elif "gpt-4" in model:
		print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
		return num_tokens_from_messages(messages, completion, model="gpt-4-0613")
	else:
		raise NotImplementedError(
			f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
		)

	if completion:
		num_tokens = len(encoding.encode(messages[0]["content"]))
	else:
		num_tokens = 0
		for message in messages:
			num_tokens += tokens_per_message
			for key, value in message.items():
				num_tokens += len(encoding.encode(value))
				if key == "name":
					num_tokens += tokens_per_name
		num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
	return num_tokens


def openai_api_calculate_cost(usage, model="gpt-3.5-turbo"):
	pricing = {
		'gpt-3.5-turbo-0125': {
			'prompt': 0.0005,
			'completion': 0.0015,
		},
		'gpt-3.5-turbo-1106': {
			'prompt': 0.0010,
			'completion': 0.0020,
		},
		'gpt-3.5-turbo': {
			'prompt': 0.0015,
			'completion': 0.002,
		},
		'azure-jp-gpt3': {
			'prompt': 0.0015,
			'completion': 0.002,
		},
		'gpt-3.5-turbo-16k': {
			'prompt': 0.003,
			'completion': 0.004,
		},
		'gpt-4-0125-preview': {
			'prompt': 0.01,
			'completion': 0.03,
		},
		'gpt-4o': {
			'prompt': 0.005,
			'completion': 0.015,
		},
		'gpt-4-turbo': {
			'prompt': 0.01,
			'completion': 0.03,
		},
		'gpt-4-turbo-2024-04-09': {
			'prompt': 0.01,
			'completion': 0.03,
		},
		'gpt-4-1106-preview': {
			'prompt': 0.01,
			'completion': 0.03,
		},
		'gpt-4': {
			'prompt': 0.03,
			'completion': 0.06,
		},
		'gpt-4-32k': {
			'prompt': 0.06,
			'completion': 0.12,
		},
		'gpt-4-0613': {
			'prompt': 0.03,
			'completion': 0.06,
		},
		'gpt-4-32k-0613': {
			'prompt': 0.06,
			'completion': 0.12,
		},
		'jp-ada': {
			'prompt': 0.0001,
			'completion': 0.0001,
		},
		'text-embedding-ada-002': {
			'prompt': 0.0001,
			'completion': 0.0001,
		},
		'text-embedding-ada-002-v2': {
			'prompt': 0.0001,
			'completion': 0.0001,
		}
	}

	try:
		model_pricing = pricing[model]
	except KeyError:
		raise ValueError("Invalid model specified")

	prompt_costs = usage['prompt_tokens'] * model_pricing['prompt'] / 1000
	completion_costs = usage['completion_tokens'] * model_pricing['completion'] / 1000

	total_costs = prompt_costs + completion_costs
	log(f"Prompt costs: {prompt_costs}, Completion costs: {completion_costs}, Total costs: {total_costs}")

	return {
		"prompt_costs": prompt_costs,
		"completion_costs": completion_costs,
		"total_costs": total_costs
	}


def generate_password(length):
	chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
	password = [chars[random.randint(0, len(chars) - 1)] for _ in range(length)]
	return ''.join(password)


def gen_user_desc():
	descriptions = [
		"纵有万般心，亦须一念空。",
		"活在当下，快乐每一天。",
		"勇于追梦，不放弃任何可能。",
		"万事起于忽微，能者方能成大器。",
		"世事无常，唯有自强不息。",
		"知足常乐，做自己的幸福主宰。",
		"不忘初心，方得始终。",
		"人生自古谁无死，留取丹心照汗青。",
		"天道酬勤，努力无所不成。",
		"心存善良，做一个温暖的人。",
	]
	return random.choice(descriptions)


class MyCustomAsyncHandler(AsyncCallbackHandler):
	"""Async callback handler that can be used to handle callbacks from langchain."""

	async def on_llm_start(
		self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
	) -> None:
		"""Run when chain starts running."""
		for prompt in prompts:
			print(prompt)

	async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
		"""Run when chain ends running."""
		for gen in response.generations:
			for g in gen:
				print(f"LLMResult: {g.text}")
		print(response.llm_output)
