from sqlmodel import col, Session, select, delete

from db import models


def get_chat_history_meta_with_page(db: Session, limit: int = 10, page: int = 1, search: str = ""):
	statement = select(models.ChatHistoryMeta)
	# Add search filter if provided
	if search:
		statement = statement.where(col(models.ChatHistoryMeta.title).contains(search))

	# Apply pagination
	statement = statement.limit(limit).offset((page - 1) * limit)

	results = db.exec(statement)
	prompts = results.fetchall()

	return prompts


def get_chat_history_meta_by_ai_mode(db: Session, user_id: str, ai_mode: str):
	statement = select(models.ChatHistoryMeta)
	statement = statement\
		.where(models.ChatHistoryMeta.user_id == user_id, models.ChatHistoryMeta.ai_mode == ai_mode)

	results = db.exec(statement)
	instances = results.fetchall()

	return instances


def get_chat_history_meta_by_ai_modes(db: Session, user_id: str, ai_modes: list[str]):
	statement = select(models.ChatHistoryMeta)
	statement = statement.where(models.ChatHistoryMeta.user_id == user_id)
	statement = statement.where(col(models.ChatHistoryMeta.ai_mode).in_(ai_modes))

	results = db.exec(statement)
	instances = results.fetchall()

	return instances


def get_chat_history_meta_by_uuid(db: Session, user_id: str, uuid: int):
	statement = select(models.ChatHistoryMeta)
	statement = statement\
		.where(models.ChatHistoryMeta.user_id == user_id, models.ChatHistoryMeta.uuid == uuid)

	results = db.exec(statement)
	instance = results.first()

	return instance


def get_chat_history_meta(db: Session, user_id: str):
	statement = select(models.ChatHistoryMeta)
	statement = statement.where(models.ChatHistoryMeta.user_id == user_id)

	results = db.exec(statement)
	instances = results.fetchall()

	return instances


def create_chat_history_meta(db: Session, payload: models.ChatHistoryMeta):
	db_model = models.ChatHistoryMeta(**payload.dict())
	db.add(db_model)
	db.commit()
	db.refresh(db_model)
	return db_model


def get_chat_history_meta_by_id(db: Session, id: str) -> models.ChatHistoryMeta:
	statement = select(models.ChatHistoryMeta)
	statement = statement\
		.where(models.ChatHistoryMeta.id == id)
	results = db.exec(statement)
	return results.first()


def get_chat_history_meta_by_userid_and_title(db: Session, user_id: str, title: str) -> models.ChatHistoryMeta:
	statement = select(models.ChatHistoryMeta)
	statement = statement\
		.where(models.ChatHistoryMeta.title == title, models.ChatHistoryMeta.user_id == user_id)
	results = db.exec(statement)
	return results.first()


def update_chat_history_meta(db: Session, db_model: models.ChatHistoryMeta, fields: dict):
	for field_name, new_value in fields.items():
		setattr(db_model, field_name, new_value)

	db.commit()
	db.refresh(db_model)

	return db_model


def delete_chat_history_meta(db: Session, id: str):
	db_model = get_chat_history_meta_by_id(db, id)
	if db_model is None:
		raise ValueError('Chat History Meta not exists')

	db.delete(db_model)
	db.commit()


def delete_chat_history_meta_by_userid_and_title(db: Session, user_id: str, title: str):
	db_model = get_chat_history_meta_by_userid_and_title(db, user_id, title)
	if db_model is None:
		raise ValueError('Chat History Meta not exists')

	db.delete(db_model)
	db.commit()


def delete_chat_history_meta_by_knowledge_base_id(db: Session, knowledge_base_id: str):
	statement = delete(models.ChatHistoryMeta).where(models.ChatHistoryMeta.knowledge_base_id == knowledge_base_id)

	db.execute(statement)
	db.commit()
