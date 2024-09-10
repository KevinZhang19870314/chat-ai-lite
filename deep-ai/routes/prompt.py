from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session

from db import models, crud_prompt
from db.database import get_db_session
from parser.my_favorites_parser import my_favorites_parser, MyFavoriteParserParameter
from response import ApiResponse, Status
from routes.auth import get_current_active_user
from routes.types import UpdatePayload

router = APIRouter()


@router.get("/all")
async def all_prompts(
	_: Annotated[models.User, Depends(get_current_active_user)],
	term: Optional[str] = None,
	db: Session = Depends(get_db_session),
):
	try:
		instances = crud_prompt.get_prompts(db, term)
		return ApiResponse(status=Status.SUCCESS, message='', data=instances)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.get("/get")
async def get_prompts(
	_: Annotated[models.User, Depends(get_current_active_user)],
	limit: Optional[int] = 10,
	page: Optional[int] = 1,
	category: Optional[str] = "",
	is_enabled: Optional[int] = 1,
	term: Optional[str] = None,
	db: Session = Depends(get_db_session),
):
	try:
		data = crud_prompt.get_prompts_by_page(db, limit, page, category, is_enabled, term)
		return ApiResponse(status=Status.SUCCESS, message='', data=data)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.get("/get-by-ai")
async def get_prompts_by_ai(
	_: Annotated[models.User, Depends(get_current_active_user)],
	term: Optional[str] = None,
):
	try:
		if term is None or term == "":
			data = MyFavoriteParserParameter(limit=15, page=1, category='all', terms=[]).dict()
		else:
			data = my_favorites_parser(term)
		return ApiResponse(status=Status.SUCCESS, message='', data=data)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/bulk-insert")
async def bulk_insert(
	_: Annotated[models.User, Depends(get_current_active_user)],
	payload: list[models.Prompt],
	db: Session = Depends(get_db_session)
):
	try:
		crud_prompt.bulk_create_prompt(db, payload)
		return ApiResponse(status=Status.SUCCESS, message='', data=None)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/create")
async def create(
	_: Annotated[models.User, Depends(get_current_active_user)],
	payload: models.Prompt,
	db: Session = Depends(get_db_session)
):
	try:
		instance = crud_prompt.create_prompt(db, payload)
		return ApiResponse(status=Status.SUCCESS, message='', data=instance)
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
		instance = crud_prompt.get_prompts_by_id(db, str(payload.id))
		if instance is None:
			raise ValueError('Prompt not exists')

		updated_instance = crud_prompt.update_prompt(db, instance, payload.fields)
		return ApiResponse(status=Status.SUCCESS, message='', data=updated_instance.json())
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/likes")
async def likes(
	_: Annotated[models.User, Depends(get_current_active_user)],
	payload: dict,
	db: Session = Depends(get_db_session)
):
	try:
		if 'id' not in payload:
			raise ValueError('id should not be None')

		# { 'likes': False }	{ 'likes': True }
		if 'likes' not in payload:
			raise ValueError('likes should not be None')

		prompt_id = payload['id']
		is_like = bool(payload['likes'])

		if is_like is True:
			instance = crud_prompt.increment_likes(db, prompt_id)
		else:
			instance = crud_prompt.decrement_likes(db, prompt_id)

		return ApiResponse(status=Status.SUCCESS, message='', data=instance.json())
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/toggle")
async def toggle(
	_: Annotated[models.User, Depends(get_current_active_user)],
	payload: dict,
	db: Session = Depends(get_db_session)
):
	try:
		if 'id' not in payload:
			raise ValueError('id should not be None')

		if 'is_enabled' not in payload:
			raise ValueError('is_enabled should not be None')

		instance = crud_prompt.get_prompts_by_id(db, payload['id'])
		if instance is None:
			raise ValueError('Prompt not exists')

		crud_prompt.toggle_prompt(db, instance, payload['is_enabled'])
		return ApiResponse(status=Status.SUCCESS, message='', data=None)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
