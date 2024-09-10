import mimetypes
from typing import TypedDict, List, Annotated, Any

from fastapi import APIRouter, Body, UploadFile, Depends, Form, Response, BackgroundTasks
from fastapi import Request
from fastapi.responses import StreamingResponse
from langchain_community.callbacks import get_openai_callback
from sqlalchemy.orm import Session

from db import models, crud_vectordocrecord
from db.database import get_db_session
from log import log
from response import Status, ApiResponse
from routes.auth import get_current_active_user
from routes.helper import generate, get_bot
from routes.types import UserMessage

router = APIRouter()


class ConversationHistory(TypedDict):
	session_ids: List[str]


@router.post("/upload-file")
def upload_file(
	_: Annotated[models.User, Depends(get_current_active_user)],
	request: Request,
	file: UploadFile,
	knowledge_base_id: Any = Form(...),
	db: Session = Depends(get_db_session)
):
	"""后台定时任务处理文件"""
	bot = request.app.state.bot
	try:
		# Validate pdf, text and md files all together
		if mimetypes.guess_type(file.filename)[0] != "application/pdf" and \
			mimetypes.guess_type(file.filename)[0] != "text/plain" and \
			mimetypes.guess_type(file.filename)[0] != "text/markdown" and \
			mimetypes.guess_type(file.filename)[0] != "text/csv" and \
			mimetypes.guess_type(file.filename)[0] != "application/msword" and \
			mimetypes.guess_type(file.filename)[0] != "application/msexcel":
			raise ValueError(f"The uploaded file {file.filename} type not supported")

		# check the file exists in the db table vector_doc_record or not
		exists = crud_vectordocrecord.check_vector_doc_record_exists(db, knowledge_base_id, file.filename)
		if exists is not None:
			raise ValueError(f"You already uploaded {file.filename} file")

		filename = f"({knowledge_base_id}){file.filename}"
		log(f"Upload {file.filename} file, rename to {filename}")
		bot.black_hole.save_uploaded_file_to_path(file, filename)
		return ApiResponse(status=Status.SUCCESS, message='File uploaded', data=None)
	except Exception as e:
		# return ApiResponse(status=Status.ERROR, message=e.__str__(), data=None)
		return Response(status_code=500, content=e.__str__())


@router.post("/ingest-file")
def ingest_file(
	_: Annotated[models.User, Depends(get_current_active_user)],
	request: Request,
	file: UploadFile,
	background_tasks: BackgroundTasks,
	knowledge_base_id: Any = Form(...),
	db: Session = Depends(get_db_session)
):
	"""使用fastapi的background tasks处理文件"""
	bot = get_bot(request.app.state.bot)
	try:
		# Validate pdf, text and md files all together
		if mimetypes.guess_type(file.filename)[0] != "application/pdf" and \
			mimetypes.guess_type(file.filename)[0] != "text/plain" and \
			mimetypes.guess_type(file.filename)[0] != "text/markdown" and \
			mimetypes.guess_type(file.filename)[0] != "text/csv" and \
			mimetypes.guess_type(file.filename)[0] != "application/msword" and \
			mimetypes.guess_type(file.filename)[0] != "application/msexcel":
			raise ValueError(f"The uploaded file {file.filename} type not supported")

		# check the file exists in the db table vector_doc_record or not
		exists = crud_vectordocrecord.check_vector_doc_record_exists(db, knowledge_base_id, file.filename)
		if exists is not None:
			raise ValueError(f"You already uploaded {file.filename} file")

		filename = f"({knowledge_base_id}){file.filename}"
		log(f"Upload {file.filename} file, rename to {filename}")
		res = bot.black_hole.save_uploaded_file_to_path(file, filename)
		full_path = res['full_path']
		background_tasks.add_task(bot.black_hole.process_file, full_path)

		return ApiResponse(status=Status.SUCCESS, message='File uploaded and is being ingested asynchronously', data=None)
	except Exception as e:
		return Response(status_code=500, content=e.__str__())


@router.post("/ingest-text")
def ingest_text(current_user: Annotated[models.User, Depends(get_current_active_user)], request: Request,
								text: str = Body(embed=True)):
	try:
		bot = get_bot(request.app.state.bot)
		faiss_db = bot.memory.vectors.faiss_db(current_user.id.__str__())
		db = faiss_db.from_texts([text], bot.embedder)

		faiss_db.merge_from(db)
		faiss_db.save_local(bot.common_storage, current_user.id.__str__())
		return ApiResponse(status=Status.SUCCESS, message='', data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=e.__str__(), data=None)


@router.post("/async-ask-bot")
async def async_ask_bot(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	request: Request,
	message: UserMessage,
	_: Session = Depends(get_db_session),
):
	try:
		log(f"\n==========Chat local AI User email: {current_user.email}==========\n")
		log(f'Model: {current_user.model}')

		bot = get_bot(request.app.state.bot)
		bot.rebuild_llm_embedder(current_user.model)
		# Used for tools `get_my_user_information`
		bot.email = current_user.email

		with get_openai_callback() as cb:
			answer = bot(message.__dict__, message.knowledge_base_id.__str__())
			log(cb)

		answer["content"] = answer["content"].strip('\'"')

		return StreamingResponse(generate(answer["content"]), media_type="text/event-stream")
	except ValueError as ve:
		return StreamingResponse(generate(str(ve)), media_type="text/event-stream")
	except Exception as e:
		return StreamingResponse(generate(str(e)), media_type="text/event-stream")
