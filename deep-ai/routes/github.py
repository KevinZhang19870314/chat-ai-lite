import os
import traceback
from datetime import timedelta
from urllib.parse import urlencode, parse_qs

import requests
from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import crud_user, models
from db.database import get_db_session
from response import ApiResponse, Status
from routes.auth import create_access_token, create_refresh_token
from routes.helper import gen_user_desc

router = APIRouter()
origin = os.getenv('GH_CALLBACK_REDIRECT_ORIGIN')


class GithubConfig(BaseModel):
	client_id: str
	client_secret: str
	redirect_uri: str


config = GithubConfig(
	client_id=os.getenv('GH_BASIC_CLIENT_ID'),
	client_secret=os.getenv('GH_BASIC_SECRET_ID'),
	redirect_uri=f'{origin}{os.getenv("GH_REDIRECT_PATH")}',
)


@router.get("/auth")
async def github_auth():
	params = {
		'scope': 'user:email',
		'client_id': config.client_id,
	}

	query_string = urlencode(params)
	authorize_url = f"https://github.com/login/oauth/authorize?{query_string}"
	return ApiResponse(status=Status.SUCCESS, message='', data={'authorize_url': authorize_url})


@router.get("/auth/callback")
async def github_auth_callback(request: Request, db: Session = Depends(get_db_session)):
	try:
		code = request.query_params.get('code')

		res = await call_access_token_api(code)
		app_access_token = res['app_access_token']
		has_user_email_scope = res['has_user_email_scope']

		call_user_info_url = 'https://api.github.com/user'
		headers = {
			'Authorization': f'Bearer {app_access_token}',
			'Content-Type': 'application/json'
		}
		response = requests.get(call_user_info_url, headers=headers)
		response_json = response.json()

		if has_user_email_scope:
			email = response_json['email']
		else:
			raise Exception('User does not have email scope')

		# TODO
		if email is None:
			call_private_emails_url = 'https://api.github.com/user/emails'
			headers = {
				'Authorization': f'Bearer {app_access_token}',
				'Content-Type': 'application/json'
			}
			response = requests.get(call_private_emails_url, headers=headers)
			emails = response.json()
			email = emails[0]['email'] or response_json['login']

		response_json['email'] = email
		response_json['access_token'] = app_access_token
		token, refresh_token = await upsert_user(response_json, db)

		redirect_url = f"{origin}/#/github-redirect?token={token}&refresh_token={refresh_token}&email={email}"
		return RedirectResponse(url=redirect_url)
	except Exception as error:
		traceback.print_exc()
		return ApiResponse(status=Status.ERROR, message='Github login failed', data=None)


async def upsert_user(data, db: Session):
	try:
		github_token = data['access_token']
		email = data['email']
		# expires_in = data['expires_in']
		nickname = data['name']
		avatar = data['avatar_url']

		# Create token
		# 过期时间8h = 480minutes
		access_token_expires = timedelta(minutes=float(os.getenv('JWT_EXPIRE_MINUTES')))
		access_token, to_encode = create_access_token(
			data={"sub": email, "github_token": github_token}, expires_delta=access_token_expires
		)
		refresh_token_expires = timedelta(days=float(os.getenv('JWT_REFRESH_EXPIRE_DAYS')))
		refresh_token = create_refresh_token(
			data=to_encode, expires_delta=refresh_token_expires
		)

		user = crud_user.get_user_by_email(db, email)
		if user:
			crud_user.update_user(db, user, {'token': access_token, 'is_github_user': True, 'nickname': nickname, 'avatar': avatar, 'type': user.type, 'model': user.model})
		else:
			crud_user.create_user(
				db,
				models.User(
					email=email,
					avatar=avatar,
					nickname=nickname,
					token=access_token,
					is_github_user=True,
					description=gen_user_desc(),
					type='normal',
					model='gpt-3.5-turbo'
				)
			)

		return access_token, refresh_token
	except Exception as error:
		raise Exception(str(error))


async def call_access_token_api(code: str):
	data = {
		'client_id': config.client_id,
		'client_secret': config.client_secret,
		'code': code
	}
	headers = {'Content-Type': 'application/json'}
	response = requests.post(
		'https://github.com/login/oauth/access_token',
		headers=headers,
		json=data
	)

	# Decode binary content and parse the query string
	decoded_content = response.content.decode('utf-8')
	parsed_content = parse_qs(decoded_content)

	# Extract the values
	access_token = parsed_content.get('access_token', [''])[0]
	scopes = parsed_content.get('scope', [''])[0].split(',')

	has_user_email_scope = 'user:email' in scopes or 'user' in scopes

	return {
		'app_access_token': access_token,
		'has_user_email_scope': has_user_email_scope
	}
