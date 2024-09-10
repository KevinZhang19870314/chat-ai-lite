from sqlalchemy import func
from sqlalchemy.engine import TupleResult
from sqlmodel import col, Session, select, or_, desc

from db import models


def get_text_to_image_with_page(db: Session, user_id: str, limit: int = 10, page: int = 1, search: str = ""):
	# Get total count
	count_stat = select(func.count(models.TextToImage.id)).where(or_(models.TextToImage.user_id == user_id, models.TextToImage.is_global == 1))
	if search:
		count_stat = count_stat.where(col(models.TextToImage.image_url).contains(search))

	results = db.exec(count_stat)
	total_count = results.first()

	# Get records
	statement = select(models.TextToImage).where(or_(models.TextToImage.user_id == user_id, models.TextToImage.is_global == 1))
	# Add search filter if provided
	if search:
		statement = statement.where(col(models.TextToImage.image_url).contains(search))

	statement = statement.order_by(desc(models.TextToImage.is_global), desc(models.TextToImage.created_at))

	# Apply pagination
	statement = statement.limit(limit).offset((page - 1) * limit)

	results: TupleResult = db.exec(statement)
	records = results.fetchall()

	return {
		"records": records,
		"page": page,
		"size": limit,
		"total": total_count
	}


def get_text_to_image_by_id(db: Session, id: str) -> models.TextToImage:
	statement = select(models.TextToImage)
	statement = statement.where(models.TextToImage.id == id)
	results = db.exec(statement)
	return results.first()


def create_text_to_image(db: Session, payload: models.TextToImage):
	db_model = models.TextToImage(**payload.dict())
	db.add(db_model)
	db.commit()
	db.refresh(db_model)
	return db_model


def update_text_to_image(db: Session, id: str, fields: dict):
	instance = get_text_to_image_by_id(db, id)
	for field_name, new_value in fields.items():
		setattr(instance, field_name, new_value)
	db.commit()
	db.refresh(instance)
	return instance


def delete_text_to_image(db: Session, id: str):
	db_model = get_text_to_image_by_id(db, id)
	if db_model is None:
		raise ValueError('Text to image not exists')

	db.delete(db_model)
	db.commit()
