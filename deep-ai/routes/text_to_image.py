import asyncio
import os
import traceback
import urllib.request
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request, BackgroundTasks
from langchain.chains.llm import LLMChain
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import PromptTemplate
from sqlmodel import Session

from db import models, crud_texttoimage, crud_user
from db.database import get_db_session
from db.models import TextToImage
from log import log
from response import ApiResponse, Status
from routes.auth import get_current_active_user
from routes.helper import get_bot
from routes.types import TextToImagePayload

router = APIRouter()

# 文件夹结构为：
# -- {STORAGE_ROOT}\text_to_image\{user email}\*.*
STORAGE_ROOT = os.getenv('STORAGE_ROOT')
TEXT_TO_IMAGE_STORAGE = os.getenv('TEXT_TO_IMAGE_STORAGE')
TEXT_TO_IMAGE_STORAGE_FOLDER_PATH = os.path.join(STORAGE_ROOT, TEXT_TO_IMAGE_STORAGE)
TEXT_TO_IMAGE_ORIGIN = os.getenv('TEXT_TO_IMAGE_ORIGIN')


@router.get("/get")
async def get_text_to_image_list(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	limit: Optional[int] = 10,
	page: Optional[int] = 1,
	term: Optional[str] = None,
	db: Session = Depends(get_db_session),
):
	try:
		user_id = current_user.id
		data = crud_texttoimage.get_text_to_image_with_page(db, str(user_id), limit, page, term)
		return ApiResponse(status=Status.SUCCESS, message='', data=data)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.post("/generate")
async def generate(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	payload: TextToImagePayload,
	request: Request,
	background_tasks: BackgroundTasks,
	db: Session = Depends(get_db_session),
):
	try:
		log(f"TextToImagePayload: {payload.json()}")

		if payload.query is None:
			raise ValueError('query should not be None')

		if payload.model is None:
			raise ValueError('model should not be None')

		if current_user.total_image_requests <= current_user.used_image_requests:
			raise ValueError('You have reached the maximum number of text to image requests')

		size = payload.size
		if size is None:
			size = "512x512" if payload.model == "dall-e-2" else "1024x1024"

		bot = get_bot(request.app.state.bot)

		prompt = PromptTemplate(
			input_variables=["image_desc"],
			template="根据以下描述生成适当的提示以生成图像: {image_desc}",
		)
		chain = LLMChain(llm=bot.llm, prompt=prompt)
		chain_result = chain.invoke({"image_desc": payload.query})
		log(f"Chain result: {chain_result['text']}")

		dall_e = DallEAPIWrapper(model=payload.model, size=size)
		image_url = dall_e.run(chain_result["text"])

		log(f"Image URL: {image_url}")

		background_tasks.add_task(_save_image_to_local_and_db, image_url, current_user, db, payload, size)

		return ApiResponse(status=Status.SUCCESS, message='', data=image_url)
	except ValueError as e:
		traceback.print_exc()
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		traceback.print_exc()
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


@router.delete("/delete/{id}")
async def delete_image(
	_: Annotated[models.User, Depends(get_current_active_user)],
	__: str,
	___: Session = Depends(get_db_session),
):
	try:
		# TODO: delete the image file

		# TODO: delete db record

		return ApiResponse(status=Status.SUCCESS, message="", data=None)
	except ValueError as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)
	except Exception as e:
		return ApiResponse(status=Status.ERROR, message=str(e), data=None)


async def _save_image_to_local_and_db(image_url, current_user, db, payload, size):
	# consume once
	crud_user.consume_once_image(db, current_user.email)

	# avoid the image url is not ready
	await asyncio.sleep(3)

	# Save the image url to local image
	image_path = os.path.join(TEXT_TO_IMAGE_STORAGE_FOLDER_PATH, current_user.email)
	os.makedirs(image_path, exist_ok=True)
	image_filename = f"{_gen_random_filename()}.png"
	image_full_path = os.path.join(image_path, image_filename)
	_save_image_from_url(image_url, image_full_path)

	# Insert a record to db
	db_image_url = os.path.join(TEXT_TO_IMAGE_ORIGIN, current_user.email, image_filename)
	crud_texttoimage.create_text_to_image(db, TextToImage(
		user_id=current_user.id,
		is_global=payload.is_global,
		query=payload.query,
		model=payload.model,
		image_url=db_image_url,
		size=size,
	))


def _save_image_from_url(url, filename):
	try:
		urllib.request.urlretrieve(url, filename)
		log(f"Image saved successfully as {filename}")
	except Exception as e:
		log(f"Error saving image: \n{e}")
		raise e


def _gen_random_filename():
	import random
	import string
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
