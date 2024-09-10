from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session

from db import models, crud_user
from db.database import get_db_session
from db.models import UserPayload
from response import ApiResponse, Status
from routes.auth import get_current_active_user
from routes.types import UpdatePayload

router = APIRouter()


@router.get("/get")
async def get_user_by_page(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	limit: Optional[int] = 10,
	page: Optional[int] = 1,
	email: Optional[str] = None,
	type: Optional[str] = None,
	db: Session = Depends(get_db_session),
):
	try:
		if current_user.type not in ("admin", "super_admin"):
			raise ValueError("Permission denied")

		data = []
		if current_user.type == "admin":
			data = crud_user.get_users_with_admin_permission(db, limit, page, email, type)

		if current_user.type == "super_admin":
			data = crud_user.get_users_with_super_admin_permission(db, limit, page, email, type)

		return ApiResponse(status=Status.SUCCESS, message='', data=data)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/update")
async def update_user(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	payload: UpdatePayload,
	db: Session = Depends(get_db_session)
):
	try:
		if current_user.type not in ("admin", "super_admin"):
			raise ValueError("Permission denied")

		if payload.id is None:
			raise ValueError("User id is required")

		instance = crud_user.get_user_by_id(db, payload.id)
		if instance is None:
			raise ValueError('User not exists')

		if payload.fields is None:
			raise ValueError("Fields is required")

		if "type" in payload.fields:
			if current_user.type == "admin":
				if payload.fields["type"] == "admin" or payload.fields["type"] == "super_admin":
					raise ValueError("Permission denied, type cannot be 'admin' or 'super_admin'")
			if current_user.type == "super_admin":
				if payload.fields["type"] == "super_admin":
					raise ValueError("Permission denied, type cannot be 'super_admin'")

		updated_instance = crud_user.update_user(db, instance, payload.fields)
		return ApiResponse(status=Status.SUCCESS, message='', data=UserPayload.from_orm(updated_instance))
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/delete")
async def delete_user(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	payload: dict,
	db: Session = Depends(get_db_session)
):
	try:
		if current_user.type not in ("admin", "super_admin"):
			raise ValueError("Permission denied")

		if payload is None:
			raise ValueError("Payload is required")

		id = payload['id']
		if id is None:
			raise ValueError("User id is required")

		instance = crud_user.get_user_by_id(db, id)
		if instance is None:
			raise ValueError('User not exists')

		crud_user.delete_user_by_id(db, id)
		return ApiResponse(status=Status.SUCCESS, message='', data=None)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
