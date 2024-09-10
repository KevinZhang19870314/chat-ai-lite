import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from db import models, crud_vectordocrecord
from db.database import get_db_session
from log import log
from response import ApiResponse, Status
from routes.auth import get_current_active_user
from routes.helper import get_bot

router = APIRouter()


@router.post("/create")
async def create(
	_: Annotated[models.User, Depends(get_current_active_user)],
	payload: models.VectorDocRecord,
	db: Session = Depends(get_db_session)
):
	try:
		new_instance = crud_vectordocrecord.create_vector_doc_record(db, payload)
		return ApiResponse(status=Status.SUCCESS, message='', data=new_instance)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.get("/get")
async def get_vector_doc_record_by_page(
	_: Annotated[models.User, Depends(get_current_active_user)],
	limit: Optional[int] = 10,
	page: Optional[int] = 1,
	knowledge_base_id: Optional[str] = None,
	term: Optional[str] = None,
	db: Session = Depends(get_db_session),
):
	try:
		data = crud_vectordocrecord.get_vector_doc_record_with_page(db, knowledge_base_id, limit, page, term)
		return ApiResponse(status=Status.SUCCESS, message='', data=data)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/delete")
async def delete(
	_: Annotated[models.User, Depends(get_current_active_user)],
	payload: dict,
	db: Session = Depends(get_db_session)
):
	try:
		if 'id' not in payload:
			raise ValueError('id should not be None')

		crud_vectordocrecord.delete_vector_doc_record(db, payload['id'])
		return ApiResponse(status=Status.SUCCESS, message='', data=None)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/delete-by-filename")
async def delete_by_filename(
	_: Annotated[models.User, Depends(get_current_active_user)],
	payload: dict,
	request: Request,
	db: Session = Depends(get_db_session)
):
	try:
		if 'filename' not in payload:
			raise ValueError('filename should not be None')

		if 'knowledge_base_id' not in payload:
			raise ValueError('knowledge_base_id should not be None')

		ai_mode = f"{payload['ai_mode']}"

		bot = get_bot(request.app.state.bot)
		filename = f"{payload['filename']}"
		knowledge_base_id = f"{payload['knowledge_base_id']}"
		index_name = f"{knowledge_base_id}"

		# get the doc_id list by filename
		records = crud_vectordocrecord.get_vector_doc_record_by_filename(db, knowledge_base_id, filename)
		doc_ids = [record.doc_id for record in records]

		# remove the vector doc records by filename in mysql
		log(f"remove the vector doc records by filename {filename} and knowledge_base_id {knowledge_base_id} in mysql", 'DEBUG')
		crud_vectordocrecord.delete_vector_doc_record_by_filename(db, knowledge_base_id, filename)

		# remove the vector db records by doc_id list in vector store
		log(f"remove vector db docs by doc ids: {doc_ids}", 'DEBUG')
		bot.memory.vectors.remove(index_name, doc_ids)
		return ApiResponse(status=Status.SUCCESS, message='', data=None)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
