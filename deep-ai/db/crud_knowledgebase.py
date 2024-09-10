import json

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlmodel import col, Session, select, delete, or_, desc

from db import models
from db.crud_user import redis_client


def get_knowledge_base_with_page(db: Session, user_id: str, limit: int = 10, page: int = 1, search: str = "", type: str = 'localai',):
	# Get total count
	count_stat = select(func.count(models.KnowledgeBase.id)).where(or_(models.KnowledgeBase.user_id == user_id, models.KnowledgeBase.is_global == 1))
	if search:
		count_stat = count_stat.where(col(models.KnowledgeBase.name).contains(search))
	if type:
		count_stat = count_stat.where(models.KnowledgeBase.type == type)

	results = db.exec(count_stat)
	total_count = results.first()

	# Get records
	statement = select(models.KnowledgeBase).where(or_(models.KnowledgeBase.user_id == user_id, models.KnowledgeBase.is_global == 1))
	# Add search filter if provided
	if search:
		statement = statement.where(col(models.KnowledgeBase.name).contains(search))
	if type:
		statement = statement.where(models.KnowledgeBase.type == type)

	statement = statement.order_by(desc(models.KnowledgeBase.is_global))

	# Apply pagination
	statement = statement.limit(limit).offset((page - 1) * limit)

	results = db.exec(statement)
	records = results.fetchall()

	return {
		"records": records,
		"page": page,
		"size": limit,
		"total": total_count
	}


def count_knowledge_base_per_user(db: Session, user_id: str):
	statement = select(func.count(models.KnowledgeBase.id)).where(models.KnowledgeBase.user_id == user_id)
	results = db.exec(statement)
	total_count = results.first()
	return total_count


def get_knowledge_base_by_name(db: Session, name: str):
	statement = select(models.KnowledgeBase).where(models.KnowledgeBase.name == name)
	results = db.exec(statement)

	return results.first()


def get_knowledge_base_by_id(db: Session, id: str) -> models.KnowledgeBase:
	statement = select(models.KnowledgeBase)
	statement = statement.where(models.KnowledgeBase.id == id)
	results = db.exec(statement)
	return results.first()


def get_use_plugins_by_id(db: Session, id: str):
	def string_to_list(input_str):
		if input_str is None or input_str.strip() == "":
			return []
		else:
			return [item.strip() for item in input_str.split(",")]

	instance = redis_client.get(id)
	if instance is None:
		instance = get_knowledge_base_by_id(db, id)
		if instance is None:
			return []
		return string_to_list(instance.use_plugins)

	instance = models.KnowledgeBase.parse_raw(instance)
	return string_to_list(instance.use_plugins)


def create_knowledge_base(db: Session, payload: models.KnowledgeBase):
	db_model = models.KnowledgeBase(**payload.dict())
	db.add(db_model)
	db.commit()
	db.refresh(db_model)

	json_compatible_data = jsonable_encoder(db_model)
	json_data = json.dumps(json_compatible_data)
	redis_client.set(db_model.id, json_data, ex=3600)

	return db_model


def update_knowledge_base(db: Session, instance: models.KnowledgeBase, fields: dict):
	for field_name, new_value in fields.items():
		setattr(instance, field_name, new_value)

	db.commit()
	db.refresh(instance)

	if 'use_plugins' in fields:
		json_compatible_data = jsonable_encoder(instance)
		json_data = json.dumps(json_compatible_data)
		redis_client.set(instance.id, json_data, ex=3600)

	return instance


def delete_knowledge_base(db: Session, id: str):
	db_model = get_knowledge_base_by_id(db, id)
	if db_model is None:
		raise ValueError('Knowledge base not exists')

	db.delete(db_model)
	db.commit()
	redis_client.delete(id)


def delete_knowledge_base_by_knowledge_base_id(db: Session, knowledge_base_id: str):
	statement = delete(models.KnowledgeBase).where(models.KnowledgeBase.id == knowledge_base_id)

	db.execute(statement)
	db.commit()
	redis_client.delete(knowledge_base_id)

