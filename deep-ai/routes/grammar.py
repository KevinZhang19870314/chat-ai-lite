import json
import traceback
from typing import Annotated

from fastapi import Depends, APIRouter, Request
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from sqlmodel import Session
from starlette.responses import StreamingResponse

from db import models
from db.database import get_db_session
from log import log
from routes.auth import get_current_active_user
from routes.helper import generate, get_bot
from utils import config_user_metadata_chain

router = APIRouter()


class Revision(BaseModel):
	revised_text: str = Field(description="corrected text")
	reasons: str = Field(description="reasons for revision, make it markdown formatted and list it in a numbered list")


@router.post("/revision-text")
async def revision_text(
	current_user: Annotated[models.User, Depends(get_current_active_user)],
	payload: dict,
	request: Request,
	db: Session = Depends(get_db_session),
):
	bot = get_bot(request.app.state.bot)
	log(f"\n==========Revision Text User email: {current_user.email}==========\n")
	if 'text' not in payload:
		raise ValueError("text is required")

	model = payload['model'] if 'model' in payload else current_user.model
	llm, _ = bot.rebuild_llm_embedder(model)
	text = payload['text']
	log(f'Model: {model}')
	log(f"Original Text: {text}")

	try:
		parser = JsonOutputParser(pydantic_object=Revision)
		prompt = PromptTemplate(
			template="""Check the following text for grammar and spelling, provide the revised text along with reasons for any changes you make.

		Original Text: {text}

		Task:
		1. Identify and correct any grammatical or spelling errors.
		2. Provide the corrected text.
		3. Explain the reasons behind each revision.

		{format_instructions}
		    """,
			input_variables=["text"],
			partial_variables={"format_instructions": parser.get_format_instructions()},
		)

		chain = prompt | llm | parser
		chain = config_user_metadata_chain(chain, current_user)
		response = chain.stream({"text": text})

		def event_generator():
			try:
				for chunk in response:
					yield f"$$${json.dumps(chunk)}"
			except Exception as ex:
				yield str(ex)

		return StreamingResponse(event_generator(), media_type="text/event-stream")
	except ValueError as ve:
		traceback.print_exc()
		return StreamingResponse(generate(str(ve)), media_type="text/event-stream")
	except Exception as e:
		traceback.print_exc()
		return StreamingResponse(generate(str(e)), media_type="text/event-stream")
