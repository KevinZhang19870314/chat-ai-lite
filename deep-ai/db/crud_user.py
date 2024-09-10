import os
import uuid

import redis
from sqlalchemy import func, asc
from sqlmodel import col, select, Session

from db import models
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')


redis_client = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=0, password=REDIS_PASSWORD)


def get_users_with_admin_permission(db: Session, limit: int = 10, page: int = 1, search: str = "", type: str = ""):
	# Get total count
	count_stat = select(func.count(models.User.id))
	if search:
		count_stat = count_stat.where(col(models.User.email).contains(search))

	if type:
		count_stat = count_stat.where(models.User.type == type)

	results = db.exec(count_stat)
	total_count = results.first()

	# query records
	statement = select(models.User)

	statement = statement.where(col(models.User.type).in_(["normal", "premium", "admin"]))

	# Add search filter if provided
	if search:
		statement = statement.where(col(models.User.email).contains(search))

	if type:
		statement = statement.where(models.User.type == type)

	statement = statement.order_by(asc(models.User.email))
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


def get_users_with_super_admin_permission(db: Session, limit: int = 10, page: int = 1, search: str = "", type: str = ""):
	# Get total count
	count_stat = select(func.count(models.User.id))
	if search:
		count_stat = count_stat.where(col(models.User.email).contains(search))

	if type:
		count_stat = count_stat.where(models.User.type == type)

	results = db.exec(count_stat)
	total_count = results.first()

	# query records
	statement = select(models.User)

	statement = statement.where(col(models.User.type).in_(["normal", "premium", "admin", "super_admin"]))

	# Add search filter if provided
	if search:
		statement = statement.where(col(models.User.email).contains(search))

	if type:
		statement = statement.where(models.User.type == type)

	statement = statement.order_by(asc(models.User.email))
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


def create_user(db: Session, payload: models.User):
	db_user = models.User(**payload.dict())
	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user


def create_super_admin_if_not_exists(db: Session):
	email = 'admin@chat-ai-lite.com'
	super_admin = get_user_by_email(db, email)

	if super_admin is not None:
		return super_admin

	db_user = models.User(
		id=str(uuid.uuid4()),
		email=email,
		nickname='超级管理员',
		avatar='https://cdn-icons-png.flaticon.com/256/4228/4228678.png',
		description='风一样的男子！！！',
		total_requests=0,
		used_requests=0,
		total_image_requests=10,
		used_image_requests=0,
		meta=None,
		is_feishu_user=False,
		is_github_user=False,
		type='super_admin',
		model='gpt-3.5-turbo',
		password='$2b$10$cfo5aBv/R49e.P89yfQdBuSaBFjZchX6YZrUAa0D2ywUSdbRMq4QW',
		token=None,
	)
	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user


def get_user_by_email(db: Session, email: str) -> models.User:
	return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, id: str) -> models.User:
	return db.query(models.User).filter(models.User.id == id).first()


def get_user_by_email_and_merchant_order_id(db: Session, email: str, merchant_order_id: str) -> models.User:
	return db.query(models.User) \
		.filter(models.User.email == email, models.User.merchant_order_id == merchant_order_id) \
		.first()


def consume_once(db: Session, email: str):
	"""聊天一次，used_requests加1"""
	user = get_user_by_email(db, email)
	if not user:
		raise ValueError('用户不存在 | User not found')

	user.used_requests += 1
	user_json = user.json()
	db.commit()

	redis_client.set(email, user_json, ex=3600)


def consume_once_image(db: Session, email: str):
	"""文生图一次，used_image_requests加1"""
	user = get_user_by_email(db, email)
	if not user:
		raise ValueError('用户不存在 | User not found')

	user.used_image_requests += 1
	user_json = user.json()
	db.commit()

	redis_client.set(email, user_json, ex=3600)


def append_total_image_requests(db: Session, email: str, append: int = 1):
	"""增加文生图次数，used_image_requests + append"""
	user = get_user_by_email(db, email)
	if not user:
		raise ValueError('用户不存在 | User not found')

	user.total_image_requests += append
	user_json = user.json()
	db.commit()

	redis_client.set(email, user_json, ex=3600)


def update_user(db: Session, user: models.User, fields: dict):
	for field_name, new_value in fields.items():
		setattr(user, field_name, new_value)

	user_json = user.json()
	db.commit()
	db.refresh(user)

	redis_client.set(user.email, user_json, ex=3600)
	return user


def upgrade_to_premium(db: Session, id: str):
	user = get_user_by_id(db, id)
	user.type = 'premium'
	user.total_image_requests += 10
	db.commit()
	db.refresh(user)

	redis_client.set(user.email, user.json(), ex=3600)
	return user


def delete_user_by_email(db: Session, email: str) -> None:
	query = db.query(models.User).where(models.User.email == email)
	query.delete(synchronize_session=False)
	db.commit()

	redis_client.delete(id)


def delete_user_by_id(db: Session, id: str) -> None:
	query = db.query(models.User).where(models.User.id == id)
	query.delete(synchronize_session=False)
	db.commit()

	redis_client.delete(id)
