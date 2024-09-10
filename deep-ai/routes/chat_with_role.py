from typing import Annotated

from fastapi import APIRouter, Depends, Request
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from openai.types.chat import ChatCompletionMessageParam
from sqlmodel import Session
from starlette.responses import StreamingResponse

from db import models, crud_chathistorymeta
from db.database import get_db_session
from log import log
from routes.auth import get_current_active_user
from routes.helper import generate, get_bot
from routes.types import OpenAIRole, OpenAIChatRequest
from utils import config_user_metadata_chain

router = APIRouter()


def build_memory(messages: list[ChatCompletionMessageParam], system_prompt: str):
	results: list[ChatCompletionMessageParam] = []
	system_message = next(
		(message for message in messages if message['role'] == OpenAIRole.SYSTEM),
		{'role': OpenAIRole.SYSTEM, 'content': system_prompt},
	)
	results.append(system_message)
	for message in messages:
		if message['role'] == OpenAIRole.USER or message['role'] == OpenAIRole.ASSISTANT:
			results.append(message)

	dict_list = [{'role': msg['role'], 'content': msg['content']} for msg in results]

	log(dict_list, 'INFO')

	return results


# AiMode.myfavorites
@router.post("/ask")
def ask(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	request: OpenAIChatRequest,
	req: Request,
	db: Session = Depends(get_db_session),
):
	bot = get_bot(req.app.state.bot)
	try:
		log(f"\n==========Chat with role User email: {current_user.email}==========\n")

		if request.uuid is None:
			raise ValueError('uuid should not be None')

		instance = crud_chathistorymeta.get_chat_history_meta_by_uuid(db, str(current_user.id), request.uuid)
		if instance is None:
			raise ValueError('Chat History Meta does not exists')

		model = current_user.model if request.model is None else request.model
		log(f'Model: {model}')
		bot.rebuild_llm_embedder(model)
		log(f"Request: {request.dict(exclude={'messages'})}")
		raw_messages = build_memory(request.messages, instance.description)
		messages: list[BaseMessage] = []
		for message in raw_messages:
			if message['role'] == "user":
				messages.append(HumanMessage(content=message['content']))
			elif message['role'] == "assistant":
				messages.append(AIMessage(content=message['content']))
			else:
				messages.append(SystemMessage(content=message['content']))

		prompt = ChatPromptTemplate.from_messages(
			[
				MessagesPlaceholder(variable_name="messages"),
			]
		)
		chain = prompt | bot.llm | StrOutputParser()
		chain = config_user_metadata_chain(chain, current_user)
		response = chain.stream({"messages": messages})

		def event_generator():
			completion_prompt = ''
			try:
				for chunk in response:
					completion_prompt += chunk
					yield chunk
			except Exception as ex:
				yield str(ex)

		return StreamingResponse(event_generator(), media_type="text/event-stream")
	except ValueError as ve:
		return StreamingResponse(generate(str(ve)), media_type="text/event-stream")
	except Exception as e:
		return StreamingResponse(generate(str(e)), media_type="text/event-stream")
