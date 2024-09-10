import uuid
from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, Query
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from pydantic import BaseModel
from sqlmodel import Session

from db import models, crud_chathistorymeta
from db.database import get_db_session
from response import ApiResponse, Status, AiMode
from routes.auth import get_current_active_user
from routes.types import UpdatePayload

router = APIRouter()


def get_greetings(bot: Any, description: str):
	# 添加了三个大括号，是因为有的description中也包含了大括号，为了防止解析错误
	human_template = """下面是对一个角色的描述，请使用第一人称生成一句问候语，我将使用它来作为一场对话中此角色的开场白：
	问题: {{{description}}}
	请注意，开场白没有占位符，并且无需做任何修改即可使用，回答如下:
	"""
	human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

	chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])
	sentence = bot.llm(chat_prompt.format_prompt(description=description).to_messages())

	return sentence.content


@router.post("/create")
async def create(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	payload: models.ChatHistoryMeta,
	db: Session = Depends(get_db_session)
):
	try:
		payload.user_id = current_user.id

		if payload.ai_mode == AiMode.MyFavorites.value:
			instance = crud_chathistorymeta.get_chat_history_meta_by_userid_and_title(db, str(payload.user_id), payload.title)
			if instance is not None:
				raise ValueError('Chat Role Agent already exists')

		new_instance = crud_chathistorymeta.create_chat_history_meta(db, payload)
		return ApiResponse(status=Status.SUCCESS, message='', data=new_instance)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/create-if-not-exists")
async def create_if_not_exists(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	payload: models.ChatHistoryMeta,
	db: Session = Depends(get_db_session)
):
	try:
		payload.user_id = current_user.id

		if payload.ai_mode == AiMode.MyFavorites.value:
			instance = crud_chathistorymeta.get_chat_history_meta_by_userid_and_title(db, str(payload.user_id), payload.title)
			if instance is not None:
				raise ValueError('Chat Role Agent already exists')

		instance = crud_chathistorymeta.get_chat_history_meta_by_uuid(db, str(current_user.id), payload.uuid)
		if instance is None:
			new_instance = crud_chathistorymeta.create_chat_history_meta(db, payload)
			return ApiResponse(status=Status.SUCCESS, message='', data=new_instance)

		return ApiResponse(status=Status.SUCCESS, message='', data=instance)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.get("/query/{ai_mode}")
async def query(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	ai_mode: str,
	db: Session = Depends(get_db_session),
):
	try:
		if ai_mode is None:
			raise ValueError('AIMode[ai_mode] should not be None')

		instances = crud_chathistorymeta.get_chat_history_meta_by_ai_mode(db, str(current_user.id), ai_mode)
		return ApiResponse(status=Status.SUCCESS, message='', data=instances)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.get("/query-with-ai-modes")
async def query(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	ai_modes: str = Query(None),
	db: Session = Depends(get_db_session),
):
	try:
		if ai_modes is None:
			raise ValueError('ai_modes should not be None')

		ai_modes = ai_modes.split(',')
		ai_modes = [item for item in ai_modes if item.strip()]

		instances = crud_chathistorymeta.get_chat_history_meta_by_ai_modes(db, str(current_user.id), ai_modes)
		return ApiResponse(status=Status.SUCCESS, message='', data=instances)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.get("/all")
async def all_by_user(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	db: Session = Depends(get_db_session),
):
	try:
		instances = crud_chathistorymeta.get_chat_history_meta(db, str(current_user.id))
		return ApiResponse(status=Status.SUCCESS, message='', data=instances)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/update")
async def update(
	_: Annotated[models.User, Depends(get_current_active_user)],
	payload: UpdatePayload,
	db: Session = Depends(get_db_session)
):
	try:
		instance = crud_chathistorymeta.get_chat_history_meta_by_id(db, str(payload.id))
		if instance is None:
			raise ValueError('Chat History Meta not exists')

		if instance.ai_mode == AiMode.ChatLLM.value:
			# AiMode.ChatLLM：前端默认了icon，只显示title，故只需要修改title，区分其他
			payload.fields = {'title': payload.fields['title']}

		updated_instance = crud_chathistorymeta.update_chat_history_meta(db, instance, payload.fields)
		return ApiResponse(status=Status.SUCCESS, message='', data=updated_instance.json())
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/delete")
async def delete(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	payload: dict,
	db: Session = Depends(get_db_session)
):
	try:
		if 'id' in payload:
			crud_chathistorymeta.delete_chat_history_meta(db, payload['id'])
		elif 'title' in payload:
			crud_chathistorymeta\
				.delete_chat_history_meta_by_userid_and_title(db, str(current_user.id), payload['title'])
		return ApiResponse(status=Status.SUCCESS, message='', data=None)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
