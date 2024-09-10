import base64
import os
import random
import time
import uuid
from datetime import timedelta, datetime
from typing import Annotated

import bcrypt
import keyring
import yagmail
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from passlib.exc import InvalidTokenError
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import crud_user, models
from db.crud_user import redis_client
from db.database import get_db_session
from db.models import UserPayload, RegisterUserPayload
from deep_ai import DeepAI
from response import ApiResponse, Status
from routes.helper import generate_password, gen_user_desc, get_bot

# to get a string like this run:
# openssl rand -hex 32
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = os.getenv('JWT_EXPIRE_MINUTES')
JWT_REFRESH_EXPIRE_DAYS = os.getenv('JWT_REFRESH_EXPIRE_DAYS')
JWT_SALT_BASE64 = os.getenv('JWT_SALT_BASE64')


class Token(BaseModel):
	refresh_token: str
	access_token: str
	token_type: str


class TokenData(BaseModel):
	email: str | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/deep-ai/auth/token")
router = APIRouter()


def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
	return pwd_context.hash(password)


def hash_password(password):
	decoded_salt = base64.b64decode(JWT_SALT_BASE64).decode('utf-8')
	hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), decoded_salt.encode('utf-8'))

	return hashed_pwd.decode('utf-8')


def authenticate_user(email: str, password: str, db: Session = Depends(get_db_session, use_cache=False)):
	user = crud_user.get_user_by_email(db, email)
	if not user:
		return False
	# if not verify_password(password, user.password):
	# 	return False
	if password != user.password:
		return False
	return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.now() + expires_delta
	else:
		expire = datetime.now() + timedelta(minutes=15)
	to_encode['exp'] = int(time.mktime(expire.timetuple()))
	encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt, to_encode


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
	to_encode = data.copy()
	to_encode.pop('exp', None)
	if expires_delta:
		expire = datetime.now() + expires_delta
	else:
		# Refresh tokens usually have a long lifespan
		expire = datetime.now() + timedelta(days=30)
	to_encode['exp'] = int(time.mktime(expire.timetuple()))
	encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt


def new_access_token(refresh_token: str, bot: DeepAI, expires_delta: timedelta | None = None):
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	# First, decode the existing refresh token
	try:
		payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
		email: str = payload.get("sub")
		if email is None:
			raise credentials_exception
		# Remove the 'exp' field if it exists because we're about to assign a new expiration time
		payload.pop('exp')
	except ExpiredSignatureError:
		raise Exception("Refresh token expired")
	except InvalidTokenError as e:
		raise Exception(f"Invalid token: {e}")

	# Set up the new expiration time for the access token
	access_token_expires = datetime.now() + (expires_delta or timedelta(minutes=15))

	# Create a new access token with the data from the refresh token and the new expiration time
	new_payload = {
		**payload,
		'exp': int(time.mktime(access_token_expires.timetuple()))
	}
	# 如果是第三方登录，如飞书、github，则需要刷新第三方token并且重新赋值
	is_feishu_user = payload.get('feishu_token') is not None
	is_github_user = payload.get('github_token') is not None
	if is_feishu_user:
		feishu_refresh_token = payload.get('feishu_refresh_token')
		app_access_token = bot.feishu.get_app_access_token()
		data = bot.feishu.refresh_access_token(feishu_refresh_token, app_access_token)
		new_payload['feishu_token'] = data['access_token']
		new_payload['feishu_refresh_token'] = data['refresh_token']

		bot.feishu.cache_user_access_token(email, data['access_token'])

	if is_github_user:
		# TODO
		print('TODO: refresh github token')

	access_token = jwt.encode(new_payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

	return access_token, payload


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db_session)):
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
		email: str = payload.get("sub")
		if email is None:
			raise credentials_exception
		token_data = TokenData(email=email)
	except JWTError:
		raise credentials_exception

	user_data = redis_client.get(email)
	if user_data:
		user = models.User.parse_raw(user_data)
		return user

	user = crud_user.get_user_by_email(db, token_data.email)
	if user is None:
		raise credentials_exception

	redis_client.set(email, user.json(), ex=3600)

	return user


