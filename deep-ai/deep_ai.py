import json
import os
import traceback
from copy import deepcopy
from dataclasses import asdict

from langchain_community.vectorstores.faiss import FAISS

from black_hole import BlackHole
from db.crud_user import redis_client
from db.database import create_db_and_tables, get_db_session
from infrastructure.feishu import Feishu
from log import log
from looking_glass.agent_manager import AgentManager
from mad_hatter.mad_hatter import MadHatter
from memory.long_term_memory import LongTermMemory
from memory.working_memory import WorkingMemory


class DeepAI:
	def __init__(self):
		# access to DB
		self.load_db()

		# bootstrap the bot!
		self.bootstrap()

		# queue of bot messages not directly related to last user input
		# i.e. finished uploading a file
		self.web_socket_notifications = []

	def load_db(self):
		# if there is no db, create it
		create_db_and_tables()
		# access db from instance
		self.db = get_db_session
		self.email = None

	def bootstrap(self):
		self.upload_path = os.getenv("UPLOAD_FILE_PATH")
		self.common_storage = os.getenv('COMMON_STORAGE')

		# bootstrap the bot!
		# re-instantiate MadHatter (reloads all plugins' hooks and tools)
		self.mad_hatter = MadHatter(self)

		# allows plugins to do something before bot components are loaded
		self.mad_hatter.execute_hook("before_bot_bootstrap")

		# load LLM and embedder
		self.load_natural_language()

		# Load memories (vector collections and working_memory)
		self.load_memory()

		# After memory is loaded, we can get/create tools embeddings
		self.mad_hatter.embed_tools()

		# Agent manager instance (for reasoning)
		self.agent_manager = AgentManager(self)

		# Rabbit Hole Instance
		self.black_hole = BlackHole(self)

		# 飞书api初始化
		app_id = os.getenv('FEISHU_APP_ID')
		app_secret = os.getenv('FEISHU_APP_SECRET')
		self.feishu = Feishu(app_id, app_secret)

		# allows plugins to do something after the bot bootstrap is complete
		self.mad_hatter.execute_hook("after_bot_bootstrap")

	def load_natural_language(self):
		# LLM and embedder
		self.llm = self.mad_hatter.execute_hook("get_language_model", "gpt-3.5-turbo")
		self.embedder = self.mad_hatter.execute_hook("get_language_embedder")

		# set the default prompt settings
		self.default_prompt_settings = {
			"prefix": "",
			"use_declarative_memory": True,
			"use_procedural_memory": True,
		}

	def rebuild_llm_embedder(self, model_name: str):
		self.llm = self.mad_hatter.execute_hook("get_language_model", model_name)
		self.embedder = self.mad_hatter.execute_hook("get_language_embedder")
		self.memory.vectors.refresh_embedder(self.embedder)

		return self.llm, self.embedder

	def load_memory(self):
		# Memory
		vector_memory_config = {"bot": self, "verbose": False}
		self.memory = LongTermMemory(vector_memory_config=vector_memory_config)
		self.working_memory = WorkingMemory()

	def recall_relevant_memories_to_working_memory(self, index_name, folder_path, refs_uuid: str):
		user_message = self.working_memory["user_message_json"]["text"]
		prompt_settings = self.working_memory["user_message_json"]["prompt_settings"]

		# We may want to search in memory
		memory_query_text = self.mad_hatter.execute_hook("bot_recall_query", user_message)
		log(f'Recall query: "{memory_query_text}"')

		# Embed recall query
		self.working_memory["memory_query"] = memory_query_text

		# hook to do something before recall begins
		self.mad_hatter.execute_hook("before_bot_recalls_memories")

		# Setting default recall configs for each memory
		default_declarative_recall_config = {
			"k": 2,
			"threshold": 0.55,
			"metadata": None,
		}

		default_procedural_recall_config = {
			"k": 2,
			"threshold": 0.55,
			"metadata": None,
		}

		# hooks to change recall configs for each memory
		recall_configs = [
			self.mad_hatter.execute_hook("before_bot_recalls_declarative_memories", default_declarative_recall_config),
			self.mad_hatter.execute_hook("before_bot_recalls_procedural_memories", default_procedural_recall_config)
		]

		# declarative: chat history memories
		# procedural: tools and hooks
		if 'feishu_rag' in folder_path:
			memory_types = ["declarative"]
		else:
			memory_types = ["declarative", "procedural"]

		for config, memory_type in zip(recall_configs, memory_types):
			setting = f"use_{memory_type}_memory"
			memory_key = f"{memory_type}_memories"

			if prompt_settings[setting]:
				# recall relevant memories
				if memory_type == "procedural":
					vector_memory: FAISS = self.memory.vectors.faiss_db(memory_type, folder_path)
				else:
					vector_memory: FAISS = self.memory.vectors.faiss_db(index_name, folder_path)

				memories = vector_memory.similarity_search_with_score(
					query=memory_query_text,
					k=config["k"],
					score_threshold=config["threshold"]
				)
			else:
				memories = []

			# 飞书引用特殊逻辑
			refs = []
			for memory in memories:
				log(f"score: {memory[1]} - content: {memory[0]}")
				if memory[0].metadata.get("node"):
					refs.append(asdict(memory[0].metadata.get("node")))

			if len(refs) > 0:
				redis_client.set(refs_uuid, json.dumps(refs), ex=5 * 60)  # 5 minutes expiration
			self.working_memory[memory_key] = memories

		# hook to modify/enrich retrieved memories
		self.mad_hatter.execute_hook("after_bot_recalled_memories", memory_query_text)

	def store_new_message_in_working_memory(self, user_message_json):
		# store last message in working memory
		self.working_memory["user_message_json"] = user_message_json

		prompt_settings = deepcopy(self.default_prompt_settings)

		# override current prompt_settings with prompt settings sent via api (if any)
		prompt_settings.update(user_message_json.get("prompt_settings", {}))

		self.working_memory["user_message_json"]["prompt_settings"] = prompt_settings

	def format_agent_input(self):
		chat_history = self.working_memory["user_message_json"]["chat_history"]

		# format memories to be inserted in the prompt
		declarative_memory_formatted_content = self.mad_hatter.execute_hook(
			"agent_prompt_declarative_memories",
			self.working_memory["declarative_memories"],
		)

		# format conversation history to be inserted in the prompt
		conversation_history_formatted_content = self.mad_hatter.execute_hook(
			"agent_prompt_chat_history", chat_history
		)

		return {
			"input": self.working_memory["user_message_json"]["text"],
			"declarative_memory": declarative_memory_formatted_content,
			"chat_history": conversation_history_formatted_content,
		}

	def get_base_path(self):
		"""Allows the Bot expose the base path."""
		# return os.getcwd()
		return ""

	def get_plugin_path(self):
		"""Allows the Bot expose the plugins path."""
		return os.path.join(self.get_base_path(), "storage/plugins/")

	def __call__(self, user_message_json, index_name, folder_path=None):
		folder_path = folder_path if folder_path else self.common_storage
		log(f"user_message_json: {user_message_json}", "DEBUG")
		log(f"index_folder_path: {folder_path}", "DEBUG")
		log(f"index_name(knowledge_base_id): {index_name}", "DEBUG")

		# recall use_plugins to memory by current knowledge_base_id
		self.mad_hatter.sync_hooks_and_tools_when_chat(index_name)

		# hook to modify/enrich user input
		user_message_json = self.mad_hatter.execute_hook("before_bot_reads_message", user_message_json)

		# store user_message_json in working memory
		# it contains the new message, prompt settings and other info plugins may find useful
		self.store_new_message_in_working_memory(user_message_json)

		# recall procedural and declarative memories from vector collections and store them in working_memory
		try:
			self.recall_relevant_memories_to_working_memory(index_name, folder_path, '')
		except Exception as e:
			log(e)
			traceback.print_exc()

			return {
				"error": False,
				"content": str(e),
				"why": {},
			}

		# prepare input to be passed to the agent executor. Info will be extracted from working memory
		agent_input = self.format_agent_input()

		# reply with agent
		try:
			bot_message = self.agent_manager.execute_agent(agent_input)
		except Exception as e:
			# This error happens when the LLM
			#   does not respect prompt instructions.
			# We grab the LLM outptu here anyway, so small and
			#   non instruction-fine-tuned models can still be used.
			error_description = str(e)
			log("LLM does not respect prompt instructions", "ERROR")
			log(error_description, "ERROR")
			traceback.print_exc()
			if not "Could not parse LLM output: `" in error_description:
				raise e

			unparsable_llm_output = error_description.replace("Could not parse LLM output: `", "").replace("`", "")
			bot_message = {
				"input": agent_input["input"],
				"intermediate_steps": [],
				"output": unparsable_llm_output
			}

		log("bot_message:", "DEBUG")
		log(bot_message, "DEBUG")

		# build data structure for output (response and why with memories)
		declarative_report = [dict(d[0]) | {"score": float(d[1])} for d in self.working_memory["declarative_memories"]]
		if "procedural_memories" in self.working_memory:
			procedural_report = [dict(d[0]) | {"score": float(d[1])} for d in self.working_memory["procedural_memories"]]
		else:
			procedural_report = []

		final_output = {
			"error": False,
			"type": "chat",
			"content": bot_message.get("output"),
			"why": {
				"input": bot_message.get("input"),
				"intermediate_steps": bot_message.get("intermediate_steps"),
				"memory": {
					"declarative": declarative_report,
					"procedural": procedural_report,
				},
			},
		}

		final_output = self.mad_hatter.execute_hook("before_bot_sends_message", final_output)

		return final_output

	def stream(self, user_message_json, index_name, refs_uuid: str, folder_path=None):
		folder_path = folder_path if folder_path else self.common_storage
		log(f"user_message_json: {user_message_json}", "DEBUG")
		log(f"index_folder_path: {folder_path}", "DEBUG")
		log(f"index_name(knowledge_base_id): {index_name}", "DEBUG")

		# recall use_plugins to memory by current knowledge_base_id
		self.mad_hatter.sync_hooks_and_tools_when_chat(index_name)

		# hook to modify/enrich user input
		user_message_json = self.mad_hatter.execute_hook("before_bot_reads_message", user_message_json)

		# store user_message_json in working memory
		# it contains the new message, prompt settings and other info plugins may find useful
		self.store_new_message_in_working_memory(user_message_json)

		# recall procedural and declarative memories from vector collections and store them in working_memory
		try:
			self.recall_relevant_memories_to_working_memory(index_name, folder_path, refs_uuid)
		except Exception as e:
			traceback.print_exc()
			raise e

		# prepare input to be passed to the agent executor. Info will be extracted from working memory
		agent_input = self.format_agent_input()

		# reply with agent
		try:
			bot_message_interator = self.agent_manager.execute_agent_stream(agent_input)
			return bot_message_interator
		except Exception as e:
			traceback.print_exc()
			raise e

