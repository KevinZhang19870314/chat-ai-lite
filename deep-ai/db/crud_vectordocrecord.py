import uuid

from sqlalchemy import distinct, func
from sqlmodel import col, Session, select, delete

from db import models


def get_vector_doc_record_with_page(db: Session, knowledge_base_id: str, limit: int = 10, page: int = 1, search: str = ""):
	# Get total count
	count_stat = select(func.count(distinct(models.VectorDocRecord.filename))).where(models.VectorDocRecord.knowledge_base_id == knowledge_base_id)
	if search:
		count_stat = count_stat.where(col(models.VectorDocRecord.filename).contains(search))
	results = db.exec(count_stat)
	total_count = results.first()

	statement = select(models.VectorDocRecord.filename).distinct(models.VectorDocRecord.filename).where(models.VectorDocRecord.knowledge_base_id == knowledge_base_id)
	# Add search filter if provided
	if search:
		statement = statement.where(col(models.VectorDocRecord.filename).contains(search))

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


def get_vector_doc_record_by_filename(db: Session, knowledge_base_id: str, filename: str):
	statement = select(models.VectorDocRecord)\
		.where(models.VectorDocRecord.knowledge_base_id == knowledge_base_id, models.VectorDocRecord.filename == filename)

	results = db.exec(statement)
	records = results.fetchall()

	return records


def check_vector_doc_record_exists(db: Session, knowledge_base_id: str, filename: str):
	statement = select(models.VectorDocRecord)\
		.where(models.VectorDocRecord.knowledge_base_id == knowledge_base_id, models.VectorDocRecord.filename == filename)
	results = db.exec(statement)
	return results.first()


def get_vector_doc_record_by_id(db: Session, id: str) -> models.VectorDocRecord:
	statement = select(models.VectorDocRecord)
	statement = statement.where(models.VectorDocRecord.id == id)
	results = db.exec(statement)
	return results.first()


def create_vector_doc_record(db: Session, payload: models.VectorDocRecord):
	db_model = models.VectorDocRecord(**payload.dict())
	db.add(db_model)
	db.commit()
	db.refresh(db_model)
	return db_model


def bulk_insert_vector_doc_records(db: Session, payload: list[models.VectorDocRecord]):
	db_records = []
	for prompt in payload:
		db_records.append(models.VectorDocRecord(**prompt.dict()))
	db.add_all(db_records)
	db.commit()


def delete_vector_doc_record(db: Session, id: str):
	db_model = get_vector_doc_record_by_id(db, id)
	if db_model is None:
		raise ValueError('Vector Doc Record not exists')

	db.delete(db_model)
	db.commit()


def delete_vector_doc_record_by_filename(db: Session, knowledge_base_id: str, filename: str):
	statement = delete(models.VectorDocRecord)\
		.where(models.VectorDocRecord.knowledge_base_id == knowledge_base_id, models.VectorDocRecord.filename == filename)

	db.execute(statement)
	db.commit()


def delete_vector_doc_record_by_knowledge_base_id(db: Session, knowledge_base_id: str):
	statement = delete(models.VectorDocRecord).where(models.VectorDocRecord.knowledge_base_id == knowledge_base_id)

	db.execute(statement)
	db.commit()
