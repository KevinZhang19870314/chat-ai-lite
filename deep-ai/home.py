import logging
import mimetypes
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from uvicorn.config import LOGGING_CONFIG

from db import crud_user
from deep_ai import DeepAI
from routes import base, local_ai, auth, feishu_auth, chat_with_role, chat_history_meta, prompt, vector_doc_record, knowledge_base, plugins, github, user, chat_llm, grammar, text_to_image

load_dotenv()
mimetypes.add_type("text/markdown", ".md")
mimetypes.add_type("text/markdown", ".markdown")
mimetypes.add_type("text/csv", ".csv")
mimetypes.add_type("application/msword", ".docx")
mimetypes.add_type("application/msword", ".doc")
mimetypes.add_type("application/msexcel", ".xlsx")
mimetypes.add_type("application/msexcel", ".xls")
mimetypes.add_type("application/zip", ".zip")
mimetypes.add_type("application/x-tar", ".tar")


@asynccontextmanager
async def lifespan(app: FastAPI):
	app.state.bot = DeepAI()
	crud_user.create_super_admin_if_not_exists(next(app.state.bot.db()))
	yield


api = FastAPI(lifespan=lifespan)

# Configures the CORS middleware for the FastAPI app
cors_allowed_origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "")
origins = cors_allowed_origins_str.split(",") if cors_allowed_origins_str else ["*"]
api.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Add routers to the middleware stack.
api.include_router(base.router, tags=["Status"], prefix="/deep-ai")
api.include_router(local_ai.router, tags=["Local AI"], prefix="/deep-ai/local-ai")
api.include_router(auth.router, tags=["Auth"], prefix="/deep-ai/auth")
api.include_router(feishu_auth.router, tags=["Feishu Auth"], prefix="/deep-ai/feishu-auth")
api.include_router(chat_with_role.router, tags=["Chat With Role"], prefix="/deep-ai/chat-with-role")
api.include_router(chat_history_meta.router, tags=["Chat History Meta"], prefix="/deep-ai/chat-history-meta")
api.include_router(prompt.router, tags=["Prompt"], prefix="/deep-ai/prompt")
api.include_router(vector_doc_record.router, tags=["Vector Document Record"], prefix="/deep-ai/vector-doc-record")
api.include_router(knowledge_base.router, tags=["Knowledge Base"], prefix="/deep-ai/knowledge-base")
api.include_router(plugins.router, tags=["Plugins"], prefix="/deep-ai/plugins")
api.include_router(github.router, tags=["Github Auth"], prefix="/deep-ai/github")
api.include_router(user.router, tags=["User"], prefix="/deep-ai/user")
api.include_router(chat_llm.router, tags=["Chat LLM"], prefix="/deep-ai/chat-llm")
api.include_router(grammar.router, tags=["Grammar"], prefix="/deep-ai/grammar")
api.include_router(text_to_image.router, tags=["Text to Image"], prefix="/deep-ai/text-to-image")

# Text to Images local image serving
STORAGE_ROOT = os.getenv('STORAGE_ROOT')
TEXT_TO_IMAGE_STORAGE = os.getenv('TEXT_TO_IMAGE_STORAGE')
TEXT_TO_IMAGE_STORAGE_FOLDER_PATH = os.path.join(STORAGE_ROOT, TEXT_TO_IMAGE_STORAGE)
os.makedirs(TEXT_TO_IMAGE_STORAGE_FOLDER_PATH, exist_ok=True)
api.mount("/tti", StaticFiles(directory=TEXT_TO_IMAGE_STORAGE_FOLDER_PATH, html=True, follow_symlink=True), name="")


@api.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc):
	return JSONResponse(
		status_code=422,
		content={"error": exc.errors()},
	)


if __name__ == "__main__":
	# debugging utilities, to deactivate put `DEBUG=false` in .env
	debug_config = {}
	if os.getenv("DEBUG", "true") == "true":
		debug_config = {
			"reload": True,
			"reload_includes": ["plugin.json"],
			"reload_excludes": ["*test_*.*", "*mock_*.*"]
		}

	LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
	LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

	# fix the tricky: `[uvicorn.error]` in log `2023-09-06 15:01:14 [uvicorn.error] INFO: Application startup complete.`
	uvicorn_error_logger = logging.getLogger('uvicorn.error')
	uvicorn_error_logger.name = 'uvicorn.server'

	uvicorn.run(
		"home:api",
		host="0.0.0.0",
		port=8000,
		proxy_headers=True,
		forwarded_allow_ips="*",
		**debug_config
	)
