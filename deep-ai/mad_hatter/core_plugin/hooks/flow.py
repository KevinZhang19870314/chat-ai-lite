"""Hooks to modify the Bot's flow of execution.

Here is a collection of methods to hook into the Bot execution pipeline.

"""
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from log import log
from mad_hatter.decorators import hook


# Called before bot bootstrap
@hook(priority=0)
def before_bot_bootstrap(bot) -> None:
	"""Hook into the Bot start up.

	Bootstrapping is the process of loading the plugins, the natural language objects (e.g. the LLM),
	the memories, the *Agent Manager* and the *Rabbit Hole*.

	This hook allows to intercept such process and is executed in the middle of plugins and
	natural language objects loading.

	This hook can be used to set or store variables to be propagated to subsequent loaded objects.

	Args:
			bot: Cheshire Bot instance.
	"""
	return None


# Called after bot bootstrap
@hook(priority=0)
def after_bot_bootstrap(bot) -> None:
	"""Hook into the end of the Bot start up.

	Bootstrapping is the process of loading the plugins, the natural language objects (e.g. the LLM),
	the memories, the *Agent Manager* and the *Rabbit Hole*.

	This hook allows to intercept the end of such process and is executed right after the Bot has finished loading
	its components.

	This can be used to set or store variables to be shared further in the pipeline.

	Args:
			bot: Cheshire Bot instance.
	"""
	return None


# Called when a user message arrives.
# Useful to edit/enrich user input (e.g. translation)
@hook(priority=0)
def before_bot_reads_message(user_message_json: dict, bot) -> dict:
	"""Hook the incoming user's JSON dictionary.

	Allows to edit and enrich the incoming message received from the WebSocket connection.

	For instance, this hook can be used to translate the user's message before feeding it to the Bot.
	Another use case is to add custom keys to the JSON dictionary.

	The incoming message is a JSON dictionary with keys:
			{
					"text": message content
			}

	Args:
			user_message_json: JSON dictionary with the message received from the chat.
			bot: Cheshire Bot instance.

	Returns:
			Edited JSON dictionary that will be fed to the Bot.

			For example::

					{
							"text": "Hello Cheshire Bot!",
							"custom_key": True
					}

			where "custom_key" is a newly added key to the dictionary to store any data.

	"""
	return user_message_json


# Called just before the bot recalls memories.
@hook(priority=0)
def before_bot_recalls_memories(bot) -> None:
	"""Hook into semantic search in memories.

	Allows to intercept when the Bot queries the memories using the embedded user's input.

	The hook is executed just before the Bot searches for the meaningful context in both memories
	and stores it in the *Working Memory*.

	Args:
			bot: Cheshire Bot instance.
	"""
	return None


@hook(priority=0)
def before_bot_recalls_declarative_memories(declarative_recall_config: dict, bot) -> dict:
	"""Hook into semantic search in memories.

	Allows to intercept when the Bot queries the memories using the embedded user's input.

	The hook is executed just before the Bot searches for the meaningful context in both memories
	and stores it in the *Working Memory*.

	The hook return the values for maximum number (k) of items to retrieve from memory and the score threshold applied
	to the query in the vector memory (items with score under threshold are not retrieved)
	It also returns the embedded query (embedding) and the conditions on recall (metadata).

	Parameters
	----------
	declarative_recall_config: dict
			Dictionary with data needed to recall declarative memories
	bot : DeepAI
			DeepAI Bot instance.

	Returns
	-------
	declarative_recall_config: dict
			Edited dictionary that will be fed to the embedder.

	"""
	return declarative_recall_config


@hook(priority=0)
def before_bot_recalls_procedural_memories(procedural_recall_config: dict, bot) -> dict:
	"""Hook into semantic search in memories.

	Allows to intercept when the Bot queries the memories using the embedded user's input.

	The hook is executed just before the Bot searches for the meaningful context in both memories
	and stores it in the *Working Memory*.

	The hook return the values for maximum number (k) of items to retrieve from memory and the score threshold applied
	to the query in the vector memory (items with score under threshold are not retrieved)
	It also returns the embedded query (embedding) and the conditions on recall (metadata).

	Parameters
	----------
	procedural_recall_config: dict
			Dictionary with data needed to recall tools from procedural memory
	bot : DeepAI
			DeepAI Bot instance.

	Returns
	-------
	procedural_recall_config: dict
			Edited dictionary that will be fed to the embedder.

	"""
	return procedural_recall_config


