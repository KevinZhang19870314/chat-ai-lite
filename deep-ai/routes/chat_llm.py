import json
import traceback
from typing import Annotated

from fastapi import Depends, APIRouter, Request
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from sqlmodel import Session
from starlette.responses import StreamingResponse

from db import models
from db.database import get_db_session
from log import log
from routes.auth import get_current_active_user
from routes.helper import generate, get_bot
from utils import config_user_metadata_chain

router = APIRouter()


@router.post("/chat")
async def chat(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	payload: dict,
	request: Request,
	_: Session = Depends(get_db_session),
):
	"""Use langchain llm api"""
	bot = get_bot(request.app.state.bot)
	log(f"\n==========Chat LLM User email: {current_user.email}==========\n")
	if 'messages' not in payload:
		raise ValueError("messages is required")

	if 'ai_mode' not in payload:
		raise ValueError("ai_mode is required")

	model = payload['model'] if 'model' in payload else current_user.model
	llm, _ = bot.rebuild_llm_embedder(model)
	raw_messages = payload['messages']
	log(f'Model: {model}')
	log(f"Messages: {json.dumps(raw_messages, indent=4, ensure_ascii=False)}")

	try:
		messages: list[BaseMessage] = []
		for message in raw_messages:
			if message['role'] == 'system':
				messages.append(SystemMessage(content=message['content']))
			elif message['role'] == "user":
				messages.append(HumanMessage(content=message['content']))
			else:
				messages.append(AIMessage(content=message['content']))

		prompt = ChatPromptTemplate.from_messages(
			[
				MessagesPlaceholder(variable_name="messages"),
			]
		)
		chain = prompt | llm | StrOutputParser()
		chain = config_user_metadata_chain(chain, current_user)
		if str(model).lower().startswith('gemini-'):
			response = chain.stream({"messages": messages})
		else:
			response = chain.astream({"messages": messages})

		async def event_generator():
			completion_prompt = ''
			try:
				if str(model).lower().startswith('gemini-'):
					for chunk in response:
						completion_prompt += chunk
						yield chunk
				else:
					async for chunk in response:
						completion_prompt += chunk
						yield chunk
			except Exception as ex:
				yield str(ex)

		return StreamingResponse(event_generator(), media_type="text/event-stream")
	except ValueError as ve:
		traceback.print_exc()
		return StreamingResponse(generate(str(ve)), media_type="text/event-stream")
	except Exception as e:
		traceback.print_exc()
		return StreamingResponse(generate(str(e)), media_type="text/event-stream")
