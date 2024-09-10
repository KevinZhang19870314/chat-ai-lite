import os
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from db import models, crud_knowledgebase, crud_vectordocrecord, crud_chathistorymeta
from db.database import get_db_session
from log import log
from response import Status, ApiResponse, AiMode
from routes.auth import get_current_active_user
from routes.helper import get_bot
from routes.types import UpdatePayload

router = APIRouter()


@router.get("/get")
async def get_knowledge_base_by_page(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	limit: Optional[int] = 10,
	page: Optional[int] = 1,
	term: Optional[str] = None,
	type: Optional[str] = 'localai',
	db: Session = Depends(get_db_session),
):
	try:
		user_id = str(current_user.id)
		data = crud_knowledgebase.get_knowledge_base_with_page(db, user_id, limit, page, term, type)
		return ApiResponse(status=Status.SUCCESS, message='', data=data)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.get("/get-use-plugins/{knowledge_base_id}")
async def get_use_plugins(
	_: Annotated[models.User, Depends(get_current_active_user)],
	request: Request,
	knowledge_base_id: str,
):
	try:
		bot = get_bot(request.app.state.bot)
		use_plugins = bot.mad_hatter.get_use_plugins(knowledge_base_id)
		return ApiResponse(status=Status.SUCCESS, message='', data=use_plugins)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/create")
async def create(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	payload: models.KnowledgeBase,
	db: Session = Depends(get_db_session)
):
	try:
		# check max count per user to create knowledge base records
		max_count = 12
		count = crud_knowledgebase.count_knowledge_base_per_user(db, str(current_user.id))
		if count >= max_count and payload.is_global is False:
			raise ValueError(f'最多可创建 {max_count} 个本地知识库，当前已创建个数 {count}')

		if payload.is_global is False or payload.is_global == 0:
			payload.user_id = current_user.id
		else:
			payload.user_id = None

		new_instance = crud_knowledgebase.create_knowledge_base(db, payload)
		return ApiResponse(status=Status.SUCCESS, message='', data=new_instance)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except IntegrityError as e:
		if isinstance(e, IntegrityError) and e.orig.args[0] == 1062:
			return ApiResponse(status=Status.ERROR, message=e.orig.args[1], data=None)
		else:
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
		instance = crud_knowledgebase.get_knowledge_base_by_id(db, payload.id)
		if instance is None:
			raise ValueError('Knowledge base not exists')

		updated_instance = crud_knowledgebase.update_knowledge_base(db, instance, payload.fields)
		return ApiResponse(status=Status.SUCCESS, message='', data=updated_instance)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/delete")
async def delete(
	_: Annotated[models.User, Depends(get_current_active_user)],
	payload: dict,
	request: Request,
	db: Session = Depends(get_db_session)
):
	try:
		if 'id' not in payload:
			raise ValueError('id should not be None')

		if 'ai_mode' not in payload:
			ai_mode = AiMode.LocalAI.value
		else:
			ai_mode = f"{payload['ai_mode']}"

		bot = get_bot(request.app.state.bot)
		knowledge_base_id = payload['id']
		log(f"delete related table vector_doc_record records by knowledge_base_id ${knowledge_base_id} in mysql", 'DEBUG')
		crud_vectordocrecord.delete_vector_doc_record_by_knowledge_base_id(db, knowledge_base_id)

		log(f"delete related table chat_history_meta records by knowledge_base_id ${knowledge_base_id} in mysql", 'DEBUG')
		crud_chathistorymeta.delete_chat_history_meta_by_knowledge_base_id(db, knowledge_base_id)

		log(f"delete related vector store file '${knowledge_base_id}.faiss' and '${knowledge_base_id}.pkl'", 'DEBUG')
		faiss_file_path = f"{os.path.join(bot.common_storage, knowledge_base_id)}.faiss"
		pkl_file_path = f"{os.path.join(bot.common_storage, knowledge_base_id)}.pkl"
		if os.path.exists(faiss_file_path):
			os.remove(faiss_file_path)
		if os.path.exists(pkl_file_path):
			os.remove(pkl_file_path)

		log(f"delete knowledge base by id ${knowledge_base_id} in mysql and redis", 'DEBUG')
		crud_knowledgebase.delete_knowledge_base_by_knowledge_base_id(db, knowledge_base_id)
		return ApiResponse(status=Status.SUCCESS, message='', data=None)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