async def get_current_active_user(
	current_user: Annotated[models.User, Depends(get_current_user)]
):
	return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
	db: Session = Depends(get_db_session, use_cache=False)
):
	user = authenticate_user(form_data.username, form_data.password, db)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"},
		)
	access_token_expires = timedelta(minutes=float(JWT_EXPIRE_MINUTES))
	access_token, to_encode = create_access_token(
		data={"sub": user.email}, expires_delta=access_token_expires
	)
	refresh_token_expires = timedelta(days=float(JWT_REFRESH_EXPIRE_DAYS))
	refresh_token = create_refresh_token(
		data=to_encode, expires_delta=refresh_token_expires
	)

	data = {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
	# 清除redis缓存
	redis_client.delete(user.email)
	return data


@router.post("/refresh-access-token", response_model=Token)
async def refresh_access_token(payload: dict, request: Request):
	if "refresh_token" not in payload:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid refresh token",
			headers={"WWW-Authenticate": "Bearer"},
		)

	bot = get_bot(request.app.state.bot)
	refresh_token = payload["refresh_token"]
	access_token_expires = timedelta(minutes=float(JWT_EXPIRE_MINUTES))
	access_token, payload = new_access_token(refresh_token, bot, expires_delta=access_token_expires)

	refresh_token_expires = timedelta(days=float(JWT_REFRESH_EXPIRE_DAYS))
	new_refresh_token = create_refresh_token(
		data=payload, expires_delta=refresh_token_expires
	)

	data = {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
	return data


@router.get("/user")
async def get_user(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
):
	res_user = UserPayload(
		id=current_user.id,
		email=current_user.email,
		nickname=current_user.nickname,
		avatar=current_user.avatar,
		description=current_user.description,
		total_requests=current_user.total_requests,
		used_requests=current_user.used_requests,
		meta=current_user.meta,
		is_feishu_user=current_user.is_feishu_user,
		is_github_user=current_user.is_github_user,
		type=current_user.type,
		model=current_user.model,
		total_image_requests=current_user.total_image_requests,
		used_image_requests=current_user.used_image_requests,
	)

	return ApiResponse(status=Status.SUCCESS, message='', data=res_user)


@router.post("/send-verification-code")
async def send_verification_code(payload: dict, db: Session = Depends(get_db_session)):
	try:
		if 'recipient' not in payload:
			raise ValueError('email should not be None')

		recipient = payload['recipient']
		user_exists = crud_user.get_user_by_email(db, recipient)
		if user_exists:
			raise ValueError('用户已存在 | User already exists')

		email = os.getenv('GMAIL_EMAIL')
		pwd = os.getenv('GMAIL_PWD')
		app_pwd = os.getenv('GMAIL_APP_PWD')
		os_pwd = keyring.get_password('yagmail', email)
		if os_pwd is None:
			yagmail.register(email, pwd)

		verification_code = str(random.randint(100000, 999999))
		subject = 'アカウント認証のための確認コード'
		content = f'''
		お客様

		サービスをご利用いただき、誠にありがとうございます。

		アカウント認証のための確認コードをお伝えいたします。以下のコードをアカウント認証画面に入力してください。

		確認コード：<strong>{verification_code}</strong>

		このコードは、アカウント認証が必要な操作の際に入力する必要があります。セキュリティのため、他の人と共有しないようにしてください。

		もし、確認コードの要求をされていない場合や、不審なアクティビティに気づいた場合は、直ちにお知らせください。

		どうぞ、安心してご利用ください。

		今後ともよろしくお願いいたします。

		-------------------------------------
		ＣａｒｄＩｎｆｏＬｉｎｋ株式会社
		'''
		yag = yagmail.SMTP(email, app_pwd, soft_email_validation=False)
		yag.send(recipient, subject, content)
		# verification code will be expired within 5 minutes
		redis_client.set(f'{recipient}_verification_code', verification_code, ex=5 * 60)

		return ApiResponse(status=Status.SUCCESS, message='', data='')
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/register")
async def register_user(
	payload: RegisterUserPayload,
	db: Session = Depends(get_db_session)
):
	try:
		user_exists = crud_user.get_user_by_email(db, payload.email)
		if user_exists:
			raise ValueError('用户已存在 | User already exists')

		key = f'{payload.email}_verification_code'
		verification_code = None if redis_client.get(key) is None else int(redis_client.get(key))
		if not verification_code:
			raise ValueError('验证码已过期 | Verification code has expired')

		print('verification_code = ', verification_code)
		print('payload.verification_code = ', payload.verification_code)
		if verification_code != payload.verification_code:
			raise ValueError('验证码错误 | Verification code is incorrect')

		payload.description = gen_user_desc()
		new_user = crud_user.create_user(db, models.User.from_orm(payload))

		access_token_expires = timedelta(minutes=float(JWT_EXPIRE_MINUTES))
		access_token, to_encode = create_access_token(
			data={"sub": new_user.email}, expires_delta=access_token_expires
		)
		refresh_token_expires = timedelta(days=float(JWT_REFRESH_EXPIRE_DAYS))
		refresh_token = create_refresh_token(
			data=to_encode, expires_delta=refresh_token_expires
		)

		data = {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

		return data
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/user")
async def create_user(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	payload: models.User,
	db: Session = Depends(get_db_session)
):
	try:
		if current_user.type not in ("admin", "super_admin"):
			raise ValueError('当前用户非admin账户 | Current user is not admin')

		user_exists = crud_user.get_user_by_email(db, payload.email)
		if user_exists:
			raise ValueError('用户已存在 | User already exists')

		pwd = generate_password(10)
		hashed_pwd = hash_password(pwd)
		payload.password = hashed_pwd
		payload.description = gen_user_desc()
		new_user = crud_user.create_user(db, payload)
		return ApiResponse(status=Status.SUCCESS, message='', data={"email": new_user.email, "password": pwd})
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


class UpdateUserPayload(BaseModel):
	id: uuid.UUID
	fields: dict


@router.post("/update")
async def update_user(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	request: Request,
	payload: UpdateUserPayload,
	db: Session = Depends(get_db_session)
):
	bot = get_bot(request.app.state.bot)
	try:
		if not payload.id:
			raise ValueError('id should not be None')

		if current_user.id != payload.id:
			raise ValueError('id should be same with current user')

		instance = crud_user.get_user_by_id(db, str(payload.id))
		if instance is None:
			raise ValueError('User not exists')

		updated_instance = crud_user.update_user(db, instance, payload.fields)

		if 'model' in payload.fields:
			model_name = payload.fields['model']
			bot.rebuild_llm_embedder(model_name)

		return ApiResponse(status=Status.SUCCESS, message='', data=UserPayload.from_orm(updated_instance))
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