# Called just before the Bot recalls memories.
@hook(priority=0)
def after_bot_recalls_memories(query: str, bot) -> None:
	"""Hook after semantic search in memories.

	The hook is executed just after the Bot searches for the meaningful context in both memories
	and stores it in the *Working Memory*.

	Parameters
	----------
	query : str
			Query used to retrieve memories.
	bot : DeepAI
			DeepAI Bot instance.

	"""
	return None


# What is the input to recall memories?
# Here you can do HyDE embedding, condense recent conversation or condition recall query on something else important to your AI
@hook(priority=0)
def bot_recall_query(user_message: str, bot) -> str:
	"""Hook the semantic search query.

	This hook allows to edit the user's message used as a query for context retrieval from memories.
	As a result, the retrieved context can be conditioned editing the user's message.

	Args:
			user_message: string with the text received from the user.
			bot: Cheshire Bot instance to exploit the Bot's methods.

	Returns:
			Edited string to be used for context retrieval in memory. The
			returned string is further stored in the Working Memory at
			`bot.working_memory["memory_query"]`
	"""

	# chat_history = []
	# raw_chat_history = bot.working_memory["user_message_json"]["chat_history"]
	# if raw_chat_history is None or len(raw_chat_history) == 0:
	# 	return user_message
	#
	# for item in raw_chat_history:
	# 	if item.who == "Human":
	# 		chat_history.append(HumanMessage(content=item.message))
	# 	elif item.who == "AI":
	# 		chat_history.append(AIMessage(content=item.message))
	# contextualize_q_system_prompt = """Given a chat history and the latest user question \
	# which might reference context in the chat history, formulate a standalone question \
	# which can be understood without the chat history. Do NOT answer the question, \
	# just reformulate it if needed and otherwise return it as is."""
	# contextualize_q_prompt = ChatPromptTemplate.from_messages(
	# 	[
	# 		("system", contextualize_q_system_prompt),
	# 		MessagesPlaceholder(variable_name="chat_history"),
	# 		("human", "{question}"),
	# 	]
	# )
	# contextualize_q_chain = contextualize_q_prompt | bot.llm | StrOutputParser()
	# contextualized_user_message = contextualize_q_chain.invoke({"chat_history": chat_history, "question": user_message})
	#
	# log(f"Contextualized user message: {contextualized_user_message}")
	# return contextualized_user_message
	return user_message


# Called just after memories are recalled. They are stored in:
# - bot.working_memory["episodic_memories"]
# - bot.working_memory["declarative_memories"]
@hook(priority=0)
def after_bot_recalled_memories(memory_query_text: str, bot) -> None:
	"""Hook into semantic search after the memory retrieval.

	Allows to intercept the recalled memories right after these are stored in the Working Memory.
	According to the user's input, the relevant context is saved in `bot.working_memory["episodic_memories"]`
	and `bot.working_memory["declarative_memories"]`. At this point,
	this hook is executed to edit the search query.

	Args:
			memory_query_text: string used to query both *episodic* and *declarative* memories.
			bot: Cheshire Bot instance.
	"""
	return None


# Hook called just before sending response to a client.
@hook(priority=0)
def before_bot_sends_message(message: dict, bot) -> dict:
	"""Hook the outgoing Bot's message.

	Allows to edit the JSON dictionary that will be sent to the client via WebSocket connection.

	This hook can be used to edit the message sent to the user or to add keys to the dictionary.

	Args:
			message: JSON dictionary to be sent to the WebSocket client.
			bot: Cheshire Bot instance.

	Returns:
			Edited JSON dictionary with the Bot's answer.
			Default to::

					{
							"error": False,
							"type": "chat",
							"content": bot_message["output"],
							"why": {
									"input": bot_message["input"],
									"output": bot_message["output"],
									"intermediate_steps": bot_message["intermediate_steps"],
									"memory": {
											"vectors": {
													"episodic": episodic_report,
													"declarative": declarative_report
											}
									},
							},
					}

	"""

	return message
