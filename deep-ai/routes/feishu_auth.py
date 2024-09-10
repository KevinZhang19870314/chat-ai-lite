import os
import traceback
from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import crud_user, models
from db.database import get_db_session
from deep_ai import DeepAI
from response import ApiResponse, Status
from routes.auth import create_access_token, create_refresh_token
from routes.helper import gen_user_desc, get_bot

router = APIRouter()
origin = os.getenv('FEISHU_CALLBACK_REDIRECT_ORIGIN')


class FeishuConfig(BaseModel):
	app_id: str
	app_secret: str
	redirect_uri: str


config = FeishuConfig(
	app_id=os.getenv('FEISHU_APP_ID'),
	app_secret=os.getenv('FEISHU_APP_SECRET'),
	redirect_uri=f'{origin}{os.getenv("FEISHU_REDIRECT_PATH")}',
)


@router.get("/auth")
async def feishu_auth(request: Request):
	bot = get_bot(request.app.state.bot)
	authorize_url = bot.feishu.get_authorize_url(config.redirect_uri)
	return ApiResponse(status=Status.SUCCESS, message='', data={'authorize_url': authorize_url})


@router.get("/auth/callback")
async def feishu_auth_callback(request: Request, db: Session = Depends(get_db_session)):
	try:
		bot = get_bot(request.app.state.bot)
		code = request.query_params.get('code')

		app_access_token = bot.feishu.get_app_access_token()
		response_json_data = bot.feishu.get_user_access_token(code, app_access_token)

		token, refresh_token, email = await upsert_user(response_json_data, db, bot)

		redirect_url = f"{origin}/#/feishu-redirect?token={token}&refresh_token={refresh_token}&email={email}"
		return RedirectResponse(url=redirect_url)
	except Exception as error:
		traceback.print_exc()
		return ApiResponse(status=Status.ERROR, message='Feishu login failed', data=None)


async def upsert_user(data, db: Session, bot: DeepAI):
	try:
		feishu_user_access_token = data['access_token']
		feishu_user_refresh_token = data['refresh_token']
		user_info = bot.feishu.get_user_info(feishu_user_access_token)

		email = user_info['email']
		avatar = user_info['avatar_url']

		bot.feishu.cache_user_access_token(email, feishu_user_access_token)

		# Create token
		# 飞书的默认过期时间是2h，我们使用自己的过期时间JWT_EXPIRE_MINUTES
		access_token_expires = timedelta(minutes=float(os.getenv('JWT_EXPIRE_MINUTES')))
		access_token, to_encode = create_access_token(
			data={"sub": email, "feishu_token": feishu_user_access_token, "feishu_refresh_token": feishu_user_refresh_token}, expires_delta=access_token_expires
		)
		refresh_token_expires = timedelta(days=float(os.getenv('JWT_REFRESH_EXPIRE_DAYS')))
		refresh_token = create_refresh_token(
			data=to_encode, expires_delta=refresh_token_expires
		)

		user = crud_user.get_user_by_email(db, email)
		if user:
			crud_user.update_user(db, user, {'token': access_token, 'is_feishu_user': True, 'avatar': avatar, 'type': user.type, 'model': user.model})
		else:
			crud_user.create_user(
				db,
				models.User(
					email=email,
					avatar=avatar,
					token=access_token,
					is_feishu_user=True,
					description=gen_user_desc(),
					type='normal',
					model='gpt-3.5-turbo'
				)
			)

		return access_token, refresh_token, email
	except Exception as error:
		raise Exception(str(error))
