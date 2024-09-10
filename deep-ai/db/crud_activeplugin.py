from sqlalchemy import func
from sqlmodel import col, Session, select

from db import models


def get_active_plugin_with_page(db: Session, limit: int = 10, page: int = 1, search: str = ""):
	# Get total count
	count_stat = select(func.count(models.ActivePlugin.id))
	if search:
		count_stat = count_stat.where(col(models.ActivePlugin.name).contains(search))
	results = db.exec(count_stat)
	total_count = results.first()

	statement = select(models.ActivePlugin)
	# Add search filter if provided
	if search:
		statement = statement.where(col(models.ActivePlugin.name).contains(search))

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


def get_all_active_plugins(db: Session) -> list[models.ActivePlugin]:
	statement = select(models.ActivePlugin)

	results = db.exec(statement)
	records = results.fetchall()

	return records


def create_active_plugin(db: Session, payload: models.ActivePlugin):
	db_model = models.ActivePlugin(**payload.dict())
	db.add(db_model)
	db.commit()
	db.refresh(db_model)
	return db_model


def bulk_insert_active_plugins(db: Session, payload: list[str]):
	# delete all records, re-added active plugins
	db.query(models.ActivePlugin).delete()

	for name in payload:
		db.add(models.ActivePlugin(name=name))

	db.commit()


def get_active_plugin_by_id(db: Session, id: str) -> models.ActivePlugin:
	statement = select(models.ActivePlugin)
	statement = statement.where(models.ActivePlugin.id == id)
	results = db.exec(statement)
	return results.first()


def delete_active_plugin(db: Session, id: str):
	db_model = get_active_plugin_by_id(db, id)
	if db_model is None:
		raise ValueError('Active plugin not exists')

	db.delete(db_model)
	db.commit()
