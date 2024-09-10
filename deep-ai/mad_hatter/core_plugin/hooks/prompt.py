import time
from datetime import timedelta

from langchain.agents.conversational import prompt

from utils import verbal_timedelta
from mad_hatter.decorators import hook


@hook(priority=0)
def agent_prompt_prefix(bot):
	prefix = """As an assistant specialized in question-answering tasks, you are expected to provide detailed and professional responses.
Utilize the information from the provided context and chat history to craft comprehensive answers.
If you encounter a question to which you do not know the answer, acknowledge it candidly.
"""
	# check if custom prompt is sent in prompt settings
	prompt_settings = bot.working_memory["user_message_json"]["prompt_settings"]

	if prompt_settings["prefix"]:
		prefix = prompt_settings["prefix"]

	return prefix


@hook(priority=0)
def agent_prompt_instructions(bot) -> str:
	"""Hook the instruction prompt.

	Allows to edit the instructions that the Cat feeds to the *Agent*.

	The instructions are then composed with two other prompt components, i.e. `agent_prompt_prefix`
	and `agent_prompt_suffix`.

	Parameters
	----------
	bot : DeepAI
			DeepAI Bot instance.

	Returns
	-------
	instructions : str
			The string with the set of instructions informing the *Agent* on how to format its reasoning to select a
			proper tool for the task at hand.

	Notes
	-----
	This prompt explains the *Agent* how to format its chain of reasoning when deciding when and which tool to use.
	Default prompt splits the reasoning in::

			- Thought: Yes/No answer to the question "Do I need to use a tool?";

			- Action: a tool chosen among the available ones;

			- Action Input: input to be passed to the tool. This is inferred as explained in the tool docstring;

			- Observation: description of the result (which is the output of the @tool decorated function found in plugins).

	"""

	DEFAULT_TOOL_TEMPLATE = """Answer the following question: `{input}`
    You can only reply using these tools:

    {tools}
    none_of_the_others: none_of_the_others(None) - Use this tool if none of the others tools help. Input is always None.

    If you want to use tools, use the following format:
    Action: the name of the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ...
    Action: the name of the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action

    When you have a final answer respond with:
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    {agent_scratchpad}"""

	# here we piggy back directly on langchain agent instructions. Different instructions will require a different OutputParser
	return DEFAULT_TOOL_TEMPLATE


@hook(priority=0)
def agent_prompt_suffix(bot):
	suffix = """
Respond using the same language as Human said in last message in chat_history. Respond using markdown.

# Context

{declarative_memory}

{tools_output}

## Conversation until now:{chat_history}
 - Human: {input}
 - AI: """

	return suffix


@hook(priority=0)
def agent_prompt_declarative_memories(memory_docs, bot):
	# convert docs to simple text
	memory_texts = [m[0].page_content.replace("\n", ". ") for m in memory_docs]

	# add source information (e.g. "extracted from file.txt")
	memory_sources = []
	for m in memory_docs:
		if "source" in m[0].metadata:
			source = m[0].metadata["source"]
		else:
			source = "text"
		memory_sources.append(f" (extracted from {source})")

	memory_texts = [a + b for a, b in zip(memory_texts, memory_sources)]

	memories_separator = "\n  - "
	memory_content = "## Context of documents containing relevant information: " + \
									 memories_separator + memories_separator.join(memory_texts)

	# if no data is retrieved from memory don't erite anithing in the prompt
	if len(memory_texts) == 0:
		memory_content = ""

	return memory_content


@hook(priority=0)
def agent_prompt_chat_history(chat_history, bot):
	history = ""
	for turn in chat_history:
		history += f"\n - {turn.who}: \"{turn.message}\""

	return history
