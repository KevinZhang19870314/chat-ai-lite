import uuid

from sqlalchemy import or_
from sqlmodel import col, Session, select, func

from db import models


def get_prompts(db: Session, search: str = ""):
	statement = select(models.Prompt).where(models.Prompt.is_deleted == 0)
	# Add search filter if provided
	if search:
		statement = statement.where(col(models.Prompt.title).contains(search))

	results = db.exec(statement)
	prompts = results.fetchall()

	return prompts


def get_prompts_by_page(db: Session, limit: int = 10, page: int = 1, category: str = "", is_enabled: int = 1, search: str = ""):
	# Get total count
	count_stat = select(func.count(models.Prompt.id))
	if is_enabled != -1:
		count_stat = count_stat.where(models.Prompt.is_enabled == is_enabled)
	if category and category != "all":
		if category == "likes":
			count_stat = count_stat.where(models.Prompt.likes > 0)
		else:
			count_stat = count_stat.where(models.Prompt.category == category)

	if search:
		search_terms = [term.strip() for term in search.split(',') if term.strip()]
		or_conditions = or_(*[func.lower(col(models.Prompt.title)).contains(term.lower()) for term in search_terms])
		count_stat = count_stat.where(or_conditions)
		# count_stat = count_stat.where(col(models.Prompt.title).contains(search))

	results = db.exec(count_stat)
	total_count = results.first()

	# query records
	statement = select(models.Prompt)
	if is_enabled != -1:
		statement = statement.where(models.Prompt.is_enabled == is_enabled)
	if category and category != "all":
		if category == "likes":
			statement = statement.where(models.Prompt.likes > 0)
		else:
			statement = statement.where(models.Prompt.category == category)
	# Add search filter if provided
	if search:
		search_terms = [term.strip() for term in search.split(',') if term.strip()]
		or_conditions = or_(*[func.lower(col(models.Prompt.title)).contains(term.lower()) for term in search_terms])
		statement = statement.where(or_conditions)
		# statement = statement.where(col(models.Prompt.title).contains(search))

	# Add order by for category likes
	if category == "likes":
		statement = statement.order_by(col(models.Prompt.likes).desc())

	# Apply pagination
	statement = statement.limit(limit).offset((page - 1) * limit)

	results = db.exec(statement)
	prompts = results.fetchall()

	return {
		"prompts": prompts,
		"page": page,
		"size": limit,
		"total": total_count
	}


def create_prompt(db: Session, payload: models.Prompt):
	db_prompt = models.Prompt(**payload.dict())
	db.add(db_prompt)
	db.commit()
	db.refresh(db_prompt)
	return db_prompt


def bulk_create_prompt(db: Session, payload: list[models.Prompt]):
	db_prompts = []
	for prompt in payload:
		db_prompts.append(models.Prompt(**prompt.dict()))
	db.add_all(db_prompts)
	db.commit()


def get_prompts_by_title(db: Session, title: str) -> list[models.Prompt]:
	statement = select(models.Prompt)
	statement = statement.where(col(models.Prompt.title).contains(title))
	results = db.exec(statement)
	return results.fetchall()


def get_prompts_by_id(db: Session, id: str) -> models.Prompt:
	statement = select(models.Prompt)
	statement = statement.where(models.Prompt.id == id)
	results = db.exec(statement)
	return results.first()


def update_prompt(db: Session, prompt: models.Prompt, fields: dict):
	for field_name, new_value in fields.items():
		setattr(prompt, field_name, new_value)

	db.commit()
	db.refresh(prompt)

	return prompt


def toggle_prompt(db: Session, prompt: models.Prompt, is_enabled: bool):
	setattr(prompt, 'is_enabled', is_enabled)
	db.commit()


def increment_likes(db: Session, id: str):
	prompt = get_prompts_by_id(db, id)
	if prompt is None:
		raise ValueError('Prompt not exists')

	prompt.likes += 1
	db.add(prompt)
	db.commit()
	db.refresh(prompt)

	return prompt


def decrement_likes(db: Session, id: str):
	prompt = get_prompts_by_id(db, id)
	if prompt is None:
		raise ValueError('Prompt not exists')

	prompt.likes -= 1
	if prompt.likes < 0:
		prompt.likes = 0

	db.add(prompt)
	db.commit()
	db.refresh(prompt)

	return prompt
